from sqlalchemy import text


def get_user_role(connection, user_id):
    if not user_id:
        return None

    result = connection.execute(
        text("""
        SELECT
            CASE
                WHEN EXISTS (SELECT 1 FROM admins WHERE admin_id = :id) THEN 'admin'
                WHEN EXISTS (SELECT 1 FROM vendors WHERE user_id = :id) THEN 'vendor'
                WHEN EXISTS (SELECT 1 FROM customers WHERE customer_id = :id) THEN 'customer'
                ELSE NULL
            END AS role
        """),
        {"id": user_id}
    ).mappings().first()

    return result["role"] if result else None
