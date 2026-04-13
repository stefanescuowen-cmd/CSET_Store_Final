# This is where we will convert the wishlist table into a python file to be used in our application.

def get_wishlist(connection, customer_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT wi.variant_id
        FROM wishlist_items wi
        JOIN wishlists w ON wi.wishlist_id = w.wishlist_id
        WHERE w.customer_id = %s
    """, (customer_id,))
    return cursor.fetchall()


def add_to_wishlist(connection, customer_id, variant_id):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO wishlist_items (wishlist_id, variant_id)
        SELECT wishlist_id, %s FROM wishlists WHERE customer_id = %s
    """, (variant_id, customer_id))
    connection.commit()