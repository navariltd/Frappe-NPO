// Copyright (c) 2025, hussain@frappe.io and contributors
// For license information, please see license.txt

frappe.query_reports["Donation Payments"] = {
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
	],

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname === "payment_percentage") {
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
					</div>
				`;
		}
		if (column.fieldname === "donor" && data && data.donor) {
			return `<a href="/app/donor/${data.donor}" target="_blank">${data.donor_name}</a>`;
		}
		if (
			column.fieldname === "amount_pledged" &&
			data &&
			(data.amount_pledged === "" || data.amount_pledged === "0")
		) {
			return " ";
		}
		return value;
	},
};
