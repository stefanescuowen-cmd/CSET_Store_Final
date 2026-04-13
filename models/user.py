def get_user_by_email_or_username(connection, email, username):
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users WHERE email=%s OR username=%s",
        (email, username)
    )
    return cursor.fetchone()


def create_user(connection, name, email, username, password):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, username, password) VALUES (%s,%s,%s,%s)",
        (name, email, username, password)
    )
    connection.commit()


def login_user(connection, username, password):
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    return cursor.fetchone()