frappe.ui.form.on("Project", {
	refresh: function (frm) {
		setup_state_filter(frm);
		if (frm.doc.project_type === "Food Distribution") {
			frm.add_custom_button("Distribute Food", () => {
				open_distribution_modal(frm);
			});
		}
	},

	custom_project_countrys: function (frm) {
		filter_states_by_selected_countries(frm);
	},
});

function setup_state_filter(frm) {
	let states_field = frm.fields_dict.custom_states;

	states_field.get_query = function () {
		let selected_countries = (frm.doc.custom_project_countrys || []).map((d) => d.country);

		if (selected_countries.length > 0) {
			return {
				filters: {
					country: ["in", selected_countries],
				},
			};
		} else {
			return {};
		}
	};
}

function filter_states_by_selected_countries(frm) {
	if (frm.fields_dict.custom_states) {
		frm.fields_dict.custom_states.refresh();
	}

	let selected_states = frm.doc.custom_states || [];
	let selected_country_names = (frm.doc.custom_project_countrys || []).map((d) => d.country);

	if (selected_states.length > 0 && selected_country_names.length > 0) {
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "State",
				filters: {
					name: ["in", selected_states.map((d) => d.state)],
					country: ["not in", selected_country_names],
				},
				fields: ["name"],
			},
			callback: function (r) {
				if (r.message && r.message.length > 0) {
					let valid_states = selected_states.filter(
						(d) => !r.message.some((invalid) => invalid.name === d.state),
					);

					if (valid_states.length !== selected_states.length) {
						frm.set_value("custom_states", valid_states);
					}
				}
			},
		});
	}
}

function open_distribution_modal(frm) {
	frappe.call({
		method: "frappe_npo.beneficiaries.overrides.stock_entry_query.get_distribution_data",
		args: {
			project: frm.doc.name,
		},
		callback: function (r) {
			if (r.message) {
				let { bom, beneficiaries } = r.message;

				let dialog = new frappe.ui.Dialog({
					title: "Create Food Distribution Entry",
					fields: [
						{
							label: "BOM",
							fieldname: "bom",
							fieldtype: "Link",
							options: "BOM",
							reqd: 1,
							default: bom,
							get_query: () => ({
								filters: {
									project: frm.doc.name,
								},
							}),
						},
						{
							label: "Warehouse",
							fieldname: "warehouse",
							fieldtype: "Link",
							options: "Warehouse",
							reqd: 1,
							get_query: () => ({
								filters: {
									disabled: 0,
								},
							}),
						},
						{
							label: "Beneficiaries",
							fieldname: "beneficiaries",
							fieldtype: "Table",
							cannot_add_rows: false,
							data: beneficiaries,
							get_data: () => beneficiaries,
							fields: [
								{
									fieldname: "beneficiary",
									label: "ID",
									fieldtype: "Link",
									options: "Beneficiary",
									in_list_view: 1,
									reqd: 1,
									cols: 2,
									get_query: () => ({
										filters: {
											branch: frm.doc.branch,
											status: "Active",
										},
									}),
								},
								{
									fieldname: "full_name",
									label: "Full Name",
									fieldtype: "Data",
									in_list_view: 1,
									reqd: 1,
									read_only: 1,
									cols: 4,
									get_value: (d) => d.beneficiary_full_name,
								},
							],
						},
					],
					primary_action_label: "Create Stock Entries",
					primary_action(values) {
						frappe.call({
							method: "frappe_npo.beneficiaries.overrides.stock_entry_query.create_food_stock_entries",
							args: {
								project: frm.doc.name,
								bom: values.bom,
								beneficiaries: values.beneficiaries,
								warehouse: values.warehouse,
							},
							freeze: true,
							callback: function (res) {
								if (res.message) {
									frappe.msgprint("Stock Entries Created Successfully!");
									dialog.hide();
								}
							},
						});
					},
				});

				dialog.show();
			}
		},
	});
}
