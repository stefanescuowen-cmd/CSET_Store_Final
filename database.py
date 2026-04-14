from sqlalchemy import text
import os

# =====
# ADMIN
# =====

def get_all_users(connection):
    result = connection.execute(text("SELECT * FROM users"))
    return result.mappings().all()


# ====
# CART
# ====

def get_cart_items(connection, customer_id):
    query = text("""
        SELECT p.title, ci.quantity, pv.variant_id
        FROM carts c
        JOIN cart_items ci ON c.cart_id = ci.cart_id
        JOIN product_variants pv ON ci.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        WHERE c.customer_id = :customer_id
    """)
    result = connection.execute(query, {"customer_id": customer_id})
    return result.mappings().all()


def add_to_cart(connection, cart_id, variant_id, quantity):
    query = text("""
        INSERT INTO cart_items (cart_id, variant_id, quantity)
        VALUES (:cart_id, :variant_id, :quantity)
        ON DUPLICATE KEY UPDATE quantity = quantity + :quantity
    """)
    connection.execute(query, {
        "cart_id": cart_id,
        "variant_id": variant_id,
        "quantity": quantity
    })
    connection.commit()


def remove_from_cart(connection, cart_id, variant_id):
    query = text("""
        DELETE FROM cart_items 
        WHERE cart_id = :cart_id AND variant_id = :variant_id
    """)
    connection.execute(query, {
        "cart_id": cart_id,
        "variant_id": variant_id
    })
    connection.commit()


# ====
# CHAT
# ====

def send_message(connection, customer_id, vendor_id, admin_id, text_msg):
    query = text("""
        INSERT INTO chats (customer_id, vendor_id, admin_id, text)
        VALUES (:customer_id, :vendor_id, :admin_id, :text)
    """)
    connection.execute(query, {
        "customer_id": customer_id,
        "vendor_id": vendor_id,
        "admin_id": admin_id,
        "text": text_msg
    })
    connection.commit()


def get_messages_by_customer(connection, customer_id):
    query = text("SELECT * FROM chats WHERE customer_id = :customer_id")
    result = connection.execute(query, {"customer_id": customer_id})
    return result.mappings().all()


# ======
# ORDERS
# ======

def create_order(connection, customer_id):
    query = text("""
        INSERT INTO orders (customer_id, order_status)
        VALUES (:customer_id, 'Pending')
    """)
    result = connection.execute(query, {"customer_id": customer_id})
    connection.commit()
    return result.lastrowid


def add_order_item(connection, order_id, variant_id, quantity):
    query = text("""
        INSERT INTO order_items (order_id, variant_id, quantity, item_status)
        VALUES (:order_id, :variant_id, :quantity, 'Pending')
    """)
    connection.execute(query, {
        "order_id": order_id,
        "variant_id": variant_id,
        "quantity": quantity
    })
    connection.commit()


def get_orders(connection, customer_id):
    query = text("""
        SELECT o.order_id, p.title, oi.quantity, o.order_status
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN product_variants pv ON oi.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        WHERE o.customer_id = :customer_id
    """)
    result = connection.execute(query, {"customer_id": customer_id})
    return result.mappings().all()


# ========
# PRODUCTS
# ========

def get_all_products(connection):
    query = text("""
        SELECT 
            p.product_id,
            p.title,
            p.description,
            p.price,
            p.discount_price,
            MIN(pi.image_url) AS image,
            SUM(v.stock) AS stock
        FROM products p
        LEFT JOIN product_images pi ON p.product_id = pi.product_id
        LEFT JOIN product_variants v ON p.product_id = v.product_id
        GROUP BY p.product_id
    """)
    result = connection.execute(query)
    return result.mappings().all()


def get_product_by_id(connection, product_id):
    query = text("SELECT * FROM products WHERE product_id = :product_id")
    result = connection.execute(query, {"product_id": product_id})
    return result.mappings().first()


def search_products(connection, term):
    query = text("""
        SELECT * FROM products 
        WHERE title LIKE :term OR description LIKE :term
    """)
    result = connection.execute(query, {"term": f"%{term}%"})
    return result.mappings().all()


# =======
# RETURNS
# =======

def create_return(connection, title, description, demand, customer_id, order_id, variant_id):
    query = text("""
        INSERT INTO returns (title, description, demand, status, customer_id, order_id, variant_id)
        VALUES (:title, :description, :demand, 'Pending', :customer_id, :order_id, :variant_id)
    """)
    connection.execute(query, {
        "title": title,
        "description": description,
        "demand": demand,
        "customer_id": customer_id,
        "order_id": order_id,
        "variant_id": variant_id
    })
    connection.commit()


def get_returns(connection, customer_id):
    query = text("SELECT * FROM returns WHERE customer_id = :customer_id")
    result = connection.execute(query, {"customer_id": customer_id})
    return result.mappings().all()


# =======
# REVIEWS
# =======

def add_review(connection, variant_id, customer_id, rating, description):
    query = text("""
        INSERT INTO reviews (variant_id, customer_id, rating, description)
        VALUES (:variant_id, :customer_id, :rating, :description)
    """)
    connection.execute(query, {
        "variant_id": variant_id,
        "customer_id": customer_id,
        "rating": rating,
        "description": description
    })
    connection.commit()


def get_reviews_for_product(connection, variant_id):
    query = text("""
        SELECT r.rating, r.description, r.date, u.name
        FROM reviews r
        JOIN users u ON r.customer_id = u.user_id
        WHERE r.variant_id = :variant_id
    """)
    result = connection.execute(query, {"variant_id": variant_id})
    return result.mappings().all()


# ======
# VENDOR
# ======

def get_vendor_products(connection, vendor_id):
    query = text("SELECT * FROM products WHERE vendor_id = :vendor_id")
    result = connection.execute(query, {"vendor_id": vendor_id})
    return result.mappings().all()


# ========
# WISHLIST
# ========

def get_wishlist(connection, customer_id):
    query = text("""
        SELECT wi.variant_id
        FROM wishlist_items wi
        JOIN wishlists w ON wi.wishlist_id = w.wishlist_id
        WHERE w.customer_id = :customer_id
    """)
    result = connection.execute(query, {"customer_id": customer_id})
    return result.mappings().all()


def add_to_wishlist(connection, customer_id, variant_id):
    query = text("""
        INSERT INTO wishlist_items (wishlist_id, variant_id)
        SELECT wishlist_id, :variant_id 
        FROM wishlists 
        WHERE customer_id = :customer_id
    """)
    connection.execute(query, {
        "variant_id": variant_id,
        "customer_id": customer_id
    })
    connection.commit()


# ===============
# USER MANAGEMENT
# ===============

def register_new_user(connection, name, email, username, password, role):
    try:
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

        user_id = connection.execute(text("SELECT LAST_INSERT_ID()")).scalar()

        if role == "customer":
            connection.execute(text("INSERT INTO customers (customer_id) VALUES (:id)"), {"id": user_id})
            connection.execute(text("INSERT INTO carts (customer_id) VALUES (:id)"), {"id": user_id})
            connection.execute(text("INSERT INTO wishlists (customer_id) VALUES (:id)"), {"id": user_id})
        
        elif role == "vendor":
            connection.execute(text("INSERT INTO vendors (vendor_id) VALUES (:id)"), {"id": user_id})
        
        connection.commit()
        return True
    except Exception as e:
        print(f"Error during registration: {e}")
        connection.rollback()
        return False


def is_admin(connection, user_id):
    query = text("SELECT * FROM admins WHERE admin_id = :id")
    result = connection.execute(query, {"id": user_id}).fetchone()
    return result is not None


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


# ==============
# DATABASE RESET
# ==============

def reset_database(connection, schema_file, seed_file):
    try:
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        
        tables = connection.execute(text("SHOW TABLES;"))
        for (table_name,) in tables:
            connection.execute(text(f"DROP TABLE IF EXISTS {table_name};"))
        
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

        def run_sql_file(filename):
            if os.path.exists(filename):
                with open(filename, 'r') as f:
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