import pandas as pd
import plotly.express as px

from expense_logic import get_transactions

from data import get_connection

print("SmartSpend Analytics Started!")

def get_category_totals(user_id):

    success, transactions = get_transactions(user_id)

    if not success:
        return None

    if not transactions:
        return pd.DataFrame(
            columns=["category_name", "total_spent"]
        )

    df = pd.DataFrame(transactions)

    expenses = df[
        df["transaction_type"] == "Expense"
    ]

    result = (
        expenses.groupby("category_name")["amount"]
        .sum()
        .reset_index()
    )

    result.columns = ["category_name", "total_spent"]

    return result

def get_monthly_totals(user_id):

    success, transactions = get_transactions(user_id)

    if not success:
        return None

    if not transactions:
        return pd.DataFrame(
            columns=["year", "month", "total_expenses"]
        )

    df = pd.DataFrame(transactions)

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"]
    )

    expenses = df[
        df["transaction_type"] == "Expense"
    ].copy()

    expenses["year"] = expenses["transaction_date"].dt.year
    expenses["month"] = expenses["transaction_date"].dt.month

    result = (
        expenses.groupby(["year", "month"])["amount"]
        .sum()
        .reset_index()
    )

    result.columns = ["year", "month", "total_expenses"]

    return result

def get_income_expense_totals(user_id):

    success, transactions = get_transactions(user_id)

    if not success:
        return None

    if not transactions:
        return {
            "total_income": 0,
            "total_expenses": 0
        }

    df = pd.DataFrame(transactions)

    income = df[
        df["transaction_type"] == "Income"
    ]["amount"].sum()

    expenses = df[
        df["transaction_type"] == "Expense"
    ]["amount"].sum()

    return {
        "total_income": income,
        "total_expenses": expenses
    }

def create_category_chart(user_id):

    data = get_category_totals(user_id)

    if data is None or data.empty:
        return None

    fig = px.pie(
        data,
        names="category_name",
        values="total_spent",
        title="Category-wise Expenses"
    )

    return fig

def create_monthly_chart(user_id):

    data = get_monthly_totals(user_id)

    if data is None or data.empty:
        return None

    data["period"] = (
        data["year"].astype(str)
        + "-"
        + data["month"].astype(str).str.zfill(2)
    )

    fig = px.bar(
        data,
        x="period",
        y="total_expenses",
        title="Monthly Expenses",
        labels={
            "period": "Month",
            "total_expenses": "Total Expenses"
        }
    )

    return fig

def get_budget_data(user_id):

    connection = get_connection()

    if connection is None:
        return None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                c.category_name,
                b.monthly_limit,
                b.month,
                b.year
            FROM budgets b
            JOIN categories c
            ON b.category_id = c.category_id
            WHERE b.user_id = %s
        """

        cursor.execute(query, (user_id,))
        budgets = cursor.fetchall()

        return pd.DataFrame(
    budgets,
    columns=[
        "category_name",
        "monthly_limit",
        "month",
        "year"
    ]
)

    except Exception as e:
        print("Budget retrieval error:", e)
        return None

    finally:
        if connection:
            cursor.close()
            connection.close()

def get_budget_comparison(user_id, month, year):

    budgets = get_budget_data(user_id)

    if budgets is None:
         return None

    if budgets.empty:
        return pd.DataFrame(
            columns=[
                "category_name",
                "monthly_limit",
                "actual_expense",
                "remaining_budget"
            ]
        )

    success, transactions = get_transactions(user_id)

    if not success:
        return None

    if transactions:
        df = pd.DataFrame(transactions)

        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"]
        )

        expenses = df[
            (df["transaction_type"] == "Expense") &
            (df["transaction_date"].dt.month == month) &
            (df["transaction_date"].dt.year == year)
        ]

        actual = (
            expenses.groupby("category_name")["amount"]
            .sum()
            .reset_index()
        )

        actual.columns = ["category_name", "actual_expense"]

    else:
        actual = pd.DataFrame(
            columns=["category_name", "actual_expense"]
        )

    budgets = budgets[
        (budgets["month"] == month) &
        (budgets["year"] == year)
    ]

    result = budgets.merge(
        actual,
        on="category_name",
        how="left"
    )

    result["actual_expense"] = (
        result["actual_expense"].fillna(0)
    )

    result["remaining_budget"] = (
        result["monthly_limit"] - result["actual_expense"]
    )

    return result

if __name__ == "__main__":

    result = get_category_totals(1)
    print("Category-wise Expenses:")
    print(result)

    monthly = get_monthly_totals(1)
    print("Monthly Expenses:")
    print(monthly)

    summary = get_income_expense_totals(1)

    print("Income vs Expense:")
    print(summary)

    chart = create_category_chart(1)

    if chart is not None:
        chart.show()
    else:
        print("No category expenses available for pie chart.")

        monthly_chart = create_monthly_chart(1)

    if monthly_chart is not None:
        monthly_chart.show()
    else:
        print("No monthly expenses available for bar chart.")

        budgets = get_budget_data(1)

    print("Budget Details:")
    print(budgets)

    from datetime import date

    today = date.today()

    comparison = get_budget_comparison(
        1,
        today.month,
        today.year
    )

    print("Budget vs Actual Expense:")
    print(comparison)