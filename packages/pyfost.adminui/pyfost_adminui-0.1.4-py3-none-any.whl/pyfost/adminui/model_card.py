from __future__ import annotations

from typing import TYPE_CHECKING

from nicegui import ui
from pydantic import BaseModel

if TYPE_CHECKING:
    from .admin import Admin


def card_edit_button(on_click, **actions: callable):
    fab = ui.element("q-fab")
    fab.props("icon=menu flat fab-mini direction=left color=accent")
    fab.on("click", on_click)
    with fab:
        for action_icon, action in actions.items():
            ui.element("q-fab-action").props(f"icon={action_icon} color=accent").on(
                "click", action
            )


def model_card(
    model: BaseModel, admin: Admin, editable: bool = False, with_menu: bool = True
):
    def toggle_edit():
        ui.notify("toggle")

    with ui.card() as card:
        with ui.row(align_items="center", wrap=False).classes("w-full"):
            ui.label(model.__class__.__name__).classes("text-bold")
            if with_menu:
                ui.space()
                card_edit_button(toggle_edit, edit=toggle_edit, save=toggle_edit)
        with ui.grid(columns="auto auto"):
            model_renderer = admin.get_model_view_for(model).model_renderer
            pk_name = model_renderer.pk_name
            for field_name, field in type(model).model_fields.items():
                if field_name == pk_name:
                    continue
                value = getattr(model, field_name)
                renderer = model_renderer.get_field_renderer(
                    admin, model, field, value, editable
                )
                if renderer is None:
                    ui.label("⚠️ NO RENDERER FOUND ⚠️").classes("text-red")
                else:
                    renderer(admin, model, field_name, value, editable)


def model_dialog(model_instance: BaseModel, admin: Admin, editable: bool):
    """
    Creates a NiceGUI form to edit the given model instance inside a dialog.

    Args:
        model_instance: The Pydantic model instance to edit.
        on_submit: A function to call when the form is submitted, passing the updated model.
    """
    with ui.dialog() as dialog:
        with ui.card() as form:
            model_card(model_instance, admin, editable)
    return dialog
