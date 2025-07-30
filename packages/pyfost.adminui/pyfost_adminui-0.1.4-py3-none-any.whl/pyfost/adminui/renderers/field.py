from __future__ import annotations

from typing import TYPE_CHECKING

from nicegui import ui

from pydantic import BaseModel

SUPPORTED_MODELS = (BaseModel,)

if TYPE_CHECKING:
    from ..admin import Admin


def get_default_renderers():
    # NB: order matters (first one handling it wins)
    return [
        ModelListValueFieldRenderer,
        ModelValueFieldRenderer,
        ValueTypeFieldRenderers,
        DefaultFieldRenderer,
    ]


class FieldRenderer:
    @classmethod
    def handles(cls, admin, model, field, value, editable):
        """
        Return True if this renderer can render `value`.
        """
        return False

    @classmethod
    def render(cls, admin, model, field_name, value, editable: bool):
        raise NotImplementedError()


class DefaultFieldRenderer(FieldRenderer):
    @classmethod
    def handles(cls, admin, model, field, value, editable: bool):
        return True

    @classmethod
    def render(cls, admin, model, field_name, value, editable: bool):
        if not editable:
            ui.label(field_name)
            ui.label(str(value))
        else:
            ui.input(field_name, value=str(value))


class BasicTypeRenderer(FieldRenderer):
    @classmethod
    def handles(cls, admin, model, field, value, editable: bool):
        return True

    @classmethod
    def coerce(self, value):
        return str(value)

    @classmethod
    def render(cls, admin, model, field_name, value, editable: bool):
        if not editable:
            ui.label(field_name)
            ui.label(str(value))
        else:
            ui.input(field_name, value=cls.coerce(value)).classes("col-span-2")


class IntRenderer(BasicTypeRenderer):
    @classmethod
    def coerce(self, value):
        return int(value)


class StrRenderer(BasicTypeRenderer):
    @classmethod
    def coerce(self, value):
        return str(value)


class FloatRenderer(BasicTypeRenderer):
    @classmethod
    def coerce(self, value):
        return float(value)


class ValueTypeFieldRenderers(FieldRenderer):
    TYPE_TO_FIELD = {
        int: IntRenderer,
        str: StrRenderer,
        float: FloatRenderer,
    }

    @classmethod
    def handles(cls, admin: Admin, model, field, value, editable):
        # print("?", type(value), value)
        return type(value) in cls.TYPE_TO_FIELD

    @classmethod
    def render(cls, admin: Admin, model, field_name, value, editable: bool):
        renderer = cls.TYPE_TO_FIELD[type(value)]
        renderer.render(admin, model, field_name, value, editable)


class ModelValueFieldRenderer(FieldRenderer):
    @classmethod
    def handles(cls, admin: Admin, model, field, value, editable):
        return isinstance(value, SUPPORTED_MODELS)

    @classmethod
    def render_label(cls, admin: Admin, model, field_name, value, editable: bool):
        ui.label(f"{field_name}:").classes("text-right")

    @classmethod
    def render_value(cls, admin: Admin, item, field_name, value, editable: bool):
        prefix = admin.prefix
        model_renderer = admin.get_model_view_for(item).model_renderer
        pk = model_renderer.pk_name
        model_type_name = value.__class__.__name__
        if not editable:
            model_renderer.render(item, field_name, admin)
        else:
            model_renderer.render_editor(item, field_name, admin)

    @classmethod
    def render(cls, admin, model, field_name, value, editable: bool):
        cls.render_label(admin, model, field_name, value, editable)
        cls.render_value(admin, model, field_name, value, editable)


class ModelListValueFieldRenderer(FieldRenderer):
    @classmethod
    def handles(cls, admin: Admin, model, field, value, editable):
        if not isinstance(value, list):
            return False

        for item in value:
            if not isinstance(item, SUPPORTED_MODELS):
                # We only handle list where all items are instance of a Model.
                # We would implement another field renderer for not omogenous lists...
                return False
        return True

    @classmethod
    def render(cls, admin: Admin, item, field_name, value, editable: bool):
        if not editable:
            renderer = ModelValueFieldRenderer
            renderer.render_label(admin, item, field_name, value, editable)
            with ui.row():
                for i, item in enumerate(value):
                    model_renderer = admin.get_model_view_for(item).model_renderer
                    pk_field_name = model_renderer.pk_name
                    renderer.render_value(
                        admin,
                        item,
                        field_name=pk_field_name,
                        value=item,
                        editable=editable,
                    )

        else:
            model_renderer = admin.get_model_view_for(item).model_renderer
            model_renderer.render_editor(item, field_name, admin)
