import mysql.connector
from data import get_connection


def save_monthly_budget(user_id, monthly_limit, month, year):

    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            return False, "Database connection failed."

        cursor = connection.cursor()

        # Check whether budget already exists
        cursor.execute(
            """
            SELECT budget_id FROM budgets
            WHERE user_id = %s
            AND category_id IS NULL
            AND month = %s
            AND year = %s
            """,
            (user_id, month, year)
        )

        result = cursor.fetchone()

        if result:
            cursor.execute(
                """
                UPDATE budgets
                SET monthly_limit = %s
                WHERE budget_id = %s AND user_id = %s
                """,
                (monthly_limit, result[0], user_id)
            )
        else:
            cursor.execute(
                """
                INSERT INTO budgets
                (user_id, category_id, monthly_limit, month, year)
                VALUES (%s, NULL, %s, %s, %s)
                """,
                (user_id, monthly_limit, month, year)
            )

        connection.commit()

        return True, "Monthly budget saved successfully!"

    except mysql.connector.Error as e:
        return False, str(e)

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


def get_monthly_budget(user_id, month, year):

    connection = None
    cursor = None

    try:
        connection = get_connection()

        if connection is None:
            return False, "Database connection failed."

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT monthly_limit FROM budgets
            WHERE user_id = %s
            AND category_id IS NULL
            AND month = %s
            AND year = %s
            """,
            (user_id, month, year)
        )

        result = cursor.fetchone()

        if result:
            return True, float(result[0])

        return True, None

    except mysql.connector.Error as e:
        return False, str(e)

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()