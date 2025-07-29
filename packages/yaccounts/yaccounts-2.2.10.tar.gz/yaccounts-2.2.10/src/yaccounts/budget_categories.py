import enum


class AccountCategory(enum.Enum):
    """Enum for account categories."""

    BENEFITS = "Benefits"
    INDIRECT_COSTS = "Indirect Costs"
    SUPPLIES = "Supplies"
    WAGES = "Wages"
    STUDENT_AID = "Student Aid"
    TRAVEL = "Travel"
    UNALLOCATED = "Unallocated"
    CAPITAL = "Capital Equipment"
    CONTRACT_SERVICES = "Contract Services"



def budget_category_to_enum(category):
    """Convert a workday category to an AccountCategory enum."""
    lookup = {
        "BYU Grants: Benefits": AccountCategory.BENEFITS,
        "BYU Grants: Indirect Costs": AccountCategory.INDIRECT_COSTS,
        "BYU Grants: Materials and Supplies": AccountCategory.SUPPLIES,
        "BYU Grants: Salaries and Wages": AccountCategory.WAGES,
        "BYU Grants: Student Aid": AccountCategory.STUDENT_AID,
        "BYU Grants: Travel": AccountCategory.TRAVEL,
        "BYU Grants: Unallocated": AccountCategory.UNALLOCATED,
        "BYU Grants: Capital Equipment": AccountCategory.CAPITAL,
        "BYU Grants: Contract Services": AccountCategory.CONTRACT_SERVICES
    }
    if category in lookup:
        return lookup[category]
    else:
        raise ValueError(f"Unknown category: {category}. Please update the lookup.")


class BudgetType(enum.Enum):
    """Enum for budget types."""

    ACTUALS = 0
    BUDGET = 1
    ACTUALS_YTD = 2
    ACTUALS_PREV = 3
