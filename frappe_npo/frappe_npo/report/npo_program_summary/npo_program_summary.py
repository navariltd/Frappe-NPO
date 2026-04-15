# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from dataclasses import dataclass
from typing import Optional
from frappe.query_builder import DocType
from pypika.queries import QueryBuilder
from pypika import Criterion


def execute(filters: dict) -> tuple[list[dict], list[list]]:

    return ProgramSummaryReport(ReportFilters(**filters)).run()


@dataclass
class ReportFilters:
    company: str
    program_name: Optional[str] = None
    program_type: Optional[str] = None
    status: Optional[str] = None
    expected_start_date: Optional[str] = None
    expected_end_date: Optional[str] = None
    program_manager: Optional[str] = None


@dataclass
class ProgramSummaryReport:
    filters: ReportFilters
    program = DocType("NPO Program")
    project = DocType("Project")
    task = DocType("Task")
    budget = DocType("Budget")

    def run(self):
        data = self.get_data(self.filters)
        columns = self.get_columns()
        report_summary = self.get_report_summary(data, self.filters)
        return columns, data, None, None, report_summary

    def get_columns(self) -> list[dict]:

        return [
            {
                "label": _("Program"),
                "fieldname": "program",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": _("Project Name"),
                "fieldname": "project_name",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "label": _("Project ID"),
                "fieldname": "project_id",
                "fieldtype": "Link",
                "options": "Project",
                "width": 200,
            },
            {
                "label": _("Project Type"),
                "fieldname": "project_type",
                "fieldtype": "Data",
            },
            {
                "label": _("Status"),
                "fieldname": "project_status",
                "fieldtype": "Data",
                "width": 90,
            },
            {
                "label": _("Budget"),
                "fieldname": "budget_amount",
                "fieldtype": "Currency",
                "width": 200,
            },
            {
                "label": _("Project Budget"),
                "fieldname": "budget_id",
                "fieldtype": "Link",
                "options": "Budget",
                "width": 200,
            },
            {
                "label": _("Task"),
                "fieldname": "task_title",
                "fieldtype": "Link",
                "options": "Task",
                "width": 200,
            },
            {
                "label": _("Task ID"),
                "fieldname": "task_id",
                "fieldtype": "Link",
                "options": "Task",
                "width": 200,
            },
        ]

    def build_conditions(self, filters: ReportFilters) -> list[Criterion]:
        conditions = []

        filters_dict = filters.__dict__
        base_program_filters = (
            "company",
            "program_name",
            "program_type",
            "status",
            "program_manager",
        )

        for key, value in filters_dict.items():
            if key in base_program_filters and value:
                conditions.append(self.program[key] == value)

        date_filters = {
            "expected_start_date": self.program.expected_start_date,
            "expected_end_date": self.program.expected_end_date,
        }

        for key, field in date_filters.items():
            value = filters_dict.get(key)
            if value:
                conditions.append(field >= value if "start" in key else field <= value)

        return conditions

    def build_query(self, filters: ReportFilters) -> QueryBuilder:
        conditions = self.build_conditions(filters)

        query = (
            frappe.qb.from_(self.program)
            .left_join(self.project)
            .on(self.program.name == self.project.program)
            .left_join(self.task)
            .on(self.project.name == self.task.project)
            .left_join(self.budget)
            .on(
                (self.budget.budget_against == "Project")
                & (self.budget.project == self.project.name)
            )
            .select(
                self.program.name.as_("program"),
                self.project.project_name,
                self.project.name.as_("project_id"),
                self.project.project_type,
                self.project.status.as_("project_status"),
                self.task.subject.as_("task_title"),
                self.task.name.as_("task_id"),
                self.budget.name.as_("budget_id"),
                self.budget.budget_amount,
            )
        )

        if conditions:
            query = query.where(Criterion.all(conditions))

        return query

    def get_data(self, filters: ReportFilters) -> list[dict]:
        data = self.build_query(filters).run(as_dict=True)
        return self.process_data(data) if data else []

    def process_data(self, data: list[dict]) -> list[dict]:
        rows = []

        seen_programs = set()
        seen_projects = set()

        for d in data:
            program = d.get("program")
            project_id = d.get("project_id")
            project_name = d.get("project_name")
            task_id = d.get("task_id")
            task_title = d.get("task_title")

            if program and program not in seen_programs:
                rows.append(
                    {
                        "name": program,
                        "program": frappe.bold(program),
                        "budget_amount": None,
                        "indent": 0,
                    }
                )
                seen_programs.add(program)

            if project_id and project_id not in seen_projects:
                rows.append(
                    {
                        "name": project_id,
                        "project_name": project_name,
                        "project_id": project_id,
                        "project_type": d.get("project_type"),
                        "project_status": d.get("project_status"),
                        "budget_amount": d.get("budget_amount"),
                        "budget_id": d.get("budget_id"),
                        "parent": program,
                        "indent": 1,
                    }
                )
                seen_projects.add(project_id)

            if task_id:
                rows.append(
                    {
                        "name": task_id,
                        "task_title": task_title,
                        "task_id": task_id,
                        "budget_amount": None,
                        "parent": project_id,
                        "indent": 2,
                    }
                )

        return rows

    def get_report_summary(
        self, data: list[dict], filters: ReportFilters
    ) -> list[dict]:
        total_programs = len(set(d.get("program") for d in data if d.get("program")))
        active_programs = len(
            set(
                d.get("program")
                for d in data
                if d.get("program") and d.get("program_status") == "Active"
            )
        )
        total_projects = len(
            set(d.get("project_id") for d in data if d.get("project_id"))
        )
        active_projects = len(
            set(
                d.get("project_id")
                for d in data
                if d.get("project_id") and d.get("project_type") == "Active"
            )
        )
        budget = sum(d.get("budget_amount", 0) for d in data if d.get("budget_amount"))

        return [
            {
                "value": total_programs,
                "indicator": "Green",
                "label": _("Programs"),
                "datatype": "Int",
            },
            {
                "value": active_programs,
                "indicator": "Red",
                "label": _("Active Programs"),
                "datatype": "Int",
            },
            {
                "value": total_projects,
                "indicator": "Green",
                "label": _("Projects"),
                "datatype": "Int",
            },
            {
                "value": active_projects,
                "indicator": "Red",
                "label": _("Active Projects"),
                "datatype": "Int",
            },
            {
                "value": budget,
                "indicator": "Green",
                "label": _("Total Budget"),
                "datatype": "Currency",
            },
        ]
