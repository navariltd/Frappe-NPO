frappe.ui.form.on("Sales Invoice", {
	refresh: function (frm) {
		if (frm.doc.docstatus === 0 && !frm.doc.is_return) {
			frm.add_custom_button(
				__("Disbursement Order"),
				function () {
					frm.events.show_disbursement_order_selector(frm);
				},
				__("Get Items From"),
			);
		}
	},

	show_disbursement_order_selector: function (frm) {
		let d;

		const fetch_data = () => {
			frappe.call({
				method: "frappe_npo.overrides.sales_invoice.get_disbursement_orders",
				args: {
					from_date: d.get_value("from_date"),
					to_date: d.get_value("to_date"),
					company: d.get_value("company"),
					donor: d.get_value("donor"),
					po_no: d.get_value("po_no"),
					disbursement_type: d.get_value("disbursement_type"),
				},
				callback: function (r) {
					let grid = d.fields_dict.orders_table.grid;
					grid.df.data = [];

					if (r.message) {
						r.message.forEach((row) => {
							grid.df.data.push({
								selected: 0,
								name: row.name,
								donor: row.donor,
								po_no: row.po_no,
								po_date: row.po_date,
							});
						});
					}

					grid.refresh();
				},
			});
		};

		const debounce_fetch = frappe.utils.debounce(fetch_data, 300);

		d = new frappe.ui.Dialog({
			title: __("Select Disbursement Orders"),
			size: "large",
			fields: [
				{
					label: __("Donor"),
					fieldname: "donor",
					fieldtype: "Link",
					options: "Donor",
					onchange: debounce_fetch,
					reqd: 1,
				},
				{
					label: __("From Date"),
					fieldname: "from_date",
					fieldtype: "Date",
					onchange: debounce_fetch,
				},
				{
					label: __("To Date"),
					fieldname: "to_date",
					fieldtype: "Date",
					onchange: debounce_fetch,
				},
				{ fieldtype: "Column Break" },
				{
					label: __("Company"),
					fieldname: "company",
					fieldtype: "Link",
					options: "Company",
					default: frm.doc.company,
					onchange: debounce_fetch,
				},
				{
					label: __("Disbursement Type"),
					fieldname: "disbursement_type",
					fieldtype: "Select",
					options: "\nCash\nPhysical Goods\nServices",
					onchange: debounce_fetch,
				},
				{
					label: __("PO No"),
					fieldname: "po_no",
					fieldtype: "Data",
					onchange: debounce_fetch,
				},
				{ fieldtype: "Section Break" },
				{
					label: __("Disbursement Orders"),
					fieldname: "orders_table",
					fieldtype: "Table",
					cannot_add_rows: true,
					in_place_edit: false,
					fields: [
						{
							fieldtype: "Link",
							fieldname: "name",
							options: "Disbursement Order",
							label: __("Order ID"),
							in_list_view: 1,
							read_only: 1,
						},
						{
							fieldtype: "Link",
							fieldname: "donor",
							options: "Donor",
							label: __("Donor"),
							in_list_view: 1,
							read_only: 1,
						},
						{
							fieldtype: "Data",
							fieldname: "po_no",
							label: __("PO No"),
							in_list_view: 1,
							read_only: 1,
						},
						{
							fieldtype: "Date",
							fieldname: "po_date",
							label: __("PO Date"),
							in_list_view: 1,
							read_only: 1,
						},
					],
				},
			],
			primary_action_label: __("Fetch Items"),
			primary_action: function () {
				const selected_rows = d.fields_dict.orders_table.grid.get_selected_children();

				if (!selected_rows.length) {
					frappe.msgprint(__("Please select at least one order"));
					return;
				}

				frappe.call({
					method: "frappe_npo.overrides.sales_invoice.get_disbursement_totals",
					args: { orders: selected_rows.map((r) => r.name) },
					callback: async function (r) {
						if (r.message) {
							const { items, customer, donor } = r.message;

							if (customer) frm.set_value("customer", customer);
							if (donor) frm.set_value("donor", donor);
							if (items.length) {
								frm.set_value("disbursement_order", items[0].disbursement_order);
							}

							frm.clear_table("items");

							const company_resp = await frappe.db.get_value(
								"Company",
								frm.doc.company,
								"default_income_account",
							);
							const company_default = company_resp.message.default_income_account;

							items.forEach((item) => {
								let row = frm.add_child("items");

								row.item_code = item.item_code;
								row.item_name = item.item_name;
								row.uom = item.uom;
								row.project = item.project;
								row.qty = item.qty || 1;
								row.rate = item.rate;
								row.amount = item.amount;
								row.disbursement_order = item.disbursement_order;

								if (item.description) {
									row.description = item.description;
								}
								if (!row.income_account && company_default) {
									row.income_account = company_default;
								}
							});

							frm.refresh_field("items");
							frm.trigger("calculate_taxes_and_totals");

							d.hide();
						}
					},
				});

				d.hide();
			},
		});

		d.show();
	},
});
