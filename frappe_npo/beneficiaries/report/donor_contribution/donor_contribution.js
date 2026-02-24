// Copyright (c) 2025, hussain@frappe.io and contributors
// For license information, please see license.txt

frappe.query_reports["Donor Contribution"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(
				frappe.datetime.get_today(),
				-1
			),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
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
		},
		{
			fieldname: "recipient_type",
			label: __("Recipient Type"),
			fieldtype: "Select",
			options: [
				"",
				"Learning Centre",
				"Student",
				"Beneficiary",
				"Budget",
				"Employee",
			],
			default: "",
		},
		{
			fieldname: "beneficiary",
			label: __("Beneficiary"),
			fieldtype: "Link",
			options: "Beneficiary",
			depends_on: 'eval:doc.recipient_type=="Beneficiary"',
		},
		{
			fieldname: "student",
			label: __("Student"),
			fieldtype: "Link",
			options: "Student",
			depends_on: 'eval:doc.recipient_type=="Student"',
		},
		{
			fieldname: "learning_centre",
			label: __("Learning Centre"),
			fieldtype: "Link",
			options: "Learning Centre",
			depends_on: 'eval:doc.recipient_type=="Learning Centre"',
		},
		{
			fieldname: "budget",
			label: __("Budget"),
			fieldtype: "Link",
			options: "Budget",
			depends_on: 'eval:doc.recipient_type=="Budget"',
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
			depends_on: 'eval:doc.recipient_type=="Employee"',
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
		},

		{
			fieldname: "general_admin",
			label: __("General / Admin"),
			fieldtype: "Data",
		},
		{
			fieldname: "show_total_pledged",
			label: __("Show Pledged Amount"),
			fieldtype: "Check",
			default: 0,
		},
		{
			fieldname: "show_total_paid",
			label: __("Show Total Paid Amount"),
			fieldtype: "Check",
			default: 0,
		},
		{
			fieldname: "show_total_distributed",
			label: __("Show Distributed Amount"),
			fieldtype: "Check",
			default: 0,
		},
	],

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname === "percentage") {
			const percent = Math.min(
				Math.max(data[column.fieldname] || 0, 0),
				100
			);
			const color = "#2ecc71";
			const textInside = percent > 40;
			const percentStr = percent.toFixed(2);

			return `
                <div style="width: 100%; background-color: #e0e0e0; border-radius: 8px; overflow: hidden; position: relative; height: 20px;">
                    <div style="
                        width: ${percent}%;
                        background-color: ${color};
                        height: 100%;
                        transition: width 0.3s ease;
                        text-align: ${textInside ? "center" : "right"};
                        color: white;
                        font-size: 12px;
                        line-height: 20px;
                        padding-right: ${textInside ? "0" : "5px"};
                    ">
                        ${textInside ? `${percentStr}%` : ""}
                    </div>
                    ${
						!textInside
							? `<div style="position: absolute; right: 5px; top: 0; font-size: 12px; line-height: 20px; color: #333;">${percentStr}%</div>`
							: ""
					}
                </div>`;
		}

		if (column.fieldname === "donor" && data && data.donor) {
			return `<a href="/app/donor/${data.donor}" target="_blank">${
				data.donor_name || data.donor
			}</a>`;
		}

		if (
			column.fieldname === "recipient" &&
			data &&
			data.recipient &&
			data.recipient_type
		) {
			const doctype_name = data.recipient_type.replace(/\s/g, "-");
			return `<a href="/app/${doctype_name}/${data.recipient}" target="_blank">${value}</a>`;
		}

		if (column.fieldname === "project" && data && data.project) {
			return `<a href="/app/project/${data.project}" target="_blank">${value}</a>`;
		}

		// Generic blanking for specified numeric fields if value is "" or "0"
		const blankFields = [
			"pledged_amount",
			"amount",
			"total_amount",
			"total_paid_amount",
			"amount_distributed",
		];

		if (
			blankFields.includes(column.fieldname) &&
			data &&
			(data[column.fieldname] === "" ||
				data[column.fieldname] == "0" ||
				data[column.fieldname] == 0 ||
				!data[column.fieldname])
		) {
			return " ";
		}

		return value;
	},
};
