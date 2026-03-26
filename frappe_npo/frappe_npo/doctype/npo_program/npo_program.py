# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.query_builder import DocType


class NPOProgram(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        company: DF.Link | None
        decription: DF.SmallText | None
        expected_end_date: DF.Date | None
        expected_start_date: DF.Date | None
        image: DF.AttachImage | None
        program_manager: DF.Link | None
        program_name: DF.Data
        program_type: DF.Link | None
        status: DF.Literal["Draft", "Active", "On Hold", "Completed", "Cancelled"]
    # end: auto-generated types

    pass

    def validate(self): ...

    @frappe.whitelist()
    def fetch_projects(self) -> list[dict]:
        rows = self.get_program_project_task_rows()
        grouped_projects = self.map_projects(rows)

        return grouped_projects

    def map_projects(self, projects: list[dict]) -> list[dict]:
        grouped_projects: dict[str, dict] = {}

        for row in projects:
            project_id = row.project

            if project_id not in grouped_projects:
                grouped_projects[project_id] = {
                    "project": row.project,
                    "project_name": row.project_name,
                    "tasks": [],
                }

            if row.task:
                grouped_projects[project_id]["tasks"].append(
                    {
                        "task": row.task,
                        "task_name": row.task_name,
                    }
                )

        return list(grouped_projects.values())

    def get_program_project_task_rows(self) -> list[dict]:
        project = DocType("Project")
        task = DocType("Task")

        query = (
            frappe.qb.from_(project)
            .left_join(task)
            .on(project.name == task.project)
            .select(
                project.name.as_("project"),
                project.project_name.as_("project_name"),
                task.name.as_("task"),
                task.subject.as_("task_name"),
            )
            .where(project.program == self.name)
        )

        return query.run(as_dict=True)
