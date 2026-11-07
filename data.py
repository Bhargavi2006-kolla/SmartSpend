import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Bhargavi@2006",
        database="smartspend"
    )
    return connection
def test_connection():
    try:
        connection = get_connection()
        print("SmartSpend Database Connected Successfully!")
        connection.close()

    except Exception as e:
        print("Connection Failed:", e)


if __name__ == "__main__":
    test_connection()