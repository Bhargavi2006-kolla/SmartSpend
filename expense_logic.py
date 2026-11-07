
import mysql.connector
from decimal import Decimal, InvalidOperation
from datetime import date
from data import get_connection


def validate_transaction(category_id, transaction_type, amount,
                         description, transaction_date):

    transaction_type = str(transaction_type).strip().title()

    if transaction_type not in ("Income", "Expense"):
        raise ValueError("Type must be Income or Expense.")

    try:
        amount = Decimal(str(amount))
    except InvalidOperation:
        raise ValueError("Enter a valid amount.")

    if not amount.is_finite() or amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if amount > Decimal("99999999.99"):
        raise ValueError("Amount is too large.")

    if amount.as_tuple().exponent < -2:
        raise ValueError("Amount can have at most 2 decimal places.")

    if not isinstance(category_id, int) or isinstance(category_id, bool):
        raise ValueError("Invalid category ID.")

    description = str(description or "").strip()

    if len(description) > 255:
        raise ValueError("Description must be within 255 characters.")

    if isinstance(transaction_date, str):
        try:
            transaction_date = date.fromisoformat(transaction_date)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")

    if not isinstance(transaction_date, date):
        raise ValueError("Invalid transaction date.")

    return category_id, transaction_type, amount, description, transaction_date


def add_transaction(user_id, category_id, transaction_type,
                    amount, description, transaction_date):

    connection = None
    cursor = None

    try:
        values = validate_transaction(
            category_id, transaction_type, amount,
            description, transaction_date
        )

        category_id, transaction_type, amount, description, transaction_date = values

        connection = get_connection()
        if connection is None:
            return False, "Database connection failed."

        cursor = connection.cursor()

        cursor.execute(
            "SELECT category_id FROM categories WHERE category_id = %s",
            (category_id,)
        )

        if cursor.fetchone() is None:
            return False, "Category does not exist."

        query = """
            INSERT INTO transactions
            (user_id, category_id, transaction_type, amount,
             description, transaction_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            user_id, category_id, transaction_type,
            amount, description, transaction_date
        ))

        connection.commit()
        return True, "Transaction added successfully!"

    except (ValueError, TypeError) as e:
        return False, str(e)

    except mysql.connector.Error as e:
        if connection:
            connection.rollback()
        print("Add transaction error:", e)
        return False, "Could not add transaction."

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_transactions(user_id):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        if connection is None:
            return False, "Database connection failed."

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT t.transaction_id, t.user_id, t.category_id,
                   c.category_name, t.transaction_type,
                   t.amount, t.description, t.transaction_date
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.user_id = %s
            ORDER BY t.transaction_date DESC
        """

        cursor.execute(query, (user_id,))
        transactions = cursor.fetchall()

        return True, transactions

    except mysql.connector.Error as e:
        print("View transactions error:", e)
        return False, "Could not retrieve transactions."

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def update_transaction(transaction_id, user_id, category_id,
                       transaction_type, amount, description,
                       transaction_date):

    connection = None
    cursor = None

    try:
        values = validate_transaction(
            category_id, transaction_type, amount,
            description, transaction_date
        )

        category_id, transaction_type, amount, description, transaction_date = values

        connection = get_connection()
        if connection is None:
            return False, "Database connection failed."

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT transaction_id FROM transactions
            WHERE transaction_id = %s AND user_id = %s
            """,
            (transaction_id, user_id)
        )

        if cursor.fetchone() is None:
            return False, "Transaction not found."

        cursor.execute(
            "SELECT category_id FROM categories WHERE category_id = %s",
            (category_id,)
        )

        if cursor.fetchone() is None:
            return False, "Category does not exist."

        query = """
            UPDATE transactions
            SET category_id = %s, transaction_type = %s,
                amount = %s, description = %s,
                transaction_date = %s
            WHERE transaction_id = %s AND user_id = %s
        """

        cursor.execute(query, (
            category_id, transaction_type, amount,
            description, transaction_date,
            transaction_id, user_id
        ))

        connection.commit()
        return True, "Transaction updated successfully!"

    except (ValueError, TypeError) as e:
        return False, str(e)

    except mysql.connector.Error as e:
        if connection:
            connection.rollback()
        print("Update transaction error:", e)
        return False, "Could not update transaction."

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def delete_transaction(transaction_id, user_id):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        if connection is None:
            return False, "Database connection failed."

        cursor = connection.cursor()

        query = """
            DELETE FROM transactions
            WHERE transaction_id = %s AND user_id = %s
        """

        cursor.execute(query, (transaction_id, user_id))

        if cursor.rowcount == 0:
            connection.rollback()
            return False, "Transaction not found."

        connection.commit()
        return True, "Transaction deleted successfully!"

    except mysql.connector.Error as e:
        if connection:
            connection.rollback()
        print("Delete transaction error:", e)
        return False, "Could not delete transaction."

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
