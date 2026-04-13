from sqlalchemy import text

def verify_user(connection, username_or_email, password):
    """Checks credentials and returns the user row if valid."""
    query = text("""
        SELECT user_id, name, username 
        FROM users 
        WHERE (username = :val OR email = :val) AND password = :pw
    """)
    result = connection.execute(query, {"val": username_or_email, "pw": password}).fetchone()
    return result # Returns a row or None



def user_exists(connection, email, username):
    """Checks if a user already exists in the system."""
    query = text("SELECT * FROM users WHERE email = :email OR username = :username")
    result = connection.execute(query, {"email": email, "username": username}).fetchone()
    return result is not None