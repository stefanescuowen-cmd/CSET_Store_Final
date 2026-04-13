# This is where we will convert the reviews table into a python file to be used in our application.

def add_review(connection, variant_id, customer_id, rating, description):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO reviews (variant_id, customer_id, rating, description)
        VALUES (%s, %s, %s, %s)
    """, (variant_id, customer_id, rating, description))
    connection.commit()


def get_reviews_for_product(connection, variant_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.rating, r.description, r.date, u.name
        FROM reviews r
        JOIN users u ON r.customer_id = u.user_id
        WHERE r.variant_id = %s
    """, (variant_id,))
    return cursor.fetchall()