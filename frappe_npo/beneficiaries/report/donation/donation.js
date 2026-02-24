// Copyright (c) 2025, hussain@frappe.io and contributors
// For license information, please see license.txt

frappe.query_reports["Donation"] = {
	filters: [
		{
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
			default: frappe.datetime.add_months(
				frappe.datetime.get_today(),
				-1
			),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "donor",
			label: "Donor",
			fieldtype: "Link",
			options: "Donor",
		},
		{
			fieldname: "donation",
			label: "Donation",
			fieldtype: "Link",
			options: "Donation",
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (
			["percent_paid", "percent_distributed"].includes(column.fieldname)
		) {
			const percent = Math.min(
				Math.max(data[column.fieldname] || 0, 0),
				100
			);

			const getColor = (p) => {
				if (p < 30) return "#e74c3c";
				if (p < 50) return "#f39c12";
				if (p < 70) return "#f1c40f";
				if (p < 90) return "#27ae60";
				return "#2ecc71";
			};

			const color = getColor(percent);
			const textInside = percent > 15;

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
						${textInside ? `${percent}%` : ""}
					</div>
					${
						!textInside
							? `<div style="position: absolute; right: 5px; top: 0; font-size: 12px; line-height: 20px; color: #333;">${percent}%</div>`
							: ""
					}
				</div>
			`;
		}

		if (column.fieldname === "donor" && data && data.donor) {
			return `<a href="/app/donor/${data.donor}" target="_blank">${data.donor_name}</a>`;
		}

		return value;
	},
};
