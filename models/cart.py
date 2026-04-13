# This is where we will convert the cart table into a python file to be used in our application.

def get_cart_items(connection, customer_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.title, ci.quantity, pv.variant_id
        FROM carts c
        JOIN cart_items ci ON c.cart_id = ci.cart_id
        JOIN product_variants pv ON ci.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        WHERE c.customer_id = %s
    """, (customer_id,))
    return cursor.fetchall()


def add_to_cart(connection, cart_id, variant_id, quantity):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO cart_items (cart_id, variant_id, quantity)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE quantity = quantity + %s
    """, (cart_id, variant_id, quantity, quantity))
    connection.commit()


def remove_from_cart(connection, cart_id, variant_id):
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM cart_items WHERE cart_id=%s AND variant_id=%s",
        (cart_id, variant_id)
    )
    connection.commit()