
import mysql.connector
from datetime import date
from data import get_connection


def get_totals(user_id):

    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            return False, "Database connection failed."

        cursor = connection.cursor(dictionary=True)

        today = date.today()

        # First day of current month
        start_date = today.replace(day=1)

        # First day of next month
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1)
        else:
            end_date = date(today.year, today.month + 1, 1)

        query = """
            SELECT
                COALESCE(
                    SUM(CASE
                        WHEN transaction_type = 'Income'
                        THEN amount ELSE 0
                    END), 0
                ) AS total_income,

                COALESCE(
                    SUM(CASE
                        WHEN transaction_type = 'Expense'
                        THEN amount ELSE 0
                    END), 0
                ) AS total_expenses,

                COALESCE(
                    SUM(CASE
                        WHEN transaction_type = 'Expense'
                        AND transaction_date >= %s
                        AND transaction_date < %s
                        THEN amount ELSE 0
                    END), 0
                ) AS monthly_expenses

            FROM transactions
            WHERE user_id = %s
        """

        cursor.execute(
            query,
            (start_date, end_date, user_id)
        )

        result = cursor.fetchone()

        total_income = result["total_income"]
        total_expenses = result["total_expenses"]
        monthly_expenses = result["monthly_expenses"]

        available_balance = total_income - total_expenses

        totals = {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "available_balance": available_balance,
            "monthly_expenses": monthly_expenses
        }

        return True, totals

    except mysql.connector.Error as e:
        print("Calculation error:", e)
        return False, "Could not calculate totals."

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
