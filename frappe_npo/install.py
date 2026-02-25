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
            "Beneficiary": [
                {
                    "fieldname": "programme_tab",
                    "fieldtype": "Tab Break",
                    "label": "Programme Details",
                    "insert_after": "image",
                },
                {
                    "fieldname": "programme_section",
                    "fieldtype": "Section Break",
                    "insert_after": "programme_tab",
                },
                {
                    "fieldname": "program",
                    "fieldtype": "Link",
                    "label": "Programme",
                    "options": "Program",
                    "insert_after": "programme_section",
                },
                {
                    "fieldname": "programme_start_date",
                    "fieldtype": "Date",
                    "label": "Programme Start Date",
                    "insert_after": "program",
                },
                {
                    "fieldname": "programme_end_date",
                    "fieldtype": "Date",
                    "label": "Programme End Date",
                    "insert_after": "programme_start_date",
                },
                {
                    "fieldname": "lead_donor",
                    "fieldtype": "Link",
                    "label": "Lead Donor",
                    "options": "Donor",
                    "insert_after": "programme_end_date",
                },
                {
                    "fieldname": "subdonor",
                    "fieldtype": "Link",
                    "label": "Sub Donor",
                    "options": "Donor",
                    "insert_after": "lead_donor",
                },
                {
                    "fieldname": "column_break_fypz",
                    "fieldtype": "Column Break",
                    "insert_after": "subdonor",
                },
                {
                    "fieldname": "scholarship_status",
                    "fieldtype": "Select",
                    "label": "Scholarship Status",
                    "options": "\nSuccessful: Completed/Graduated\nUnsuccessful: Failed\nUnsuccessful: Other (Died)",
                    "insert_after": "column_break_fypz",
                },
                {
                    "fieldname": "program_country",
                    "fieldtype": "Link",
                    "label": "Programme Country",
                    "options": "Country",
                    "insert_after": "scholarship_status",
                },
                {
                    "fieldname": "programme_state",
                    "fieldtype": "Data",
                    "label": "Programme State",
                    "insert_after": "program_country",
                },
                {
                    "fieldname": "programme_county",
                    "fieldtype": "Data",
                    "label": "Programme County",
                    "insert_after": "programme_state",
                },
                {
                    "fieldname": "institution",
                    "fieldtype": "Link",
                    "label": "Institution",
                    "options": "Learning Centre",
                    "insert_after": "programme_county",
                },
                {
                    "fieldname": "course_section",
                    "fieldtype": "Section Break",
                    "insert_after": "institution",
                },
                {
                    "fieldname": "course",
                    "fieldtype": "Link",
                    "label": "Course",
                    "options": "Course",
                    "insert_after": "course_section",
                },
                {
                    "fieldname": "thematic_area",
                    "fieldtype": "Link",
                    "label": "Thematic Area",
                    "options": "Thematic Area",
                    "insert_after": "course",
                },
                {
                    "fieldname": "column_break_kvlj",
                    "fieldtype": "Column Break",
                    "insert_after": "thematic_area",
                },
                {
                    "fieldname": "course_level",
                    "fieldtype": "Select",
                    "label": "Course Level",
                    "options": "\nPostgraduate Masters\nPostgraduate Doctorate",
                    "insert_after": "column_break_kvlj",
                },
                {
                    "fieldname": "student",
                    "fieldtype": "Link",
                    "label": "Student",
                    "options": "Student",
                    "insert_after": "column_break_zvdz",
                },
            ],
        }
        for doctype, fields in custom_fields.items():
            for field in fields:
                field["module"] = "Education"

        create_custom_fields(custom_fields, update=True)
