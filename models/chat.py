# This is where we will convert the chat table into a python file to be used in our application.

def send_message(connection, customer_id, vendor_id, admin_id, text):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO chats (customer_id, vendor_id, admin_id, text)
        VALUES (%s, %s, %s, %s)
    """, (customer_id, vendor_id, admin_id, text))
    connection.commit()


def get_messages_by_customer(connection, customer_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM chats WHERE customer_id=%s",
        (customer_id,)
    )
    return cursor.fetchall()