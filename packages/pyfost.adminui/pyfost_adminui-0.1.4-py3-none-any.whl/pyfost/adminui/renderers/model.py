from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nicegui import ui

from .field import get_default_renderers
from .column import get_default_column_renderers

if TYPE_CHECKING:
    from ..admin import Admin


class ModelRenderer:
    def __init__(self, pk_name: str = "id"):
        self._model_pk_name = pk_name
        self._hide_pk_by_default = pk_name == "id"

        self._column_renderers = get_default_column_renderers()
        self._field_renderers = get_default_renderers()

    @property
    def hide_pk_by_default(self) -> bool:
        return self._hide_pk_by_default

    @property
    def pk_name(self) -> str:
        return self._model_pk_name

    def get_pk(self, item) -> Any:
        pk = getattr(item, self.pk_name)
        return pk

    def get_field_renderer(self, admin, model, field, value, editable: bool):
        for field_renderer in self._field_renderers:
            if field_renderer.handles(admin, model, field, value, editable):
                return field_renderer.render
        return None

    def get_column_renderer(self, admin, ModelType, column: dict[str, str]):
        for ColumnRendererType in self._column_renderers:
            if ColumnRendererType.handles(admin, ModelType, column):
                return ColumnRendererType(admin, ModelType, column)

    def cell(self, item, field_name, admin):
        """
        Return the content to use in a table cell for the given field.
        If a method `cell_<field_name>()` is defined on the model, it will
        be used to generate the content by calling it with args: (model, admin)
        """
        try:
            cell = getattr(self, f"cell_{field_name}")
        except AttributeError:
            return str(getattr(item, field_name, f"field not found:{field_name!r}"))
        else:
            return cell(item, admin)

    def display(self, item, field_name, admin):
        """
        Return a text representation of the value in field_name.
        If a method `display_<field_name>()` is defined on the model, it will
        be used to generate the text by calling it with args: (model, admin)
        """
        try:
            display = getattr(self, f"display_{field_name}")
        except AttributeError:
            return getattr(item, field_name)
        else:
            return display(item, admin)

    def render(self, item, field_name, admin: Admin):
        """
        Renders the form ui for the given field.
        If a method `render_<field_name>()` is defined on the model, it will
        be used to render the field ui by calling it with args: (model, admin)

        Default is to render a chip with the display value
        """
        try:
            renderer = getattr(self, f"render_{field_name}")
        except AttributeError:
            admin = admin
            prefix = admin.prefix
            model_type_name = item.__class__.__name__
            model_view = admin.get_model_view_for(item)
            pk = self.get_pk(item)
            # pk = getattr(self, model_view.model_pk_name)
            ui.button(
                self.display(item, field_name, admin),
                on_click=lambda p=prefix, m=model_type_name, pk=pk: ui.navigate.to(
                    f"{p}/{m}/{pk}"
                ),
            ).props("flat")
        else:
            return renderer(item, admin)

    def render_editor(self, item, field_name, admin: Admin):
        value = repr(getattr(item, field_name))
        with ui.chip(f"{field_name}"):
            ui.tooltip(value)
