"""
This example shows how to use adminui to build a standalone web app.
"""

import datetime

from nicegui import ui
from pydantic import BaseModel, Field

from pyfost.adminui import Admin
from pyfost.adminui import ModelRenderer

from fastapi import FastAPI

import random


#
# --- MODELS ---
#


class Position(BaseModel):
    name: str
    x: float = 0
    y: float = 0


class Tag(BaseModel):
    name: str
    description: str = ""
    color: str | None = None


class MyModel(BaseModel):
    name: str
    description: str
    position: Position = Field(default_factory=Position)
    tags: list[Tag] = Field(default_factory=[])


class Project(BaseModel):
    name: str
    start: datetime.date | None = None
    end: datetime.date | None = None
    tags: list[Tag]


#
# --- RENDERERS
#


class MyModelRenderer(ModelRenderer):

    @classmethod
    def cell_position(self, model, admin):
        return f"{int(model.position.x)}, {int(model.position.y)}"

    @classmethod
    def cell_tags(self, model, admin):
        return ", ".join([t.name for t in model.tags])

    @classmethod
    def render_position(cls, model, admin):
        prefix = admin.prefix
        pos = model.position
        ui.button(
            f"{pos.x},{pos.y}",
            on_click=lambda p=pos: ui.navigate.to(
                f"{prefix}/{p.__class__.__name__}/{p.name}"
            ),
        ).props("flat")

    @classmethod
    def render_tags(cls, model, admin):
        prefix = admin.prefix
        with ui.row():
            for t in model.tags:
                ui.button(
                    t.name,
                    on_click=lambda t=t: ui.navigate.to(
                        f"{prefix}/{t.__class__.__name__}/{t.name}"
                    ),
                ).props("flat")


class ProjectRenderer(ModelRenderer):

    @classmethod
    def cell_tags(self, model, admin):
        return ", ".join([t.name for t in model.tags])

    @classmethod
    def render_tags(cls, model, admin):
        with ui.row():
            for t in model.tags:
                ui.button(
                    t.name,
                    on_click=lambda t=t: ui.navigate.to(
                        f"{admin.prefix}/{t.__class__.__name__}/{t.name}"
                    ),
                ).props("flat")


#
# --- COLLECTIONS ---
#

positions = []
for x in range(0, 100, 3):
    for y in range(0, 100, 3):
        positions.append(Position(name=f"P({x:02}{y:02})", x=x, y=y))


def get_positions():
    return positions


tags = []
for i in range(10):
    tags.append(Tag(name=f"T{i}", description=f"Description of tag #{i}"))


def get_tags():
    return tags


projects = []
for x in range(0, 100, 3):
    projects.append(
        Project(
            name=f"Project{x}",
            tags=random.sample(tags, k=3),
        )
    )


def get_projects():
    return projects


my_models = []
available_positions = list(positions)
random.shuffle(available_positions)
for i in range(len(available_positions)):
    my_models.append(
        MyModel(
            name=f"Model {i:03}",
            description=f"Description {i}",
            position=available_positions.pop(),
            tags=random.sample(tags, k=3),
        )
    )


# the getter can be async
async def get_my_models():
    return my_models


admin = Admin("/admin", default_model_renderer=ModelRenderer(pk_name="name"))
admin.title = "Admin Simple Example"
admin.add_view(MyModel, get_my_models, renderer=MyModelRenderer(pk_name="name"))
admin.add_view(Tag, get_tags)
admin.add_view(Position, get_positions)
admin.add_view(Project, get_projects, renderer=ProjectRenderer(pk_name="name"))


# You can still add all the pages you want (but not under /admin)
@ui.page("/")
def app():
    ui.add_head_html(
        '<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />'
    )

    with ui.header(elevated=True):
        with ui.row(align_items="center"):
            ui.markdown("### pyfost.adminui.examples.simple")
            with ui.row():
                with ui.link(
                    target="https://github.com/fost-studio/pyfost.adminui",
                    new_tab=True,
                ):
                    ui.icon("eva-github", size="md", color="stone-700").classes("wh-20")
                with ui.link(
                    target="https://pypi.org/project/pyfost.adminui", new_tab=True
                ):
                    ui.icon("sym_o_deployed_code_update", size="md", color="stone-700")

    with ui.column().classes("w-full"):
        with ui.row().classes("w-full justify-center"):
            ui.markdown("# ✨ Welcome✨")
        with ui.row().classes("w-full justify-center"):
            with ui.link(target="admin"):
                ui.button("Show me the Admin !")

    with ui.footer(elevated=True):
        ui.markdown("Made with ♥️ by Dee and AI.")


app = FastAPI()
admin.add_to(app)
ui.run_with(app)


if __name__ == "__main__":
    if 0:
        ui.run(port=8001)
    else:
        import uvicorn

        uvicorn.run(
            "pyfost.adminui.examples.simple:app", host="0.0.0.0", port=8003, reload=True
        )
