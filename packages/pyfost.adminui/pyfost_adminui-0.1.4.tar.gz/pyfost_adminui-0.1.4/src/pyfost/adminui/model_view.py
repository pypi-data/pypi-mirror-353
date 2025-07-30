from __future__ import annotations

from typing import Type, TypeVar, get_args, Literal, TYPE_CHECKING

import inspect

from nicegui import ui

from pydantic import BaseModel
from .model_card import model_dialog

from .renderers.column import ColumnRenderer
from .renderers.model import ModelRenderer

ModelType = TypeVar("ModelType", bound=BaseModel)


class ModelView:

    def __init__(self, admin, model_type: ModelType, getter, renderer: ModelRenderer):
        # print(
        #     "------------------------------------------------- NEW MODEL VIEW",
        #     model_type,
        # )
        super().__init__()
        self.admin = admin

        self.columns_align = "left"
        self.columns_headerClasses = "uppercase text-primary"
        self.columns_classes = ""

        self.model_type = model_type
        self.model_type_name = model_type.__name__
        self.model_renderer = renderer

        # print("===>", self._card_prefix)

        self._items: list[ModelType] = None
        self._rows = []
        self._by_pk = {}
        self.getter = getter
        # self.set_items(getter()) <- cant do that, need async and maybe lazy too.

        self._table = None
        self._column_checkboxes = {}

        self._column_renderers: list[ColumnRenderer] = []
        self.columns: list[dict] = self._get_columns()
        self.items: list[ModelType] = []

    @property
    def _card_prefix(self):
        return f"{self.admin.prefix}/{self.model_type_name}"

    def _get_columns(self) -> list[dict]:
        action_column = {
            "name": "actions",
            "label": "Actions",
            "field": "action",
            "sortable": False,
            "classes": self.columns_classes,
            "headerClasses": self.columns_headerClasses,
            "align": self.columns_align,
        }
        columns = [action_column]
        for field_name, field in self.model_type.model_fields.items():
            c = {
                "name": field_name,
                "label": field_name,
                "field": field_name,
                # "required": True,
                "sortable": True,
                "classes": self.columns_classes,
                "headerClasses": self.columns_headerClasses,
                "align": self.columns_align,
            }

            if (
                self.model_renderer.hide_pk_by_default
                and field_name == self.model_renderer.pk_name
            ):
                c["classes"] += " hidden"
                c["headerClasses"] += " hidden"

            columns.append(c)

        # build column renderers
        self._column_renderers.clear()
        for column in columns:
            column_renderer = self.model_renderer.get_column_renderer(
                self.admin, self.model_type, column
            )
            if column_renderer is not None:
                # print("+++", column_renderer)
                self._column_renderers.append(column_renderer)
        # print("------------------->", self.model_type_name, self._column_renderers)
        return columns

    def get_by_pk(self, pk):
        return self._by_pk.get(pk)

    def set_items(self, items: list[ModelType]):
        self._items = items
        self._rows = []
        self._by_pk.clear()
        for item in self._items:
            # the pk will be sent to js, so we need to coerce to something
            # we're using str(), but I guess we need'll to handle thing when
            # the pk is an int :[
            pk = str(self.model_renderer.get_pk(item))
            r = item.model_dump()
            for k, v in r.items():
                r[k] = self.model_renderer.cell(item, k, self.admin)
            r["__pk__"] = pk
            self._rows.append(r)
            self._by_pk[pk] = item

    async def refresh_items(self):
        if inspect.iscoroutinefunction(self.getter):
            items = await self.getter()
        else:
            items = self.getter()
        self.set_items(items)
        if self._table is not None:
            self._table.rows = self._rows

    def set_view_mode(self, mode: Literal["grid", "table"]) -> None:
        if self._table is None:
            return
        grid = mode == "grid"
        self._table.props("grid" if grid else "grid=false")
        # Hide column switch from menu when in grid mode:
        for cb in self._column_checkboxes.values():
            cb.classes(add=grid and "hidden", remove=not grid and "hidden")

    def toggle_column(self, column: dict, visible: bool) -> None:
        column["classes"] = (
            self.columns_classes if visible else self.columns_classes + " hidden"
        )
        column["headerClasses"] = (
            self.columns_headerClasses
            if visible
            else self.columns_headerClasses + " hidden"
        )
        self._table.update()

    async def render(self):
        if self._items is None:
            # self._items = []
            await self.refresh_items()

        with ui.element().classes("w-full bg-stone-100 p-5"):
            with ui.row(align_items="center").classes("w-full"):
                name = self.model_type_name
                if name.endswith("y"):
                    name = name[:-1] + "ies"
                else:
                    name = name + "s"
                ui.label(name).classes("text-h4 my-5")
                ui.space()
                ui.button(f"New {self.model_type_name}", icon="add").props("no-caps")
                ui.button(icon="refresh", on_click=self.refresh_items)

            with (
                ui.table(
                    columns=self.columns,
                    rows=self._rows,
                    row_key="__pk__",
                    pagination=8,
                    selection="multiple",
                    on_select=self._on_select_row,
                )
                .classes("w-full")
                .style("max-height: 700px")
                .props(f"virtual-scroll")
            ) as self._table:

                # print(
                #     "------------> ??????", self.model_type_name, self._column_renderers
                # )
                for column_renderer in self._column_renderers:
                    column_renderer.apply(self._table)

                # Make the "name" column clickable:
                # FIXME: this should be configurable:
                self._table.add_slot(
                    "body-cell-name",
                    f"""
                    <q-td :props="props">
                        <q-chip esize="xs">
                        <a :href="'{self._card_prefix}/'+props.value">{{{{ props.value }}}}</a>
                        </q-chip>
                        <q-btn flat dense round icon="visibility" color=accent @click="$parent.$parent.$emit('show', props.row)" />
                """,
                )

                # Define slots for actions (buttons in the action column)
                # NB: we use $parent.$parent because https://github.com/zauberzeug/nicegui/discussions/3405#discussioncomment-10267129
                self._table.add_slot(
                    "body-cell-actions",
                    """
                    <q-td :props="props">
                        <xxx-q-btn flat dense round icon="visibility" color=accent @click="$parent.$parent.$emit('show', props.row)" />
                        <q-btn flat dense round icon="edit" color=accent @click="$parent.$parent.$emit('edit', props.row)" />
                        <q-btn flat dense round icon="delete" color="red-7" @click="$parent.$parent.$emit('delete', props.row)"/>
                    </q-td>
                """,
                )
                self._table.on("show", lambda e: self._on_show(e.args))
                self._table.on("edit", lambda e: self._on_edit(e.args))
                self._table.on("delete", lambda e: self._on_delete(e.args))

            with self._table.add_slot("top") as table_top:
                with ui.row(align_items="center") as tools:
                    filter = (
                        ui.input("Search Item")
                        .props("clearable")
                        .bind_value(self._table, "filter")
                    )
                    with filter.add_slot("prepend"):
                        ui.icon("search").props("flat")
                ui.space()
                with ui.button(icon="table_view"):
                    with ui.menu(), ui.column().classes("gap-0 p-2"):
                        ui.toggle(
                            ["Table", "Grid"],
                            value="Table",
                            on_change=lambda e: self.set_view_mode(e.value.lower()),
                        )
                        ui.separator()
                        for column in self.columns:
                            s = ui.switch(
                                column["label"],
                                value=" hidden" not in column["headerClasses"],
                                on_change=lambda e, c=column: self.toggle_column(
                                    c, e.value
                                ),
                            )
                            self._column_checkboxes[column["field"]] = s

            with self._table.add_slot("header-selection"):
                self._multi_select_cb = ui.checkbox(
                    on_change=self._on_multi_select_change
                )
                with ui.button(icon="settings").props(
                    "xflat"
                ) as self._selected_actions_button:
                    with ui.menu().classes("gap-0 p-2"):
                        # TODO: list of actions should be configured on the view / model type
                        for name in ["Do Something", "Do Something else..."]:
                            ui.menu_item(
                                name, on_click=lambda n=name: self._on_action(n)
                            )
                        # ui.menu_item("Do Something Else...")
                    self._selected_actions_button.set_visibility(False)

            if 0:
                # these may be usefull later:
                self._table.add_slot(
                    "item",
                    r"""
                        <q-card flat bordered :props="props" class="m-1">
                            <q-card-section class="text-center">
                                <strong>{{ props.row.name }}</strong>
                            </q-card-section>
                            <q-separator />
                            <q-card-section class="text-center">
                                <div>{{ props.row.age }} years</div>
                            </q-card-section>
                        </q-card>
                    """,
                )

                with self._table.add_slot("top-row"):
                    ui.label("this is the top row")
                with self._table.add_slot("bottom-row"):
                    ui.label("this is the bottom row")

    def _on_multi_select_change(self, e):
        checked = e.value
        actions_enabled = True
        if checked is True:
            self._table.selected = self._table.rows
        elif checked is False:
            self._table.selected = []
            actions_enabled = False

        self._selected_actions_button.set_visibility(actions_enabled)

    def _on_select_row(self, e):
        if e.selection:
            # FIXME: this will be slow on big tables !
            # but we need it bc table.selected is ordered
            selected_pk = set([i["__pk__"] for i in e.selection])
            all_pk = set([i["__pk__"] for i in self._table.rows])
            if selected_pk == all_pk:
                self._multi_select_cb.set_value(True)
            else:
                self._multi_select_cb.set_value(None)
        else:
            self._multi_select_cb.set_value(False)

    def _on_show(self, row):
        model = self._by_pk[row["__pk__"]]
        dialog = model_dialog(model, self.admin, editable=False)
        dialog.open()

    def _on_edit(self, row):
        print("!!!!!!!!!!!!!!!!!!!!!!!", self._by_pk)
        model = self._by_pk[row["__pk__"]]
        dialog = model_dialog(model, self.admin, editable=True)
        dialog.open()

    def _on_delete(self, row):
        model = self._by_pk[row["__pk__"]]
        print("DELETE NOT IMPLEMENTED", model)

    def _on_action(self, action_name):
        print(action_name)
