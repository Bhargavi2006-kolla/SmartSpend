
import mysql.connector
import bcrypt
from data import get_connection


def register_user(name, email, password):
    connection = None
    cursor = None

    try:
        name = name.strip()
        email = email.strip().lower()

        if not name or not email or not password:
            return False, "All fields are required."

        if len(email) > 150:
            return False, "Email must be within 150 characters."

        if len(password.encode("utf-8")) > 72:
            return False, "Password is too long."

        # Hash the password before storing it
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        connection = get_connection()

        if connection is None:
            return False, "Database connection failed."

        cursor = connection.cursor()

        query = """
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
        """

        cursor.execute(query, (name, email, password_hash))
        connection.commit()

        return True, "Registration successful!"

    except mysql.connector.IntegrityError:
        if connection:
            connection.rollback()
        return False, "This email is already registered."

    except mysql.connector.Error as e:
        if connection:
            connection.rollback()
        print("Registration error:", e)
        return False, "Database error during registration."

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def login_user(email, password):
    connection = None
    cursor = None

    try:
        email = email.strip().lower()

        if not email or not password:
            return False, "Email and password are required."

        connection = get_connection()

        if connection is None:
            return False, "Database connection failed."

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT user_id, name, email, password_hash
            FROM users
            WHERE email = %s
        """

        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user is None:
            return False, "Invalid email or password."

        password_matches = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )

        if password_matches:
            user_data = {
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"]
            }

            return True, user_data

        return False, "Invalid email or password."

    except mysql.connector.Error as e:
        print("Login error:", e)
        return False, "Database error during login."

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
