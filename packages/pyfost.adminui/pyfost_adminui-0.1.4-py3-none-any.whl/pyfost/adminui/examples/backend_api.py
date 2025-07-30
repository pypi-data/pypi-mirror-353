"""
This example shows how to connect the admin pages to a backend REST api.

(For reference. You would actually need to have the backend running to run this.)
"""

from __future__ import annotations

import os
import enum
from typing import Any
from contextlib import asynccontextmanager

import httpx
from pydantic import BaseModel, Field, UUID4, EmailStr
from fastapi import FastAPI
from nicegui import ui

from pyfost.adminui import Admin, ModelRenderer


#
# --- CLIENT ---
#


# (These would be defined in a external package)
class User(BaseModel):
    id: UUID4
    email: EmailStr
    login: str


class Project(BaseModel):
    id: UUID4
    code: str
    title: str


class TaskStatus(str, enum.Enum):
    NYS = "NYS"
    WIP = "WIP"
    Done = "Done"


class Task(BaseModel):
    id: UUID4
    project: Project
    title: str
    description: str | None = None
    status: TaskStatus = Field(default=TaskStatus.NYS)
    assignee_id: str | None = None
    assignee: User | None = None


class API:
    def __init__(self, api_url: str = "http://127.0.0.1:8002"):
        api_url = api_url if api_url.endswith("/") else api_url + "/"

        self._client = httpx.AsyncClient(base_url=api_url, timeout=2.0)

    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Helper function to make requests and handle basic errors."""
        try:
            response = await self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            if response.status_code == 204:  # No Content
                return None
            return response.json()
        except httpx.HTTPStatusError as e:
            # Try to get detail from response, otherwise use generic message
            detail = (
                e.response.json().get("detail", e.response.text)
                if e.response
                else str(e)
            )
            print(
                f"HTTP Error: {e.response.status_code} - {detail}"
            )  # Log detailed error
            raise Exception(f"API Error ({e.response.status_code}): {detail}") from e
        except httpx.RequestError as e:
            print(f"Request Error: {e}")
            raise Exception(f"Network or connection error: {e}") from e
        except Exception as e:
            print(f"Unexpected Error during API call: {e}")
            raise Exception(
                "An unexpected error occurred while contacting the API."
            ) from e

    async def get_users(self) -> list[User]:
        return [User(**i) for i in await self._request("GET", "users/")]

    async def get_projects(self) -> list[Project]:
        return [Project(**i) for i in await self._request("GET", "projects/")]

    async def get_tasks(self) -> list[Task]:
        return [Task(**i) for i in await self._request("GET", "tasks/")]


#
# --- RENDERERS ---
#


class UserRenderer(ModelRenderer):
    def cell_login(self, item, admin):
        return f"King {item.login}"


#
# --- API and Admin ---
#

api = API()
admin = Admin("/admin")
admin.title = "Admin Example using a API client"


async def get_users() -> list[User]:
    return await api.get_users()


async def get_project() -> list[Project]:
    return await api.get_projects()


async def get_tasks() -> list[Task]:
    return await api.get_tasks()


admin.add_view(User, get_users, renderer=UserRenderer())
admin.add_view(Project, get_project)
admin.add_view(Task, get_tasks)

#
# --- FastAPI app
#


@asynccontextmanager
async def lifespan(app: FastAPI):
    # print(100 * "#")
    yield
    # print(100 * "#")


app = FastAPI(lifespan=lifespan)
admin.add_to(app)
ui.run_with(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "pyfost.adminui.examples.backend_api:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
    )
