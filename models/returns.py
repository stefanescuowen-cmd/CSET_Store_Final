# This is where we will convert the returns table into a python file to be used in our application.

def create_return(connection, title, description, demand, customer_id, order_id, variant_id):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO returns (title, description, demand, status, customer_id, order_id, variant_id)
        VALUES (%s, %s, %s, 'Pending', %s, %s, %s)
    """, (title, description, demand, customer_id, order_id, variant_id))
    connection.commit()


def get_returns(connection, customer_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM returns WHERE customer_id=%s",
        (customer_id,)
    )
    return cursor.fetchall()