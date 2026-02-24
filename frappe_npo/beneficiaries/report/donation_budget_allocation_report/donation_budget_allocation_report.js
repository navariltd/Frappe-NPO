// Copyright (c) 2025, hussain@frappe.io and contributors
// For license information, please see license.txt

frappe.query_reports["Donation Budget Allocation Report"] = {
	filters: [
		{
			fieldname: "budget_against",
			label: __("Budget Against"),
			fieldtype: "Select",
			options: [
				"",
				"Project",
				"Employee",
				"Task",
				"Cost Center",
				"Program",
			],
			default: "",
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
			depends_on: "eval:doc.budget_against == 'Project'",
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			depends_on: "eval:doc.budget_against == 'Employee'",
		},
		{
			fieldname: "task",
			label: __("Task"),
			fieldtype: "Link",
			options: "Task",
			depends_on: "eval:doc.budget_against == 'Task'",
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
			depends_on: "eval:doc.budget_against == 'Cost Center'",
		},
		{
			fieldname: "program",
			label: __("Program"),
			fieldtype: "Link",
			options: "Program",
			depends_on: "eval:doc.budget_against == 'Program'",
		},
		{
			fieldname: "budget_against_docname",
			label: __("Budget Against (Name)"),
			fieldtype: "Link",
			options: "",
			hidden: 1,
		},
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: frappe.defaults.get_user_default("fiscal_year"),
		},
		{
			fieldname: "budget_name",
			label: __("Budget Name"),
			fieldtype: "Link",
			options: "Budget",
		},
		{
			fieldname: "budget_account",
			label: __("Budget Account"),
			fieldtype: "Link",
			options: "Account",
		},
		{
			fieldname: "donor",
			label: __("Donor"),
			fieldtype: "Link",
			options: "Donor",
		},
		{
			fieldname: "donation",
			label: __("Donation"),
			fieldtype: "Link",
			options: "Donation",
			depends_on: "eval:doc.donor",
			get_query: function () {
				let donor = frappe.query_report.get_filter_value("donor");
				if (donor) {
					return {
						filters: {
							donor: donor,
						},
					};
				}
			},
		},
		{
			fieldname: "donation_allocation",
			label: __("Donation Allocation"),
			fieldtype: "Link",
			options: "Donation Allocation",
			depends_on: "eval:doc.donation",
			get_query: function () {
				let donation = frappe.query_report.get_filter_value("donation");
				if (donation) {
					return {
						filters: {
							donation: donation,
						},
					};
				}
			},
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		let formatted_value = default_formatter(value, row, column, data);

		const blankFields = [
			"amount",
			"allocation_amount",
			"budget_amount",
			"actual_amount",
			"months_distributed",
			"percentage",
			"variance_amount",
		];

		// Check if the column is one of the blankable fields OR a dynamically generated month column
		if (
			(blankFields.includes(column.fieldname) ||
				/\d+$/.test(column.fieldname)) &&
			data &&
			(value === null ||
				value === undefined ||
				value === "" ||
				value === 0 ||
				value === "0%" ||
				formatted_value === "Sh 0.00")
		) {
			return "";
		}

		return formatted_value;
	},
};
