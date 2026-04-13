# This is where we will convert the products table into a python file to be used in our application.

def get_all_products(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            p.product_id,
            p.title,
            p.description,
            p.price,
            p.discount_price,
            MIN(pi.image_url) AS image,
            SUM(v.stock) AS stock
        FROM products p
        LEFT JOIN product_images pi ON p.product_id = pi.product_id
        LEFT JOIN product_variants v ON p.product_id = v.product_id
        GROUP BY p.product_id
    """)
    return cursor.fetchall()


def get_product_by_id(connection, product_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE product_id=%s", (product_id,))
    return cursor.fetchone()


def search_products(connection, term):
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM products WHERE title LIKE %s OR description LIKE %s",
        (f"%{term}%", f"%{term}%")
    )
    return cursor.fetchall()