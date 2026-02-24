frappe.ui.form.on("Payment Entry", {
	refresh: function (frm) {
		if (frm.doc.party_type == "Donor") {
			frm.set_query("reference_doctype", "references", function () {
				return {
					filters: { name: ["in", ["Donation", "Journal Entry"]] },
				};
			});
		}
		if (frm.doc.docstatus === 1 && frm.doc.references) {
			const has_donation = frm.doc.references.some(
				(ref) => ref.reference_doctype === "Donation",
			);

			if (has_donation) {
				frm.add_custom_button("Allocate Donation", () => {
					frappe.call({
						method: "frappe_npo.beneficiaries.doctype.donation_allocation.donation_allocation.get_available_donations_for_payment_entry",
						args: {
							payment_entry_name: frm.doc.name,
						},
						callback: function (r) {
							if (r.message) {
								const donations = r.message;

								if (donations.length === 0) {
									frappe.msgprint(
										"No unallocated donations found for this Payment Entry.",
									);
									return;
								}

								const donationMap = {};
								const donationOptions = donations.map((d) => {
									donationMap[d.name] = d;
									return d.name;
								});

								const dialog = new frappe.ui.Dialog({
									title: "Allocate Donation",
									fields: [
										{
											label: "Select Donation",
											fieldname: "donation",
											fieldtype: "Link",
											options: "Donation",
											reqd: 1,
											get_query: () => ({
												filters: [["name", "in", donationOptions]],
											}),
										},
										{
											label: "Allocate to Budget",
											fieldname: "allocate_to_budget",
											fieldtype: "Check",
											default: 0,
										},
										{
											label: "Budget",
											fieldname: "budget",
											fieldtype: "Link",
											options: "Budget",
											depends_on: "eval:doc.allocate_to_budget == 1",
											mandatory_depends_on:
												"eval:doc.allocate_to_budget == 1",
											get_query: () => ({
												query: "frappe_npo.beneficiaries.doctype.donation_allocation.donation_allocation.get_available_budgets",
											}),
										},
									],
									primary_action_label: "Allocate",
									primary_action: function (values) {
										frappe.route_options = {
											donation: values.donation,
											total_amount:
												donationMap[values.donation]?.remaining_amount,
										};

										const temp_data = {
											budget: values.budget,
											payment_entry: frm.doc.name,
										};

										localStorage.setItem(
											"donation_allocation_temp",
											JSON.stringify(temp_data),
										);

										frappe.new_doc("Donation Allocation");
										dialog.hide();
									},
								});

								dialog.show();
							} else {
								frappe.msgprint("Error fetching available donations.");
							}
						},
					});
				});
			}
		}
	},
});
