// Copyright (c) 2025, [hussain@frappe.io](mailto:hussain@frappe.io) and contributors
// For license information, please see license.txt

frappe.query_reports["Beneficiary"] = {
	filters: [
		{
			fieldname: "program",
			label: "Program",
			fieldtype: "Link",
			options: "Program",
		},
		{
			fieldname: "lead_donor",
			label: "Lead Donor",
			fieldtype: "Link",
			options: "Donor",
		},
		{
			fieldname: "subdonor",
			label: "Subdonor",
			fieldtype: "Link",
			options: "Donor",
		},
		{
			fieldname: "beneficiary_type",
			label: "Beneficiary Type",
			fieldtype: "Select",
			options: ["", "Student", "Teacher", "Others"],
		},
		{
			fieldname: "status",
			label: "Status",
			fieldtype: "Link",
			options: "Beneficiary Status",
		},
		{
			fieldname: "program_country",
			label: "Country",
			fieldtype: "Link",
			options: "Country",
		},
		{
			fieldname: "programme_state",
			label: "State",
			fieldtype: "Data",
		},
		{
			fieldname: "programme_county",
			label: "County",
			fieldtype: "Data",
		},
		{
			fieldname: "institution",
			label: "Institution",
			fieldtype: "Data",
		},
		{
			fieldname: "course",
			label: "Course",
			fieldtype: "Link",
			options: "Course",
		},
		{
			fieldname: "thematic_area",
			label: "Thematic Area",
			fieldtype: "Link",
			options: "Thematic Area",
		},
		{
			fieldname: "start_date_from",
			label: "Start Date From",
			fieldtype: "Date",
		},
		{
			fieldname: "start_date_to",
			label: "Start Date To",
			fieldtype: "Date",
		},
		{
			fieldname: "end_date_from",
			label: "End Date From",
			fieldtype: "Date",
		},
		{
			fieldname: "end_date_to",
			label: "End Date To",
			fieldtype: "Date",
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "status") {
			const status_colors = {
				Active: "green",
				Inactive: "red",
				Alumni: "purple",
				Deceased: "blue",
			};

			const status = data["status"];
			if (status && status_colors[status]) {
				value = `<span style="color:${status_colors[status]};font-weight:bold">${value}</span>`;
			}
		}

		return value;
	},
};
