from frappe import _

app_name = "frappe_npo"
app_title = "Frappe NPO"
app_publisher = "Navari Ltd"
app_description = "Frappe Non Profit Organization"
app_email = "support@navari.co.ke"
app_license = "agpl-3.0"

# Apps
# ------------------

required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "frappe_npo",
# 		"logo": "/assets/frappe_npo/logo.png",
# 		"title": "Frappe NPO",
# 		"route": "/frappe_npo",
# 		"has_permission": "frappe_npo.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/frappe_npo/css/frappe_npo.css"
app_include_js = "/assets/frappe_npo/js/frappe_npo.js"

website_route_rules = [
    {"from_route": "/c/<path:app_path>", "to_route": "c"},
]
# include js, css files in header of web template
# web_include_css = "/assets/frappe_npo/css/frappe_npo.css"
# web_include_js = "/assets/frappe_npo/js/frappe_npo.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "frappe_npo/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Stock Entry": "overrides/stock_entry.js",
    "Sales Order": "overrides/sales_order.js",
    "Project": "overrides/project.js",
    "Payment Entry": "overrides/payment_entry.js",
    "Sales Person": "overrides/sales_person.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "frappe_npo/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "frappe_npo.utils.jinja_methods",
# 	"filters": "frappe_npo.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "frappe_npo.install.before_install"
after_install = "frappe_npo.install.after_install"
after_migrate = "frappe_npo.install.after_migrate"

# Uninstallation
# ------------

# before_uninstall = "frappe_npo.uninstall.before_uninstall"
# after_uninstall = "frappe_npo.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "frappe_npo.utils.before_app_install"
# after_app_install = "frappe_npo.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "frappe_npo.utils.before_app_uninstall"
# after_app_uninstall = "frappe_npo.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "frappe_npo.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "User": {
        "after_insert": "frappe_npo.beneficiaries.doctype.changemakers_user_profile.changemakers_user_profile.create_user_profile",
        "on_trash": [
            "frappe_npo.beneficiaries.doctype.changemakers_user_profile.changemakers_user_profile.delete_user_profile",
        ],
    },
    "ToDo": {
        "before_save": "frappe_npo.controllers.case.before_save",
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [
        "frappe_npo.non_profit.doctype.membership.membership.set_expired_status",
    ],
}

# Testing
# -------

before_tests = "frappe_npo.non_profit.utils.before_tests"

# Extend DocType Class
# ------------------------------

extend_doctype_class = {
    "Payment Entry": "frappe_npo.non_profit.custom_doctype.payment_entry.NonProfitPaymentEntry",
}

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "frappe_npo.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "frappe_npo.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["frappe_npo.utils.before_request"]
# after_request = ["frappe_npo.utils.after_request"]

# Job Events
# ----------
# before_job = ["frappe_npo.utils.before_job"]
# after_job = ["frappe_npo.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"frappe_npo.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


global_search_doctypes = {
    "Non Profit": [
        {"doctype": "Certified Consultant", "index": 1},
        {"doctype": "Certification Application", "index": 2},
        {"doctype": "Volunteer", "index": 3},
        {"doctype": "Membership", "index": 4},
        {"doctype": "Member", "index": 5},
        {"doctype": "Donor", "index": 6},
        {"doctype": "Chapter", "index": 7},
        {"doctype": "Grant Application", "index": 8},
        {"doctype": "Volunteer Type", "index": 9},
        {"doctype": "Donor Type", "index": 10},
        {"doctype": "Membership Type", "index": 11},
    ]
}

standard_portal_menu_items = [
    {
        "title": _("Certification"),
        "route": "/certification",
        "reference_doctype": "Certification Application",
        "role": "Non Profit Portal User",
    },
]

fixtures = [
    {
        "doctype": "Property Setter",
        "filters": [
            ["is_system_generated", "=", 0],
            ["module", "=", "Non Profit"],
        ],
    },
    "Custom HTML Block",
    "Case Type",
    "State",
    "Payment Type",
    {"dt": "Client Script", "filters": {"name": "Action: Create User Profile"}},
    {
        "dt": "Role",
        "filters": {
            "role_name": (
                "in",
                [
                    "Social Worker",
                    "Shelter Team Member",
                    "Healthcare Team Member",
                    "Food Team Member",
                    "SMT(NGO)-Field Co-ordinator",
                    "Medical Co-ordinator",
                    "Program Manager",
                    "Partner SMT",
                    "Data MIS/Documentation (Admin)",
                ],
            )
        },
    },
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "dt",
                "in",
                ("Project", "Stock Entry", "Budget", "Task", "Case"),
            ],
            ["is_system_generated", "=", 0],
            ["module", "=", "Beneficiaries"],
        ],
    },
]

accounting_dimension_doctypes = [
    "Beneficiary",
    "Donor",
    "Donation Allocation",
    "Donation Allocation Item",
    "Disbursement Order",
]
