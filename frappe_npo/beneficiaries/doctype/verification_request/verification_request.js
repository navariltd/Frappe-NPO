// Copyright (c) 2026, Navari Ltd and contributors
// For license information, please see license.txt

var in_progress = false;
frappe.ui.form.on("Verification Request", {
	refresh: function (frm) {
		frm.trigger("render_custom_table_actions");
	},

	render_custom_table_actions: function (frm) {
		const grid_wrapper = frm.get_field("items").$wrapper;
		grid_wrapper.find(".custom-grid-actions").remove();

		const $btn_container = $(`
			<div class="custom-grid-actions" style="margin-bottom: 10px; display: flex; gap: 10px; align-items: center;">
				<button type="button" class="btn btn-xs btn-default btn-upload-verification">
					<i class="fa fa-upload"></i> ${__("Upload Verification Results")}
				</button>
				<button type="button" class="btn btn-xs btn-primary btn-set-status" style="display: none;">
					<i class="fa fa-check-square-o"></i> ${__("Set Status for Selected")}
				</button>
			</div>
		`).prependTo(grid_wrapper);

		$btn_container.find(".btn-upload-verification").on("click", () => {
			frm.trigger("upload_verification_results");
		});

		$btn_container.find(".btn-set-status").on("click", () => {
			frm.trigger("set_status_for_selected");
		});

		frm.trigger("toggle_grid_selection_button");
	},

	toggle_grid_selection_button: function (frm) {
		const grid = frm.get_field("items").grid;
		const selected = grid.get_selected_children();
		const $btn_status = frm.get_field("items").$wrapper.find(".btn-set-status");

		if (selected.length > 0) {
			$btn_status.fadeIn(200);
		} else {
			$btn_status.fadeOut(200);
		}
	},

	set_status_for_selected: function (frm) {
		const grid = frm.get_field("items").grid;
		const selected = grid.get_selected_children();

		const d = new frappe.ui.Dialog({
			title: __("Update Status"),
			fields: [
				{
					label: __("Status"),
					fieldname: "status",
					fieldtype: "Select",
					options: ["Open", "Verified", "Not Verified"],
					reqd: 1,
				},
				{
					label: __("Comments"),
					fieldname: "comments",
					fieldtype: "Small Text",
				},
			],
			primary_label: __("Update"),
			primary_action: (values) => {
				selected.forEach((row) => {
					frappe.model.set_value(row.doctype, row.name, "status", values.status);
					if (values.comments) {
						frappe.model.set_value(row.doctype, row.name, "comments", values.comments);
					}
				});
				grid.refresh();
				d.hide();
			},
		});
		d.show();
	},

	upload_verification_results: function (frm) {
		new frappe.ui.FileUploader({
			allow_multiple: false,
			on_success: (file) => {
				frm.call({
					method: "process_verification_upload",
					doc: frm.doc,
					args: { file_url: file.file_url },
					freeze: true,
					freeze_message: __("Updating rows..."),
					callback: (r) => {
						if (r.message) {
							frm.reload_doc();
							frappe.show_alert({
								message: __("Verification statuses updated"),
								indicator: "green",
							});
						}
					},
				});
			},
			restrictions: { allowed_file_types: [".csv", ".xlsx", ".xls"] },
		});
	},
});

frappe.ui.form.on("Verification Request Item", {
	items_add: function (frm) {
		frm.trigger("toggle_grid_selection_button");
	},
	items_remove: function (frm) {
		frm.trigger("toggle_grid_selection_button");
	},
	form_render: function (frm) {
		frm.trigger("toggle_grid_selection_button");
	},
});

$(document).on("change", 'div[data-fieldname="items"] .grid-row-check', function () {
	let frm = cur_frm;
	if (frm && frm.doctype === "Verification Request") {
		frm.trigger("toggle_grid_selection_button");
	}
});
