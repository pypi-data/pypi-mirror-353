from __future__ import annotations

from typing import TYPE_CHECKING
from enum import Enum

from fastapi import APIRouter, FastAPI
from nicegui import ui

from .model_view import ModelView, ModelType
from .model_card import model_card

from .renderers.model import ModelRenderer


class Admin:
    def __init__(
        self,
        prefix: str = "/admin",
        # tags: list[str | Enum] | None = None,
        default_model_renderer: ModelRenderer | None = None,
    ):
        print("------------------ NEW ADMIN", prefix, self)
        self.api_router = APIRouter(
            prefix=prefix,
        )
        self.title = "Admin"
        self._views = {}
        self._default_model_renderer = default_model_renderer or ModelRenderer()

        self._parent_router: APIRouter = None

        self._show_left_drawer = True
        self._header_renderer = None
        self._index_renderer = None

    @property
    def prefix(self) -> str:
        return self._parent_router.prefix + self.api_router.prefix

    def set_header(self, header_renderer_coro):
        self._header_renderer = header_renderer_coro

    @property
    def show_left_drawer(self) -> bool:
        return self._show_left_drawer

    @show_left_drawer.setter
    def show_left_drawer(self, b: bool):
        self._show_left_drawer = b

    def set_index(self, index_renderer_coro):
        self._index_renderer = index_renderer_coro

    def to_plural(self, name: str):
        if name.endswith("y"):
            name = name[:-1] + "ies"
        else:
            name = name + "s"
        return name

    def add_view(self, ModelType, getter, renderer: ModelRenderer | None = None):
        view = ModelView(
            self, ModelType, getter, renderer or self._default_model_renderer
        )
        self._views[ModelType] = view

    def has_view_for(self, ModelType: ModelType) -> bool:
        """
        Returns True if the given type has a corresponding view.
        """
        return ModelType in self._views

    def get_model_view_for(self, model) -> ModelView:
        return self._views[model.__class__]

    def add_to_router(self, app_or_router: APIRouter):
        self._parent_router = app_or_router

        @ui.page("", api_router=self.api_router, title=self.title)
        async def admin() -> None:
            await self.render_header(None)
            self.render_left_drawer(None)
            await self.render_index()

        for ModelType, view in self._views.items():

            @ui.page(
                f"/{view.model_type_name}",
                api_router=self.api_router,
                title=f"{self.title}:{view.model_type_name}",
            )
            async def model_page(view=view):
                await self.render_header(self.to_plural(view.model_type_name))
                self.render_left_drawer(self.to_plural(view.model_type_name))

                @ui.refreshable
                async def main_area():
                    # ui.label(f"{view!r} -> {view.model_type.__name__}")
                    await view.render()

                await main_area()

            @ui.page(f"/{view.model_type_name}/{{ID}}", api_router=self.api_router)
            async def item_detail(ID, view=view) -> None:
                try:
                    ID = int(ID)
                except ValueError:
                    pass

                await self.render_header(f"{view.model_type_name} ({ID})")
                self.render_left_drawer(f"{view.model_type_name} ({ID})")

                @ui.refreshable
                def main_area():
                    ui.button("Back", on_click=ui.navigate.back)
                    ui.label(f"{view!r} -> {view.model_type.__name__}")
                    model = view.get_by_pk(ID)
                    if model is None:
                        ui.markdown(
                            "# 😭\n"
                            f"Could not find {view.model_type.__name__} model with primary key {ID!r}.\n\n"
                            f"Available ids are: \n\n - {'\n - '.join(view._by_pk.keys())}"
                        )
                    else:
                        model_card(
                            view.get_by_pk(ID), self, editable=True, with_menu=True
                        )

                main_area()

        app_or_router.include_router(self.api_router)

    async def render_header(self, model_type_name: str | None):
        if self._header_renderer is not None:
            await self._header_renderer(model_type_name)
        else:
            with ui.header(elevated=True):
                with ui.row(align_items="center"):
                    with ui.link(target=self._parent_router.prefix + "/"):
                        ui.button(icon="sym_o_arrow_circle_left")
                    ui.markdown(f"##{self.title}")

    async def render_index(self):
        if self._index_renderer is not None:
            await self._index_renderer()
        else:
            ui.markdown(f"# ✨ Welcome to {self.prefix} ✨")

    def render_left_drawer(self, model_type_name: str | None):
        if not self._show_left_drawer:
            return
        prefix = self.prefix
        with ui.left_drawer(value=True).classes("bg-stone-600"):
            for view in self._views.values():
                name = view.model_type_name
                name = self.to_plural(name)
                ui.button(
                    name,
                    on_click=lambda n=view.model_type_name: ui.navigate.to(
                        f"{prefix}/{n}"
                    ),
                ).props(model_type_name != view.model_type_name and "flat" or "")

    async def render_view_selector(
        self, current: str = "Select...", index_title: str | None = None
    ):
        with ui.dropdown_button(text=current):
            with ui.column().classes("gap-0"):
                if index_title is not None:
                    ui.button(
                        index_title,
                        on_click=lambda: ui.navigate.to(f"{self.prefix}"),
                    ).props("flat")
                    ui.separator()
                for view in self._views.values():
                    name = view.model_type_name
                    name = self.to_plural(name)
                    ui.button(
                        name,
                        on_click=lambda n=view.model_type_name: ui.navigate.to(
                            f"{self.prefix}/{n}"
                        ),
                    ).props("flat")
