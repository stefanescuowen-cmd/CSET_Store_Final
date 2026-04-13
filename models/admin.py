def get_all_users(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()