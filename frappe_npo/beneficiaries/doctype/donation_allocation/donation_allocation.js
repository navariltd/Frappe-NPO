frappe.ui.form.on("Donation Allocation", {
	refresh(frm) {
		if (!frm.doc.from_date) {
			frm.set_value("from_date", frappe.datetime.get_today());
		}

		handle_temp_values_from_local_storage(frm);
		add_get_items_from_budget_button(frm);
		setup_account_query(frm);

		if (frm.doc.donation) {
			calculate_unallocated_amount(frm);
		}
	},

	before_save: function (frm) {
		update_total_amount(frm);
	},

	donation_total_paid_amount(frm) {
		calculate_unallocated_amount(frm);
	},

	total_amount(frm) {
		if (
			frm.doc.total_amount &&
			frm.doc.donation_unallocated_amount &&
			flt(frm.doc.total_amount) > flt(frm.doc.donation_unallocated_amount)
		) {
			frappe.msgprint(
				__("Total Allocation Amount cannot be greater than the Unallocated Balance."),
			);
			frm.set_value("total_amount", "");
		}
	},

	donation(frm) {
		calculate_unallocated_amount(frm);
	},
});

frappe.ui.form.on("Donation Allocation Item", {
	recipient_type: function (frm, cdt, cdn) {
		setup_account_query_for_row(frm, cdt, cdn);
		refresh_field("account", cdn, "items");
	},

	recipient: function (frm, cdt, cdn) {
		setup_account_query_for_row(frm, cdt, cdn);
		refresh_field("account", cdn, "items");
	},

	amount: function (frm, cdt, cdn) {
		update_total_amount(frm);
	},

	items_add: function (frm, cdt, cdn) {
		if (frm.doc.payment_entry) {
			frappe.model.set_value(cdt, cdn, "payment_entry", frm.doc.payment_entry);
		}

		update_total_amount(frm);
	},

	items_remove: function (frm, cdt, cdn) {
		update_total_amount(frm);
	},
});

function handle_temp_values_from_local_storage(frm) {
	const data = localStorage.getItem("donation_allocation_temp");
	if (!data) return;

	const temp_data = JSON.parse(data);
	localStorage.removeItem("donation_allocation_temp");

	if (temp_data.payment_entry) {
		frm.doc.payment_entry = temp_data.payment_entry;
	}

	if (temp_data.budget) {
		frm.doc.budget = temp_data.budget;
		allocate_items_from_budget(frm, temp_data.budget, temp_data.payment_entry);
	}
}

function add_get_items_from_budget_button(frm) {
	frm.add_custom_button(
		"Budget",
		() => {
			frappe.prompt(
				[
					{
						label: "Budget",
						fieldname: "budget",
						fieldtype: "Link",
						options: "Budget",
						get_query: () => ({
							query: "frappe_npo.beneficiaries.doctype.donation_allocation.donation_allocation.get_available_budgets",
						}),
						reqd: true,
					},
				],
				(values) => {
					allocate_items_from_budget(frm, values.budget, frm.doc.payment_entry);
				},
				"Select Budget",
				"Allocate",
			);
		},
		__("Get items from"),
	);
}

function allocate_items_from_budget(frm, budget, payment_entry = null) {
	frm.doc.items = frm.doc.items.filter((row) => {
		return flt(row.amount) > 0;
	});
	frm.refresh_field("items");

	const already_allocated = frm.doc.items.reduce((total, row) => {
		return total + flt(row.amount || 0);
	}, 0);

	const total_available = flt(frm.doc.total_amount || 0);
	const remaining_to_allocate = total_available - already_allocated;

	if (remaining_to_allocate <= 0) {
		frappe.msgprint("All funds have already been allocated.");
		return;
	}

	frappe.call({
		method: "frappe_npo.beneficiaries.doctype.donation_allocation.donation_allocation.allocate_to_budget",
		args: {
			total_amount_to_allocate: remaining_to_allocate,
			budget: budget,
		},
		callback: (r) => {
			if (r.message && r.message.length > 0) {
				let allocated = 0;

				r.message.forEach((row) => {
					if (allocated >= remaining_to_allocate) return;

					const remaining = remaining_to_allocate - allocated;
					const amount = Math.min(row.amount, remaining);

					if (amount > 0) {
						const child = frm.add_child("items");
						child.account = row.account;
						child.amount = amount;
						child.recipient = budget;
						child.recipient_type = "Budget";

						if (payment_entry) {
							child.payment_entry = payment_entry;
						}

						allocated += amount;
					}
				});

				frm.refresh_field("items");
			} else {
				frappe.msgprint("No allocatable accounts found in the selected budget.");
			}
		},
	});
}

function setup_account_query(frm) {
	if (!frm.fields_dict.items) return;

	frm.fields_dict.items.grid.grid_rows.forEach((row) => {
		setup_account_query_for_row(frm, row.doc.doctype, row.doc.name);
	});
}

function setup_account_query_for_row(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	const grid = frm.fields_dict.items.grid;
	if (!grid || !row) return;

	const account_field = grid.get_field("account", cdn);
	if (!account_field) return;

	let filters = { name: ["in", []] };

	if (row.recipient_type === "Budget" && row.recipient) {
		frappe
			.call({
				method: "frappe_npo.beneficiaries.doctype.donation_allocation.donation_allocation.get_budget_accounts",
				args: { budget_name: row.recipient },
			})
			.then((r) => {
				if (r.message) {
					filters = { name: ["in", r.message] };
				}
				account_field.get_query = () => ({ filters });
				frm.fields_dict.items.grid.refresh();
			})
			.catch((err) => {
				console.error("Error fetching budget accounts:", err);
			});
	}
}

function calculate_unallocated_amount(frm) {
	if (!frm.doc.donation || !frm.doc.donation_total_paid_amount) return;

	frappe.call({
		method: "frappe_npo.beneficiaries.doctype.donation_allocation.donation_allocation.get_total_allocated_amount",
		args: {
			donation_name: frm.doc.donation,
			exclude_allocation: frm.doc.name || null,
		},
		callback: (r) => {
			if (r.message !== undefined) {
				const allocated = r.message;
				const unallocated = frm.doc.donation_total_paid_amount - allocated;
				frm.set_value("donation_unallocated_amount", unallocated);
			}
		},
	});
}

function update_total_amount(frm) {
	let total = 0;
	(frm.doc.items || []).forEach((row) => {
		row.amount = flt(row.rate || 0) * flt(row.qty || 0);
		total += flt(row.amount || 0);
	});
	frm.set_value("total_amount", total);
}
