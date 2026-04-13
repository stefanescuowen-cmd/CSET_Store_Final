from sqlalchemy import text

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