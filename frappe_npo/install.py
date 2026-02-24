import frappe

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from .setup import setup_non_profit
from frappe_npo.utils.data import scrap_and_import_india_district_list
from .beneficiaries.patches.set_default_beneficiary_status import (
    create_beneficiary_status,
)


def after_install():
    # Change password reset link expiry to 1 day
    frappe.db.set_single_value(
        "System Settings", "reset_password_link_expiry_duration", 86400
    )

    try:
        # Create default beneficiary status
        setup_non_profit()
        create_beneficiary_status()
        frappe.db.commit()
    except Exception:
        frappe.errprint("Beneficiary Status Creation Failed")

    # Import indian district list
    try:
        scrap_and_import_india_district_list()
        frappe.db.set_single_value("Frappe NPO Settings", "statedistrict_imported", 1)
        frappe.db.commit()
    except Exception:
        frappe.errprint("Indian District Import Failed")


def is_app_installed(app_name: str) -> bool:
    return app_name in frappe.get_installed_apps()


def after_migrate():
    if is_app_installed("education"):
        custom_fields = {
            "Student": [
                {
                    "fieldname": "school",
                    "fieldtype": "Link",
                    "label": "School",
                    "options": "Learning Centre",
                    "translatable": 1,
                    "insert_after": "last_name",
                }
            ],
            "Instructor": [
                {
                    "fieldname": "school",
                    "fieldtype": "Link",
                    "label": "School",
                    "options": "Learning Centre",
                    "translatable": 1,
                    "insert_after": "gender",
                }
            ],
            "Task": [
                {
                    "fieldname": "program",
                    "fieldtype": "Link",
                    "label": "Program",
                    "options": "Program",
                    "translatable": 1,
                    "insert_after": "project",
                }
            ],
        }

        create_custom_fields(custom_fields, update=True)
