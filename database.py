from sqlalchemy import text
import os

def register_new_user(connection, name, email, username, password, role):
    """Handles the multi-table insert for a new user."""
    try:
        # 1. Insert into the main USERS table
        user_query = text("""
            INSERT INTO users (name, email, username, password)
            VALUES (:name, :email, :username, :password)
        """)
        connection.execute(user_query, {
            "name": name, 
            "email": email, 
            "username": username, 
            "password": password
        })

        # 2. Get the ID of the user we just created
        user_id = connection.execute(text("SELECT LAST_INSERT_ID()")).scalar()

        # 3. Insert into the specific Role table
        if role == "customer":
            connection.execute(text("INSERT INTO customers (customer_id) VALUES (:id)"), {"id": user_id})
            # Since your schema requires a cart/wishlist for customers, create them now:
            connection.execute(text("INSERT INTO carts (customer_id) VALUES (:id)"), {"id": user_id})
            connection.execute(text("INSERT INTO wishlists (customer_id) VALUES (:id)"), {"id": user_id})
        
        elif role == "vendor":
            connection.execute(text("INSERT INTO vendors (vendor_id) VALUES (:id)"), {"id": user_id})
        
        # Commit the transaction (if not using autocommit)
        connection.commit()
        return True
    except Exception as e:
        print(f"Error during registration: {e}")
        connection.rollback()
        return False


def is_admin(connection, user_id):
    """Checks if the given user ID belongs to an admin."""
    query = text("SELECT * FROM admins WHERE admin_id = :id")
    result = connection.execute(query, {"id": user_id}).fetchone()
    return result is not None

def reset_database(connection, schema_file, seed_file):
    """Drops all tables and recreates them using provided SQL files."""
    try:
        # 1. Disable foreign key checks so we can drop tables in any order
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        
        # 2. Get all table names and drop them
        tables = connection.execute(text("SHOW TABLES;"))
        for (table_name,) in tables:
            connection.execute(text(f"DROP TABLE IF EXISTS {table_name};"))
        
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

        # 3. Helper to run SQL files
        def run_sql_file(filename):
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    # Split by semicolon to run statements one by one
                    commands = f.read().split(';')
                    for command in commands:
                        if command.strip():
                            connection.execute(text(command))

        run_sql_file(schema_file)
        run_sql_file(seed_file)
        
        connection.commit()
        return True
    except Exception as e:
        print(f"Reset Error: {e}")
        connection.rollback()
        return False