frappe.listview_settings["Payment Entry"] = {
	onload: function (listview) {
		listview.page.add_action_item(__("Download Payment Proofs"), () => {
			const selected = listview.get_checked_items();
			if (!selected.length) {
				frappe.msgprint(__("Please select at least one Payment Entry"));
				return;
			}

			const dialog = new frappe.ui.Dialog({
				title: __("Enter Folder Name"),
				fields: [
					{
						label: __("Folder Name"),
						fieldname: "folder_name",
						fieldtype: "Data",
						reqd: 1,
						default: "PaymentProofs",
					},
				],
				primary_action_label: __("Download"),
				primary_action: (values) => {
					dialog.hide();
					const payment_entry_names = selected.map((d) => d.name);
					frappe.call({
						method: "frappe_npo.overrides.payment_entry.download_payment_proofs_zip",
						args: {
							payment_entries: payment_entry_names,
							folder_name: values.folder_name,
						},
						freeze: true,
						freeze_message: "Generating ZIP...",
						callback: (r) => {
							console.log(r);
						},
					});
				},
			});
			dialog.show();
		});
	},
};
