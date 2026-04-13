def create_order(connection, customer_id):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO orders (customer_id, order_status) VALUES (%s, 'Pending')",
        (customer_id,)
    )
    connection.commit()
    return cursor.lastrowid


def add_order_item(connection, order_id, variant_id, quantity):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO order_items (order_id, variant_id, quantity, item_status)
        VALUES (%s, %s, %s, 'Pending')
    """, (order_id, variant_id, quantity))
    connection.commit()


def get_orders(connection, customer_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.order_id, p.title, oi.quantity, o.order_status
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN product_variants pv ON oi.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        WHERE o.customer_id = %s
    """, (customer_id,))
    return cursor.fetchall()