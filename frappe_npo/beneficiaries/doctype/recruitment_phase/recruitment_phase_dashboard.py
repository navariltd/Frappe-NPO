from frappe import _


def get_data():
    return {
        "fieldname": "recruitment_phase",
        "transactions": [
            {
                "label": _(""),
                "items": [
                    "Beneficiary",
                    # "Donor",
                ],
            },
        ],
    }
