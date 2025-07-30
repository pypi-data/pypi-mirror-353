from __future__ import annotations


from nicegui import ui

from pyfost.adminui import Admin, ModelRenderer

from ...api import FloorsAPI, models
from ....components.header import header

# class FacilityRenderer(ModelRenderer):
#     @classmethod
#     def cell_email(self, model, admin):
#         return str(model.email)

#     @classmethod
#     def cell_projects(self, model, admin):
#         return ",".join([i.code for i in model.projects])

#     @classmethod
#     def render_login(cls, model, admin):
#         ui.button(model.login)
#         # with ui.row():
#         #     for t in model.tags:
#         #         ui.button(
#         #             t.name,
#         #             on_click=lambda t=t: ui.navigate.to(
#         #                 f"{admin.prefix}/{t.__class__.__name__}/{t.name}"
#         #             ),
#         #         ).props("flat")


# class TaskRenderer(ModelRenderer):
#     @classmethod
#     def cell_project(self, model, admin):
#         return model.project.title

#     @classmethod
#     def cell_status(self, model, admin):
#         return model.status.value

#     @classmethod
#     def cell_assignee(self, model, admin):
#         assignee = model.assignee
#         if assignee is None:
#             return "<FREE>"
#         return assignee.login


def mount_admin(parent_router, api_host: str, api_port: int):
    floors_api = FloorsAPI(host=api_host, port=api_port)

    async def get_facilities() -> list[models.Facility]:
        return await floors_api.get_facilities()

    async def get_floors() -> list[models.Floor]:
        return await floors_api.get_floors()

    async def get_seats() -> list[models.Seat]:
        return await floors_api.get_seats()

    async def get_resources() -> list[models.Resource]:
        return await floors_api.get_resources()

    async def get_assignations() -> list[models.Assignation]:
        return await floors_api.get_assignations()

    async def get_tasks() -> list[models.Task]:
        return await floors_api.get_tasks()

    async def header_title(model_type_name: str = "???"):
        with ui.row():
            ui.label("Floor Plans Admin").classes("text-h4 text-weight-bolder")
            await admin.render_view_selector(
                model_type_name or "Home", index_title="Home"
            )

    async def admin_header(model_type_name):
        await header(
            header_title,  # "Floor Plans Admin",
            back_target=parent_router.prefix + "/",
            back_icon="sym_o_arrow_circle_left",
            model_type_name=model_type_name,
        )

    async def admin_index():
        ui.markdown(
            """
            ## Floor Plan Admin 
            This page will contain helping resource to help you manage your Floor Plans.

            I the meantime, have fun fooling around 😅

            Maybe start by browsing the different pages using the selector at the top? 🤷
            
            And don't forget to BACKUP YOUR DATA!
        """
        )
        with ui.row():
            ui.button("Export DB Data", icon="save")
            ui.button("Import DB Data", icon="upload_file")

    admin = Admin("/admin")
    admin.show_left_drawer = False
    admin.title = "Floor Plans Admin"
    admin.set_header(admin_header)
    admin.set_index(admin_index)

    admin.add_view(models.Facility, get_facilities)
    admin.add_view(models.Floor, get_floors)
    admin.add_view(models.Seat, get_seats)
    admin.add_view(models.Resource, get_resources)
    admin.add_view(models.Assignation, get_assignations)
    admin.add_view(models.Task, get_tasks)
    admin.add_to_router(parent_router)
