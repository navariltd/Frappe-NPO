import frappe

def create_beneficiary_status() -> None:
    status_list = [
        "Waitlist",
        "Endorsed",
        "Approved",
        "Active",
        "Relocated",
        "Deceased",
        "Disqualified",
        "Inactive",
        "Alumni",
        "Archived"
    ]

    for status in status_list:
        if not frappe.db.exists("Beneficiary Status", status):
            frappe.get_doc({
                "doctype": "Beneficiary Status",
                "status": status
            }).insert(ignore_permissions=True)
            frappe.db.commit()

def execute() -> None:
    create_beneficiary_status()
