def get_vendor_products(connection, vendor_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM products WHERE vendor_id=%s",
        (vendor_id,)
    )
    return cursor.fetchall()