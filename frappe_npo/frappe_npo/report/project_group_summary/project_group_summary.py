# Copyright (c) 2026, Navari Ltd and contributors
# For license information, please see license.txt

import calendar
from dataclasses import dataclass
from typing import Optional

import frappe
from frappe import _
from frappe.query_builder import DocType
from pypika import Criterion
from pypika.queries import QueryBuilder


def execute(filters: dict) -> tuple[list[dict], list[list]]:
	return ProjectGroupSummaryReport(ReportFilters(**filters)).run()


@dataclass
class ReportFilters:
	company: str
	project_group_name: str | None = None
	project_type: str | None = None
	status: str | None = None
	expected_start_date: str | None = None
	expected_end_date: str | None = None
	project_group_manager: str | None = None


@dataclass
class ProjectGroupSummaryReport:
	filters: ReportFilters
	project_group = DocType("Project Group")
	project = DocType("Project")
	task = DocType("Task")
	budget = DocType("Budget")

	def run(self):
		data = self.get_data(self.filters)
		columns = self.get_columns()
		report_summary = self.get_report_summary(data)
		return columns, data, None, None, report_summary

	def get_columns(self) -> list[dict]:
		return [
			{
				"label": _("Project Group"),
				"fieldname": "project_group",
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
				"label": _("Project Budget"),
				"fieldname": "project_budget",
				"fieldtype": "Currency",
				"width": 200,
			},
			{
				"label": _("Budget"),
				"fieldname": "project_budget_id",
				"fieldtype": "Link",
				"options": "Budget",
				"width": 200,
			},
			{
				"label": _("Task"),
				"fieldname": "task_title",
				"fieldtype": "Data",
				"width": 150,
			},
			{
				"label": _("Task ID"),
				"fieldname": "task_id",
				"fieldtype": "Link",
				"options": "Task",
				"width": 200,
			},
			{
				"label": _("Task Budget"),
				"fieldname": "task_budget",
				"fieldtype": "Currency",
				"width": 200,
			},
			{
				"label": _("Budget"),
				"fieldname": "task_budget_id",
				"fieldtype": "Link",
				"options": "Budget",
				"width": 200,
			},
		]

	def build_conditions(self, filters: ReportFilters) -> list[Criterion]:
		conditions = []

		filters_dict = filters.__dict__
		base_program_filters = (
			"company",
			"project_group_name",
			"project_type",
			"status",
			"project_group_manager",
		)

		for key, value in filters_dict.items():
			if key in base_program_filters and value:
				conditions.append(self.project_group[key] == value)

		date_filters = {
			"expected_start_date": self.project_group.expected_start_date,
			"expected_end_date": self.project_group.expected_end_date,
		}

		for key, field in date_filters.items():
			value = filters_dict.get(key)
			if value:
				conditions.append(field >= value if "start" in key else field <= value)

		return conditions

	def build_query(self, filters: ReportFilters) -> QueryBuilder:
		conditions = self.build_conditions(filters)

		query = (
			frappe.qb.from_(self.project_group)
			.left_join(self.project)
			.on(self.project_group.name == self.project.project_group)
			.left_join(self.task)
			.on(self.project.name == self.task.project)
			.left_join(self.budget)
			.on(
				((self.budget.budget_against == "Project") & (self.budget.project == self.project.name))
				| ((self.budget.budget_against == "Task") & (self.budget.task == self.task.name))
			)
			.select(
				self.project_group.name.as_("project_group"),
				self.project.project_name,
				self.project.name.as_("project_id"),
				self.project.project_type,
				self.project.status.as_("project_status"),
				self.task.subject.as_("task_title"),
				self.task.name.as_("task_id"),
				self.budget.name.as_("budget_id"),
				self.budget.budget_amount,
				self.budget.budget_against,
			)
		)

		if conditions:
			query = query.where(Criterion.all(conditions))

		return query

	def get_data(self, filters: ReportFilters) -> tuple[list[dict], list[dict]]:
		data = self.build_query(filters).run(as_dict=True)
		return self.process_data(data) if data else []

	def process_data(self, data: list[dict]) -> list[dict]:
		rows = []
		seen_project_groups = set()
		seen_projects = set()
		seen_tasks = set()  # ADD THIS

		project_budgets = {}
		task_budgets = {}

		for d in data:
			budget_against = d.get("budget_against")
			if budget_against == "Project":
				project_id = d.get("project_id")
				if project_id and project_id not in project_budgets:
					project_budgets[project_id] = {
						"project_budget": d.get("budget_amount"),
						"project_budget_id": d.get("budget_id"),
					}
			elif budget_against == "Task":
				task_id = d.get("task_id")
				if task_id and task_id not in task_budgets:
					task_budgets[task_id] = {
						"task_budget": d.get("budget_amount"),
						"task_budget_id": d.get("budget_id"),
					}

		for d in data:
			project_group = d.get("project_group")
			project_id = d.get("project_id")
			project_name = d.get("project_name")
			task_id = d.get("task_id")
			task_title = d.get("task_title")

			if project_group and project_group not in seen_project_groups:
				rows.append(
					{
						"name": project_group,
						"project_group": frappe.bold(project_group),
						"project_name": None,
						"project_id": None,
						"project_type": None,
						"project_status": None,
						"project_budget": None,
						"project_budget_id": None,
						"task_title": None,
						"task_id": None,
						"task_budget": None,
						"task_budget_id": None,
						"indent": 0,
					}
				)
				seen_project_groups.add(project_group)

			if project_id and project_id not in seen_projects:
				pb = project_budgets.get(project_id, {})
				rows.append(
					{
						"name": project_id,
						"program": None,
						"project_name": project_name,
						"project_id": project_id,
						"project_type": d.get("project_type"),
						"project_status": d.get("project_status"),
						"project_budget": pb.get("project_budget"),
						"project_budget_id": pb.get("project_budget_id"),
						"task_title": None,
						"task_id": None,
						"task_budget": None,
						"task_budget_id": None,
						"parent": project_group,
						"indent": 1,
					}
				)
				seen_projects.add(project_id)

			if task_id and task_id not in seen_tasks:
				tb = task_budgets.get(task_id, {})
				rows.append(
					{
						"name": task_id,
						"program": None,
						"project_name": None,
						"project_id": None,
						"project_type": None,
						"project_status": None,
						"project_budget": None,
						"project_budget_id": None,
						"task_title": task_title,
						"task_id": task_id,
						"task_budget": tb.get("task_budget"),
						"task_budget_id": tb.get("task_budget_id"),
						"parent": project_id,
						"indent": 2,
					}
				)
				seen_tasks.add(task_id)

		return rows

	def get_report_summary(self, data: list[dict]) -> list[dict]:
		total_project_groups = len(set(d.get("project_group") for d in data if d.get("project_group")))

		total_projects = len(set(d.get("project_id") for d in data if d.get("project_id")))

		active_projects = len(
			set(
				d.get("project_id") for d in data if d.get("project_id") and d.get("project_status") == "Open"
			)
		)

		def total_budget(field_name: str) -> float:
			return sum(row.get(field_name) or 0 for row in data)

		return [
			{
				"value": total_project_groups,
				"indicator": "Blue",
				"label": _("Total Project Groups"),
				"datatype": "Int",
			},
			{
				"value": total_projects,
				"indicator": "Blue",
				"label": _("Total Projects"),
				"datatype": "Int",
			},
			{
				"value": active_projects,
				"indicator": "Green",
				"label": _("Active Projects"),
				"datatype": "Int",
			},
			{
				"value": total_budget("project_budget"),
				"indicator": "Red",
				"label": _("Total Project Budget"),
				"datatype": "Currency",
			},
			{
				"value": total_budget("task_budget"),
				"indicator": "Red",
				"label": _("Total Task Budget"),
				"datatype": "Currency",
			},
		]
