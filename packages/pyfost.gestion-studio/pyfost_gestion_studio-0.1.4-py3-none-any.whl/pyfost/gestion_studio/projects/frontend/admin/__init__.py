from __future__ import annotations


from nicegui import ui

from pyfost.adminui import Admin, ModelRenderer

from ...api import ProjectsAPI, models
from ....components.header import header


class UserRenderer(ModelRenderer):
    @classmethod
    def cell_email(self, model, admin):
        return str(model.email)

    @classmethod
    def cell_projects(self, model, admin):
        return ",".join([i.code for i in model.projects])

    @classmethod
    def render_login(cls, model, admin):
        ui.button(model.login)
        # with ui.row():
        #     for t in model.tags:
        #         ui.button(
        #             t.name,
        #             on_click=lambda t=t: ui.navigate.to(
        #                 f"{admin.prefix}/{t.__class__.__name__}/{t.name}"
        #             ),
        #         ).props("flat")


class TaskRenderer(ModelRenderer):
    @classmethod
    def cell_project(self, model, admin):
        return model.project.title

    @classmethod
    def cell_status(self, model, admin):
        return model.status.value

    @classmethod
    def cell_assignee(self, model, admin):
        assignee = model.assignee
        if assignee is None:
            return "<FREE>"
        return assignee.login


def mount_admin(parent_router, api_host: str, api_port: int):
    project_api = ProjectsAPI(host=api_host, port=api_port)

    async def get_users() -> list[models.User]:
        return await project_api.get_users()

    async def get_projects() -> list[models.Project]:
        return await project_api.get_projects()

    async def get_tasks() -> list[models.Task]:
        return await project_api.get_tasks()

    async def admin_header():
        await header(
            "Projects Admin",
            back_target=parent_router.prefix + "/",
            back_icon="sym_o_arrow_circle_left",
        )

    admin = Admin("/admin")
    admin.title = "Projects Admin"
    admin.set_header(admin_header)
    admin.add_view(models.User, get_users, renderer=UserRenderer(pk_name="id"))
    admin.add_view(models.Project, get_projects)
    admin.add_view(models.Task, get_tasks, renderer=TaskRenderer())
    admin.add_to_router(parent_router)
