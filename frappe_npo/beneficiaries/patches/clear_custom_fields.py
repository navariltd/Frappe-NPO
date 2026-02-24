import frappe


def execute():
    custom_fields = frappe.get_all(
        "Custom Field", filters={"module": "Beneficiaries"}, pluck="name"
    )

    for field in custom_fields:
        frappe.delete_doc("Custom Field", field, ignore_permissions=True)

    frappe.db.commit()
