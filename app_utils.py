from sqlalchemy import text

def get_user_role(connection, user_id):
    if not user_id:
        return None

    result = connection.execute(
        text("""
        SELECT 'admin' AS role
        FROM admins
        WHERE admin_id = :id

        UNION ALL

        SELECT 'vendor'
        FROM vendors
        WHERE user_id = :id

        UNION ALL

        SELECT 'customer'
        FROM customers
        WHERE customer_id = :id

        LIMIT 1
        """),
        {"id": user_id}
    ).mappings().first()

    return result["role"] if result else None
