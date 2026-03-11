from frappe import _


def get_data():
    return {
        "fieldname": "disbursement_order",
        "internal_links": {
            "Sales Invoice": ["items", "disbursement_order"],
        },
        "transactions": [
            {
                "label": _("Sales"),
                "items": ["Sales Order", "Sales Invoice"],
            },
            {
                "label": _("Payment"),
                "items": ["Payment Entry"],
            },
            {
                "label": _("Project & Verification"),
                "items": ["Project", "Verification Request"],
            },
        ],
    }
