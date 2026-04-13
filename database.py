from sqlalchemy import text
import os

class DatabaseManager:
    def __init__(self, connection):
        self.conn = connection

    def user_exists(self, email, username):
        """Checks if a user already exists in the system."""
        query = text("SELECT * FROM users WHERE email = :email OR username = :username")
        result = self.conn.execute(query, {"email": email, "username": username}).fetchone()
        return result is not None

    def register_new_user(self, name, email, username, password, role):
        """Handles the multi-table insert for a new user."""
        try:
            # 1. Insert into the main USERS table
            user_query = text("""
                INSERT INTO users (name, email, username, password)
                VALUES (:name, :email, :username, :password)
            """)
            self.conn.execute(user_query, {
                "name": name, 
                "email": email, 
                "username": username, 
                "password": password
            })

            # 2. Get the ID of the user we just created
            user_id = self.conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

            # 3. Insert into the specific Role table
            if role == "customer":
                self.conn.execute(text("INSERT INTO customers (customer_id) VALUES (:id)"), {"id": user_id})
                # Since your schema requires a cart/wishlist for customers, create them now:
                self.conn.execute(text("INSERT INTO carts (customer_id) VALUES (:id)"), {"id": user_id})
                self.conn.execute(text("INSERT INTO wishlists (customer_id) VALUES (:id)"), {"id": user_id})
            
            elif role == "vendor":
                self.conn.execute(text("INSERT INTO vendors (vendor_id) VALUES (:id)"), {"id": user_id})
            
            # Commit the transaction (if not using autocommit)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error during registration: {e}")
            self.conn.rollback()
            return False
    
    def verify_user(self, username_or_email, password):
        """Checks credentials and returns the user row if valid."""
        query = text("""
            SELECT user_id, name, username 
            FROM users 
            WHERE (username = :val OR email = :val) AND password = :pw
        """)
        result = self.conn.execute(query, {"val": username_or_email, "pw": password}).fetchone()
        return result # Returns a row or None
    
    def is_admin(self, user_id):
        """Checks if the given user ID belongs to an admin."""
        query = text("SELECT * FROM admins WHERE admin_id = :id")
        result = self.conn.execute(query, {"id": user_id}).fetchone()
        return result is not None
    
    def reset_database(self, schema_file, seed_file):
        """Drops all tables and recreates them using provided SQL files."""
        try:
            # 1. Disable foreign key checks so we can drop tables in any order
            self.conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            
            # 2. Get all table names and drop them
            tables = self.conn.execute(text("SHOW TABLES;"))
            for (table_name,) in tables:
                self.conn.execute(text(f"DROP TABLE IF EXISTS {table_name};"))
            
            self.conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

            # 3. Helper to run SQL files
            def run_sql_file(filename):
                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        # Split by semicolon to run statements one by one
                        commands = f.read().split(';')
                        for command in commands:
                            if command.strip():
                                self.conn.execute(text(command))

            run_sql_file(schema_file)
            run_sql_file(seed_file)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Reset Error: {e}")
            self.conn.rollback()
            return False