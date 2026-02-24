# Copyright (c) 2025, hussain@frappe.io and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, Sum


Budget = DocType("Budget")
MonthlyDistribution = DocType("Monthly Distribution")
BudgetAccount = DocType("Budget Account")
DonationAllocation = DocType("Donation Allocation")
DonationAllocationItem = DocType("Donation Allocation Item")


def execute(filters=None):
    """
    Main function to execute the report.
    """
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters=None):
    """
    Defines the columns for the report.
    """
    columns = [
        {
            "fieldname": "budget_name",
            "fieldtype": "Link",
            "label": "Budget",
            "options": "Budget",
            "width": 250,
        },
        {
            "fieldname": "budget_against",
            "fieldtype": "Data",
            "label": "Budget Against",
            "options": "Project",
            "width": 200,
        },
        {"fieldname": "name", "fieldtype": "Data", "label": "Name", "width": 200},
        {
            "fieldname": "budget_account",
            "fieldtype": "Link",
            "label": "Account",
            "options": "Account",
            "width": 200,
        },
        {
            "fieldname": "budget_amount",
            "fieldtype": "Currency",
            "label": "Budget Allocation",
            "width": 150,
        },
        {
            "fieldname": "donation_name",
            "fieldtype": "Link",
            "label": "Donation Allocation Doc",
            "options": "Donation Allocation",
            "width": 200,
        },
        {
            "fieldname": "donor",
            "fieldtype": "Link",
            "label": "Donor",
            "options": "Donor",
            "width": 200,
        },
        {
            "fieldname": "allocated_amount_item",
            "fieldtype": "Currency",
            "label": "Allocated Item Amount",
            "width": 150,
        },
        {
            "fieldname": "total_allocation_amount",
            "fieldtype": "Currency",
            "label": "Total Donation Allocated",
            "width": 150,
        },
        {
            "fieldname": "donation_total_paid_amount",
            "fieldtype": "Currency",
            "label": "Donation Total Paid",
            "width": 150,
        },
        {
            "fieldname": "donation_unallocated_balance",
            "fieldtype": "Currency",
            "label": "Donation Unallocated Balance",
            "width": 150,
        },
        {
            "fieldname": "total_donations",
            "fieldtype": "Currency",
            "label": "Total Donations (Budget)",
            "width": 150,
        },
        {
            "fieldname": "months_distributed",
            "fieldtype": "Int",
            "label": "Months Distributed",
            "width": 150,
        },
        {
            "fieldname": "percentage",
            "fieldtype": "Percent",
            "label": "Percentage (Monthly Avg.)",
            "width": 200,
        },
    ]

    sorted_months = _get_sorted_months_from_fiscal_years(filters)
    for month_label in sorted_months:
        columns.append(
            {
                "fieldname": frappe.scrub(month_label),
                "fieldtype": "Currency",
                "label": month_label,
                "width": 200,
            }
        )
    return columns


def _get_sorted_months_from_fiscal_years(filters=None):
    """
    Retrieves a sorted list of month labels (e.g., "January 2023") within the fiscal years specified by the filters.

    Args:
        filters (dict, optional): A dictionary of filters that may include:
            - "fiscal_year" (str): The name of a specific fiscal year to use.
            - "budget_name" (str): The name of a budget to filter fiscal years.

    Returns:
        list: A list of unique month labels, sorted chronologically, covering the range of the selected fiscal years.
    """
    fiscal_year_names = []
    if filters and filters.get("fiscal_year"):
        fiscal_year_names.append(filters["fiscal_year"])
    else:
        budget_fiscal_years_query = (
            frappe.qb.from_(Budget)
            .join(MonthlyDistribution)
            .on(Budget.monthly_distribution == MonthlyDistribution.name)
            .select(MonthlyDistribution.fiscal_year)
            .where(MonthlyDistribution.fiscal_year.isnotnull())
            .where(MonthlyDistribution.fiscal_year != "")
            .distinct()
        )
        if filters and filters.get("budget_name"):
            budget_fiscal_years_query = budget_fiscal_years_query.where(
                Budget.name == filters["budget_name"]
            )
        fiscal_year_names.extend(
            [fy[0] for fy in budget_fiscal_years_query.run(as_list=True)]
        )

    if not fiscal_year_names:
        return []

    unique_month_labels = set()
    month_datetime_map = {}

    for fy_name in list(set(fiscal_year_names)):
        fiscal_year_doc = frappe.get_cached_doc("Fiscal Year", fy_name)
        start_date = fiscal_year_doc.year_start_date
        end_date = fiscal_year_doc.year_end_date

        current_date = frappe.utils.getdate(start_date)
        end_date_obj = frappe.utils.getdate(end_date)

        while current_date <= end_date_obj:
            month_label = current_date.strftime("%B %Y")
            unique_month_labels.add(month_label)
            month_datetime_map[month_label] = current_date
            current_date = (current_date.replace(day=28) + timedelta(days=4)).replace(
                day=1
            )  # Move to next month's 1st day

    return sorted(list(unique_month_labels), key=lambda x: month_datetime_map[x])


def get_data(filters=None):
    """
    Retrieves and processes budget data for the report.
    """
    budgets = _get_filtered_budgets(filters)
    final_report_data = []
    fiscal_year_cache = {}

    sorted_months_labels = _get_sorted_months_from_fiscal_years(filters)
    allocation_month_empty_data = {
        frappe.scrub(month_label): "" for month_label in sorted_months_labels
    }

    for budget in budgets:
        fiscal_year_dates = _get_fiscal_year_dates(
            budget.fiscal_year, fiscal_year_cache
        )
        start_date = fiscal_year_dates["start_date"]
        end_date = fiscal_year_dates["end_date"]

        monthly_distribution_data = _get_monthly_distribution_data(
            budget.monthly_distribution, start_date, end_date
        )
        months_distributed = monthly_distribution_data["count"]
        distribution_dict_percentages = monthly_distribution_data["percentages"]

        total_budget_amount = _get_total_budget_amount(budget.budget_name)
        month_data_amounts = _calculate_monthly_allocated_amounts(
            total_budget_amount, distribution_dict_percentages
        )

        percentage_avg = 100 / months_distributed if months_distributed > 0 else 0
        budget_against_name = _get_budget_against_name(budget)

        current_budget_accounts_data = []  # To hold account rows
        current_budget_allocations_data = []  # To hold allocation item rows

        # Calculate total donations for the budget by summing `total_amount` from related Donation Allocation documents.
        total_donations_for_budget = _get_total_donations_for_budget_from_new_doctype(
            budget.budget_name
        )

        accounts = _get_budget_accounts(
            budget.budget_name,
            filters.get("budget_account") if filters else None,
        )

        for account in accounts:
            account_monthly_amounts = _calculate_monthly_allocated_amounts(
                account.budget_amount, distribution_dict_percentages
            )

            # --- Fetch Total Donations for Account from new Donation Allocation Item DocType ---
            total_donations_for_account = (
                _get_total_donations_for_account_from_new_doctype(
                    budget.budget_name, account.account
                )
            )

            current_budget_accounts_data.append(
                {
                    "budget_name": "",
                    "budget_against": "",
                    "name": "",
                    "budget_account": account.account,
                    "budget_amount": account.budget_amount,
                    "total_donations": "",  # Not applicable for account row as it's for budget
                    "months_distributed": "",
                    "percentage": "",
                    "donor": "",
                    "donation_name": "",
                    "allocated_amount_item": "",
                    "total_allocation_amount": "",
                    "donation_total_paid_amount": "",
                    "donation_unallocated_balance": "",
                    "indent": 1,  # Indent account rows under budget
                    **account_monthly_amounts,
                }
            )

            # --- Fetch and append Donation Allocation Item Rows ---
            allocation_items = _get_donation_allocation_items_for_account(
                budget.budget_name,
                account.account,
                filters.get("donation_allocation") if filters else None,
            )

            for item in allocation_items:
                current_budget_allocations_data.append(
                    {
                        "budget_name": "",
                        "budget_against": "",
                        "name": "",
                        "donor": item.donor,
                        "donation_name": item.donation_allocation_name,
                        "allocated_amount_item": item.amount,
                        "total_allocation_amount": item.total_amount,  # From parent Donation Allocation
                        "donation_total_paid_amount": item.donation_total_paid_amount,  # From parent
                        "donation_unallocated_balance": item.donation_unallocated_amount,  # From parent
                        "budget_account": "",
                        "budget_amount": "",
                        "total_donations": "",
                        "months_distributed": "",
                        "percentage": "",
                        "indent": 2,  # Indent allocation items under accounts
                        **allocation_month_empty_data,
                    }
                )

        final_report_data.append(
            {
                "budget_name": budget.budget_name,
                "budget_against": budget.budget_against,
                "name": budget_against_name,
                "budget_account": "",
                "budget_amount": total_budget_amount,
                "total_donations": total_donations_for_budget,
                "months_distributed": months_distributed,
                "percentage": percentage_avg,
                "donor": "",
                "donation_name": "",
                "allocated_amount_item": "",
                "total_allocation_amount": "",
                "donation_total_paid_amount": "",
                "donation_unallocated_balance": "",
                "indent": 0,  # Top-level budget rows
                **month_data_amounts,
            }
        )
        final_report_data.extend(current_budget_accounts_data)
        final_report_data.extend(current_budget_allocations_data)

    return final_report_data


def _get_filtered_budgets(filters):
    """
    Retrieve filtered budget records based on provided criteria.

    This function constructs and executes a query to fetch budget records from the database,
    joining with monthly distribution data and applying various filters. The filters can include
    fiscal year, budget type, employee, project, task, cost center, program, budget name, budget account,
    donor, donation allocation, and donation. The function supports dynamic filtering based on the
    'budget_against' type and links budgets to donation allocations via recipient relationships.

    Args:
        filters (dict): A dictionary containing filter criteria. Possible keys include:
            - 'fiscal_year' (str): Fiscal year to filter budgets.
            - 'budget_against' (str): Type of budget (e.g., 'Employee', 'Project', etc.).
            - 'employee' (str): Employee identifier (used if 'budget_against' is 'Employee').
            - 'project' (str): Project identifier (used if 'budget_against' is 'Project').
            - 'task' (str): Task identifier (used if 'budget_against' is 'Task').
            - 'cost_center' (str): Cost center identifier (used if 'budget_against' is 'Cost Center').
            - 'program' (str): Program identifier (used if 'budget_against' is 'Program').
            - 'budget_name' (str): Specific budget name to filter.
            - 'budget_account' (str): Account linked to the budget.
            - 'donor' (str): Donor identifier to filter budgets linked via donation allocations.
            - 'donation_allocation' (str): Donation allocation identifier.
            - 'donation' (str): Donation identifier.

    Returns:
        list[dict]: A list of dictionaries representing the filtered budget records, with fields such as
        budget name, budget type, employee, project, task, cost center, program, monthly distribution, and fiscal year.
    """
    budgets_query = (
        frappe.qb.from_(Budget)
        .left_join(MonthlyDistribution)
        .on(Budget.monthly_distribution == MonthlyDistribution.name)
        .select(
            Budget.name.as_("budget_name"),
            Budget.budget_against,
            Budget.employee,
            Budget.project,
            Budget.task,
            Budget.cost_center,
            Budget.program,
            Budget.monthly_distribution,
            MonthlyDistribution.fiscal_year,
        )
        .orderby(Budget.name)
    )

    if filters:
        if filters.get("fiscal_year"):
            budgets_query = budgets_query.where(
                MonthlyDistribution.fiscal_year == filters["fiscal_year"]
            )
        if filters.get("budget_against"):
            budgets_query = budgets_query.where(
                Budget.budget_against == filters["budget_against"]
            )

            budget_against_type = filters["budget_against"]
            if budget_against_type == "Employee" and filters.get("employee"):
                budgets_query = budgets_query.where(
                    Budget.employee == filters.get("employee")
                )
            elif budget_against_type == "Project" and filters.get("project"):
                budgets_query = budgets_query.where(
                    Budget.project == filters.get("project")
                )
            elif budget_against_type == "Task" and filters.get("task"):
                budgets_query = budgets_query.where(Budget.task == filters.get("task"))
            elif budget_against_type == "Cost Center" and filters.get("cost_center"):
                budgets_query = budgets_query.where(
                    Budget.cost_center == filters.get("cost_center")
                )
            elif budget_against_type == "Program" and filters.get("program"):
                budgets_query = budgets_query.where(
                    Budget.program == filters.get("program")
                )

        if filters.get("budget_name"):
            budgets_query = budgets_query.where(Budget.name == filters["budget_name"])

        if filters.get("budget_account"):
            budgets_with_account = (
                frappe.qb.from_(BudgetAccount)
                .select(BudgetAccount.parent)
                .where(BudgetAccount.account == filters["budget_account"])
                .where(BudgetAccount.parenttype == "Budget")
                .distinct()
            )
            budgets_query = budgets_query.where(Budget.name.isin(budgets_with_account))

        # --- Refactored filters for Donation Allocation DocType ---
        # A budget is linked via the 'recipient' dynamic link in Donation Allocation Item
        if filters.get("donor"):
            budgets_with_donor = (
                frappe.qb.from_(DonationAllocationItem)
                .join(DonationAllocation)
                .on(DonationAllocationItem.parent == DonationAllocation.name)
                .select(
                    DonationAllocationItem.recipient
                )  # Use 'recipient' for the budget name
                .where(DonationAllocationItem.recipient_type == "Budget")
                .where(DonationAllocation.donor == filters["donor"])
                .distinct()
            )
            budgets_query = budgets_query.where(Budget.name.isin(budgets_with_donor))

        if filters.get("donation_allocation"):
            budgets_with_donation_allocation = (
                frappe.qb.from_(DonationAllocationItem)
                .select(
                    DonationAllocationItem.recipient
                )  # Use 'recipient' for the budget name
                .where(DonationAllocationItem.recipient_type == "Budget")
                .where(DonationAllocationItem.parent == filters["donation_allocation"])
                .distinct()
            )
            budgets_query = budgets_query.where(
                Budget.name.isin(budgets_with_donation_allocation)
            )

        if filters.get("donation"):
            budgets_with_donation = (
                frappe.qb.from_(DonationAllocationItem)
                .select(
                    DonationAllocationItem.recipient
                )  # Use 'recipient' for the budget name
                .where(DonationAllocationItem.recipient_type == "Budget")
                .where(DonationAllocationItem.parent == filters["donation"])
                .distinct()
            )
            budgets_query = budgets_query.where(Budget.name.isin(budgets_with_donation))

    return budgets_query.run(as_dict=True)


def _get_donation_allocation_items_for_account(
    budget_name, account_name, filter_allocation_name=None
):
    """
    Retrieve donation allocation items for a specific budget and account.

    This function queries the DonationAllocationItem and DonationAllocation tables to fetch allocation details
    where the recipient type is "Budget", the recipient matches the given budget name, and the account matches
    the given account name. Optionally, it can filter by a specific donation allocation name.

    Args:
        budget_name (str): The name of the budget to filter allocations.
        account_name (str): The name of the account to filter allocations.
        filter_allocation_name (str, optional): If provided, filters allocations by this specific allocation name.

    Returns:
        list[dict]: A list of dictionaries containing allocation details, including parent allocation name,
                    amount, account, donor, total amount, total paid amount, and unallocated amount.
    """

    allocations_query = (
        frappe.qb.from_(DonationAllocationItem)
        .left_join(DonationAllocation)
        .on(DonationAllocationItem.parent == DonationAllocation.name)
        .select(
            DonationAllocationItem.parent.as_("donation_allocation_name"),
            DonationAllocationItem.amount,
            DonationAllocationItem.account,
            DonationAllocation.donor,
            DonationAllocation.total_amount,
            DonationAllocation.donation_total_paid_amount,
            DonationAllocation.donation_unallocated_amount,
        )
        .where(DonationAllocationItem.recipient_type == "Budget")
        .where(DonationAllocationItem.recipient == budget_name)
        .where(DonationAllocationItem.account == account_name)
    )
    if filter_allocation_name:
        allocations_query = allocations_query.where(
            DonationAllocationItem.parent == filter_allocation_name
        )
    return allocations_query.run(as_dict=True)


def _get_fiscal_year_dates(fiscal_year_name, fiscal_year_cache):
    """Retrieves and caches fiscal year start and end dates."""
    if not fiscal_year_name:
        return {"start_date": None, "end_date": None}

    if fiscal_year_name not in fiscal_year_cache:
        fiscal_year_doc = frappe.get_cached_doc("Fiscal Year", fiscal_year_name)
        fiscal_year_cache[fiscal_year_name] = {
            "start_date": fiscal_year_doc.year_start_date,
            "end_date": fiscal_year_doc.year_end_date,
        }
    return fiscal_year_cache[fiscal_year_name]


def _get_monthly_distribution_data(
    monthly_distribution_name, fiscal_year_start_date, fiscal_year_end_date
):
    """
    Retrieves and processes monthly distribution percentage data for a given distribution name within a fiscal year.

    Args:
        monthly_distribution_name (str): The name of the monthly distribution to fetch data for.
        fiscal_year_start_date (str or datetime.date): The start date of the fiscal year.
        fiscal_year_end_date (str or datetime.date): The end date of the fiscal year.

    Returns:
        dict: A dictionary containing:
            - "count" (int): The number of months distributed.
            - "percentages" (dict): A mapping of scrubbed month labels (optionally including year)
              to their corresponding percentage allocation values.

    Notes:
        - Month labels are formatted as "<Month> <Year>" if fiscal year dates are provided and matched.
        - If a month name is invalid or its year cannot be determined, errors are logged using frappe.log_error.
        - The function expects the existence of a DocType named "Monthly Distribution Percentage" and uses Frappe's query builder.
    """
    MonthlyDistributionPercentage = DocType("Monthly Distribution Percentage")

    months_distributed_count = (
        frappe.qb.from_(MonthlyDistributionPercentage)
        .select(Count("*").as_("cnt"))
        .where(MonthlyDistributionPercentage.parent == monthly_distribution_name)
    ).run(as_dict=True)[0]["cnt"] or 0

    distribution_rows = (
        frappe.qb.from_(MonthlyDistributionPercentage)
        .select(
            MonthlyDistributionPercentage.month,
            MonthlyDistributionPercentage.percentage_allocation,
        )
        .where(MonthlyDistributionPercentage.parent == monthly_distribution_name)
        .orderby(MonthlyDistributionPercentage.month)
    ).run(as_dict=True)

    distribution_dict_percentages = {}

    for row in distribution_rows:
        month_label = row["month"]
        if fiscal_year_start_date and fiscal_year_end_date:
            try:
                month_number = datetime.strptime(row["month"], "%B").month
                current_fy_date = frappe.utils.getdate(fiscal_year_start_date)
                fy_end_date_obj = frappe.utils.getdate(fiscal_year_end_date)
                found_year = None
                while current_fy_date <= fy_end_date_obj:
                    if current_fy_date.month == month_number:
                        found_year = current_fy_date.year
                        break
                    current_fy_date = (
                        current_fy_date.replace(day=28) + timedelta(days=4)
                    ).replace(day=1)
                if found_year:
                    month_label = f"{row['month']} {found_year}"
                else:
                    frappe.log_error(
                        f"Could not determine year for month '{row['month']}' in Fiscal Year.",
                        "Month Year Mismatch",
                    )
            except ValueError:
                frappe.log_error(
                    f"Invalid month name '{row['month']}' in Monthly Distribution Percentage.",
                    "Invalid Month Name Format",
                )
        distribution_dict_percentages[frappe.scrub(month_label)] = row[
            "percentage_allocation"
        ]

    return {
        "count": months_distributed_count,
        "percentages": distribution_dict_percentages,
    }


def _get_total_budget_amount(budget_name):
    """
    Calculate and return the total budget amount for a given budget name.

    Args:
        budget_name (str): The name of the budget to retrieve the total amount for.

    Returns:
        float: The total budget amount associated with the specified budget name. Returns 0 if no amount is found.
    """
    total_budget_amount_result = (
        frappe.qb.from_(BudgetAccount)
        .select(Sum(BudgetAccount.budget_amount).as_("total_amount"))
        .where(BudgetAccount.parent == budget_name)
        .where(BudgetAccount.parenttype == "Budget")
    ).run(as_dict=True)
    return total_budget_amount_result[0]["total_amount"] or 0


def _calculate_monthly_allocated_amounts(base_amount, distribution_percentages):
    """
    Calculates the allocated amounts for each month based on a base amount and distribution percentages.

    Args:
        base_amount (float): The total amount to be distributed across months.
        distribution_percentages (dict): A dictionary where keys are month labels and values are the percentage of the base amount to allocate to each month.

    Returns:
        dict: A dictionary mapping each month label to its allocated amount.
    """
    month_data_amounts = {}
    for month_label_scrubbed, percentage_value in distribution_percentages.items():
        month_data_amounts[month_label_scrubbed] = (
            percentage_value / 100
        ) * base_amount
    return month_data_amounts


def _get_budget_against_name(budget):
    """
    Retrieves the display name associated with a budget's "budget_against" entity.

    Depending on the type specified in `budget.budget_against`, this function looks up
    the corresponding document (such as Employee, Project, Task, Cost Center, or Program)
    and returns its display name field (e.g., first_name, project_name, subject, or name).

    Args:
        budget (dict or object): The budget record containing the "budget_against" type and
            the relevant document identifier.

    Returns:
        str: The display name of the associated entity, or an empty string if not found.
    """
    name_field_map = {
        "Employee": "first_name",
        "Project": "project_name",
        "Task": "subject",
        "Cost Center": "name",
        "Program": "name",
    }
    doctype_map = {
        "Employee": "Employee",
        "Project": "Project",
        "Task": "Task",
        "Cost Center": "Cost Center",
        "Program": "Program",
    }

    budget_against_type = budget.budget_against
    if budget_against_type and budget.get(
        budget_against_type.lower().replace(" ", "_")
    ):
        doc_name = budget.get(budget_against_type.lower().replace(" ", "_"))
        field_name = name_field_map.get(budget_against_type)
        doctype_name = doctype_map.get(budget_against_type)
        if doc_name and field_name and doctype_name:
            return frappe.db.get_value(doctype_name, doc_name, field_name)
    return ""


def _get_total_donations_for_budget_from_new_doctype(budget_name):
    """
    Calculate the total donated amount for a specific budget from the new DonationAllocation doctype.

    Args:
        budget_name (str): The name of the budget to retrieve total donations for.

    Returns:
        float: The total donated amount for the specified budget. Returns 0 if no donations are found.
    """
    total_donations_result = (
        frappe.qb.from_(DonationAllocationItem)
        .join(DonationAllocation)
        .on(DonationAllocationItem.parent == DonationAllocation.name)
        .select(Sum(DonationAllocation.total_amount).as_("total_donated_amount"))
        .where(DonationAllocationItem.recipient_type == "Budget")
        .where(DonationAllocationItem.recipient == budget_name)
    ).run(as_dict=True)

    return total_donations_result[0]["total_donated_amount"] or 0


def _get_budget_accounts(budget_name, filter_account=None):
    """
    Retrieve budget account details for a given budget.

    Args:
        budget_name (str): The name of the budget to fetch accounts for.
        filter_account (str, optional): If provided, only fetch details for this specific account.

    Returns:
        list[dict]: A list of dictionaries containing 'account' and 'budget_amount' for each matching budget account.
    """
    accounts_query = (
        frappe.qb.from_(BudgetAccount)
        .select(
            BudgetAccount.account,
            BudgetAccount.budget_amount,
        )
        .where(BudgetAccount.parent == budget_name)
        .where(BudgetAccount.parenttype == "Budget")
    )

    if filter_account:
        accounts_query = accounts_query.where(BudgetAccount.account == filter_account)

    return accounts_query.run(as_dict=True)


def _get_total_donations_for_account_from_new_doctype(budget_name, account_name):
    """
    Calculate the total donated amount for a specific account and budget from the DonationAllocationItem doctype.

    Args:
        budget_name (str): The name of the budget to filter donations by.
        account_name (str): The name of the account to filter donations by.

    Returns:
        float: The total donated amount for the specified account and budget. Returns 0 if no donations are found.
    """
    total_donations_account_result = (
        frappe.qb.from_(DonationAllocationItem)
        .select(
            Sum(DonationAllocationItem.amount).as_("total_donated_amount_for_account")
        )
        .where(DonationAllocationItem.recipient_type == "Budget")
        .where(DonationAllocationItem.recipient == budget_name)
        .where(DonationAllocationItem.account == account_name)
    ).run(as_dict=True)

    return total_donations_account_result[0]["total_donated_amount_for_account"] or 0
