// Copyright (c) 2026, Navari Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["NPO Program Summary"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
		},
		{
			fieldname: "program_name",
			label: __("Program"),
			fieldtype: "Link",
			options: "NPO Program",
			get_query: () => {
				let company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						company: company,
					},
				};
			},
		},
		{
			fieldname: "program_type",
			label: __("Program Type"),
			fieldtype: "Link",
			options: "NPO Program Type",
		},
		{
			fieldname: "status",
			label: __("Program Status"),
			fieldtype: "Select",
			options: "\nDraft\nActive\nOn Hold\nCompleted\nCancelled",
		},
		{
			fieldname: "expected_start_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "expected_end_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "program_manager",
			label: __("Program Manager"),
			fieldtype: "Link",
			options: "User",
			get_query: () => {
				return {
					filters: {
						"roles.role": "Program Manager",
					},
				};
			},
		},
	],

	formatter: (value, row, column, data, default_formatter) => {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "project_status") {
			const badgeColor = mapStatusToBadge(value);

			value = `<span class="badge" style="background-color: ${badgeColor}">${value}</span>`;
		}
		return value;
	},
};

function mapStatusToBadge(status) {
	const statusMap = {
		Open: "blue",
		Completed: "green",
		Cancelled: "red",
	};

	return statusMap[status] || "gray";
}
