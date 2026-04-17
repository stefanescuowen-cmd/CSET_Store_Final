from sqlalchemy import text
import os

# =====
# ADMIN
# =====

def get_all_users(connection):
    result = connection.execute(text("SELECT * FROM users"))
    return result.mappings().all()


def get_all_orders(connection):
    query = text("""
        SELECT 
            o.order_id,
            o.customer_id,
            o.order_status,
            o.ordered_at,
            p.title,
            oi.quantity,
            oi.item_status
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN product_variants pv ON oi.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        ORDER BY o.ordered_at DESC
    """)
    result = connection.execute(query)
    return result.mappings().all()

def get_all_reviews(connection):
    query = text("""
        SELECT 
            r.review_id,
            r.rating,
            r.description,
            r.date,
            u.name,
            p.title
        FROM reviews r
        JOIN users u ON r.customer_id = u.user_id
        JOIN products p ON r.product_id = p.product_id
        ORDER BY r.review_id DESC
    """)
    return connection.execute(query).mappings().all()


# ======
# VENDOR
# ======

def get_vendor_orders(connection, vendor_id):
    query = text("""
        SELECT 
            o.order_id,
            oi.variant_id,
            oi.quantity,
            oi.item_status,
            p.title
        FROM order_items oi
        JOIN orders o ON o.order_id = oi.order_id
        JOIN product_variants pv ON oi.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        WHERE p.vendor_id = :vendor_id
        ORDER BY o.order_id DESC
    """)
    result = connection.execute(query, {"vendor_id": vendor_id})
    return result.mappings().all()


def confirm_vendor_item(connection, order_id, vendor_id, variant_id):
    query = text("""
        INSERT INTO order_confirmations (order_id, vendor_id, variant_id, status)
        VALUES (:order_id, :vendor_id, :variant_id, 'Confirmed')
        ON DUPLICATE KEY UPDATE status = 'Confirmed'
    """)
    connection.execute(query, {
        "order_id": order_id,
        "vendor_id": vendor_id,
        "variant_id": variant_id
    })
    connection.commit()


# ====
# CART
# ====

def get_variant_stock(connection, variant_id):
    query = text("SELECT stock FROM product_variants WHERE variant_id = :variant_id")
    result = connection.execute(query, {"variant_id": variant_id}).fetchone()
    return result[0] if result else 0

def get_cart_items(connection, customer_id):
    query = text("""
        SELECT p.title, p.price, p.discount_price, ci.quantity, pv.variant_id, pv.stock
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

def get_cart_item(connection, customer_id, variant_id):
    query = text("""
        SELECT ci.quantity 
        FROM carts c
        JOIN cart_items ci ON c.cart_id = ci.cart_id
        WHERE c.customer_id = :customer_id AND ci.variant_id = :variant_id
    """)
    result = connection.execute(query, {
        "customer_id": customer_id,
        "variant_id": variant_id
    }).fetchone()
    return result['quantity'] if result else None

def update_cart_quantity(connection, cart_id, variant_id, quantity):
    query = text("""
        UPDATE cart_items 
        SET quantity = :quantity 
        WHERE cart_id = :cart_id AND variant_id = :variant_id
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

# ==============
# CUSTOMER CHATS
# ==============

def get_customer_conversations(connection, customer_id):

    query = text("""
        SELECT
            c.vendor_id,
            c.admin_id,
            CASE
                WHEN c.vendor_id IS NOT NULL THEN 'vendor'
                WHEN c.admin_id IS NOT NULL THEN 'admin'
            END AS partner_type,
            u.name AS partner_name,
            MAX(c.timestamp) AS last_message_time
        FROM chats c
        JOIN users u
            ON u.user_id = COALESCE(c.vendor_id, c.admin_id)
        WHERE c.customer_id = :customer_id
        GROUP BY c.vendor_id, c.admin_id, u.name
        ORDER BY last_message_time DESC
    """)

    return connection.execute(query, {
        "customer_id": customer_id
    }).mappings().all()


# ===========
# VENDOR LIST
# ===========

def get_all_vendors(connection):
    query = text("""
        SELECT v.vendor_id, u.name
        FROM vendors v
        JOIN users u ON u.user_id = v.vendor_id
        ORDER BY u.name
    """)
    return connection.execute(query).mappings().all()


# ==========
# ADMIN LIST
# ==========

def get_all_admins(connection):
    query = text("""
        SELECT a.admin_id, u.name
        FROM admins a
        JOIN users u ON u.user_id = a.admin_id
        ORDER BY u.name
    """)
    return connection.execute(query).mappings().all()


# ========================
# CUSTOMER <=> VENDOR CHAT
# ========================

def get_customer_vendor_chat(connection, customer_id, vendor_id):

    query = text("""
        SELECT
            c.*,
            u.name AS sender_name
        FROM chats c
        JOIN users u ON u.user_id = c.customer_id
        WHERE c.customer_id = :customer_id
        AND c.vendor_id = :vendor_id
        ORDER BY c.timestamp
    """)

    return connection.execute(query, {
        "customer_id": customer_id,
        "vendor_id": vendor_id
    }).mappings().all()


def get_vendor_chat(connection, vendor_id, customer_id):

    query = text("""
        SELECT
            c.*,
            u.name AS sender_name
        FROM chats c
        JOIN users u ON u.user_id = c.customer_id
        WHERE c.vendor_id = :vendor_id
        AND c.customer_id = :customer_id
        ORDER BY c.timestamp
    """)

    return connection.execute(query, {
        "vendor_id": vendor_id,
        "customer_id": customer_id
    }).mappings().all()


# =======================
# CUSTOMER <=> ADMIN CHAT
# =======================

def get_customer_admin_chat(connection, customer_id, admin_id):

    query = text("""
        SELECT
            c.*,
            u.name AS sender_name
        FROM chats c
        JOIN users u ON u.user_id = c.customer_id
        WHERE c.customer_id = :customer_id
        AND c.admin_id = :admin_id
        ORDER BY c.timestamp
    """)

    return connection.execute(query, {
        "customer_id": customer_id,
        "admin_id": admin_id
    }).mappings().all()


def get_admin_chat(connection, admin_id, customer_id):

    query = text("""
        SELECT
            c.*,
            u.name AS sender_name
        FROM chats c
        JOIN users u ON u.user_id = c.customer_id
        WHERE c.admin_id = :admin_id
        AND c.customer_id = :customer_id
        ORDER BY c.timestamp
    """)

    return connection.execute(query, {
        "admin_id": admin_id,
        "customer_id": customer_id
    }).mappings().all()


# =============
# CONVERSATIONS
# =============

def get_vendor_conversations(connection, vendor_id):

    query = text("""
        SELECT
            c.customer_id,
            u.name AS partner_name,
            MAX(c.timestamp) AS last_message_time
        FROM chats c
        JOIN users u ON u.user_id = c.customer_id
        WHERE c.vendor_id = :vendor_id
        GROUP BY c.customer_id, u.name
        ORDER BY last_message_time DESC
    """)

    return connection.execute(query, {
        "vendor_id": vendor_id
    }).mappings().all()


def get_admin_conversations(connection, admin_id):

    query = text("""
        SELECT
            c.customer_id,
            u.name AS partner_name,
            MAX(c.timestamp) AS last_message_time
        FROM chats c
        JOIN users u ON u.user_id = c.customer_id
        WHERE c.admin_id = :admin_id
        GROUP BY c.customer_id, u.name
        ORDER BY last_message_time DESC
    """)

    return connection.execute(query, {
        "admin_id": admin_id
    }).mappings().all()


# ============
# SEND MESSAGE
# ============

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


# =======
# REVIEWS
# =======

def create_review(connection, product_id, customer_id, rating, description, image=None):
    """
    Inserts a new review. If the user has already reviewed this product,
    it updates the existing review (handling the UNIQUE constraint).
    """
    query = text("""
        INSERT INTO reviews (product_id, customer_id, rating, description, image)
        VALUES (:product_id, :customer_id, :rating, :description, :image)
        ON DUPLICATE KEY UPDATE 
            rating = :rating, 
            description = :description, 
            image = :image, 
            date = CURRENT_TIMESTAMP
    """)
    connection.execute(query, {
        "product_id": product_id,
        "customer_id": customer_id,
        "rating": rating,
        "description": description,
        "image": image
    })
    connection.commit()

def get_product_reviews(connection, product_id, sort_by="date", filter_rating=None):
    """
    Retrieves reviews for a specific product.
    Supports filtering by rating and sorting by date or rating.
    """
    # 1. Base SQL joining users to get the reviewer's name
    sql = """
        SELECT r.*, u.name as reviewer_name 
        FROM reviews r
        JOIN users u ON r.customer_id = u.user_id
        WHERE r.product_id = :product_id
    """
    params = {"product_id": product_id}

    # 2. Add Filtering logic
    if filter_rating:
        sql += " AND r.rating = :rating"
        params["rating"] = filter_rating

    # 3. Add Sorting logic
    if sort_by == "rating_high":
        sql += " ORDER BY r.rating DESC"
    elif sort_by == "rating_low":
        sql += " ORDER BY r.rating ASC"
    else:
        sql += " ORDER BY r.date DESC" # Default to newest first

    result = connection.execute(text(sql), params)
    return result.mappings().all()

def get_all_reviews(connection, sort_by="date", filter_rating=None):
    # Base SQL logic
    sql = """
        SELECT r.*, u.name as reviewer_name, p.title as product_title
        FROM reviews r
        JOIN users u ON r.customer_id = u.user_id
        JOIN product_variants pv ON r.product_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
    """
    params = {}
    
    # Filtering logic - Check if a specific rating was requested
    if filter_rating:
        sql += " WHERE r.rating = :rating"
        params["rating"] = filter_rating

    # Sorting logic - Decide the order based on the user's choice
    if sort_by == "rating_high":
        sql += " ORDER BY r.rating DESC"
    elif sort_by == "rating_low":
        sql += " ORDER BY r.rating ASC"
    else:
        sql += " ORDER BY r.date DESC" # Default to newest first

    result = connection.execute(text(sql), params)
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

def add_new_product(connection, vendor_id, title, description, price, discount_price, discount_end, variants, images):    
    query = text("""
        INSERT INTO products (vendor_id, title, description, price, discount_price, discount_deadline)
        VALUES (:vendor_id, :title, :description, :price, :discount_price, :discount_end)
    """)
    result = connection.execute(query, {
        "vendor_id": vendor_id,
        "title": title,
        "description": description,
        "price": price,
        "discount_price": discount_price,
        "discount_end": discount_end
    })
    product_id = result.lastrowid

    if images:
        img_query = text("""
            INSERT INTO product_images (product_id, image_url) 
            VALUES (:product_id, :image_url)
        """)
        for url in images:
            connection.execute(img_query, {
                "product_id": product_id,
                "image_url": url
            })

    for variant in variants:
        variant_query = text("""
            INSERT INTO product_variants (product_id, size, color, stock)
            VALUES (:product_id, :size, :color, :stock)
        """)
        connection.execute(variant_query, {
            "product_id": product_id,
            "size": variant['size'],
            "color": variant['color'],
            "stock": variant['stock']
        })
    
    connection.commit()
    return product_id

def get_all_products(connection):
    query = text("""
        SELECT 
            p.product_id, p.title, p.description, p.price, p.discount_price,
            GROUP_CONCAT(v.variant_id) as v_ids,
            GROUP_CONCAT(v.size) as v_sizes,
            GROUP_CONCAT(v.color) as v_colors,
            GROUP_CONCAT(v.stock) as v_stocks
        FROM products p
        JOIN product_variants v ON p.product_id = v.product_id
        GROUP BY p.product_id
    """)
    result = connection.execute(query).mappings().all()

    products = []
    for row in result:
        item = dict(row)
        item['variants'] = []
        ids = str(item['v_ids']).split(',')
        sizes = str(item['v_sizes']).split(',')
        colors = str(item['v_colors']).split(',')
        stocks = str(item['v_stocks']).split(',')

        for i in range(len(ids)):
            item['variants'].append({
                "id": ids[i],
                "size": sizes[i],
                "color": colors[i],
                "stock": stocks[i]
            })
        products.append(item)
    return products

def get_product_images(connection):
    query = text("SELECT * FROM product_images")
    result = connection.execute(query)
    return result.mappings().all()


def get_product_by_id(connection, product_id):
    query = text("SELECT * FROM products WHERE product_id = :product_id")
    result = connection.execute(query, {"product_id": product_id})
    return result.mappings().first()


def search_products(connection, term):
    query = text("""
        SELECT 
            p.product_id, p.title, p.description, p.price, p.discount_price,
            GROUP_CONCAT(v.variant_id) as v_ids,
            GROUP_CONCAT(v.size) as v_sizes,
            GROUP_CONCAT(v.color) as v_colors,
            GROUP_CONCAT(v.stock) as v_stocks
        FROM products p
        JOIN product_variants v ON p.product_id = v.product_id
        WHERE p.title LIKE :term OR p.description LIKE :term
        GROUP BY p.product_id
    """)
    result = connection.execute(query, {"term": f"%{term}%"}).mappings().all()

    products = []
    for row in result:
        item = dict(row)
        item['variants'] = []
        ids = str(item['v_ids']).split(',')
        sizes = str(item['v_sizes']).split(',')
        colors = str(item['v_colors']).split(',')
        stocks = str(item['v_stocks']).split(',')

        for i in range(len(ids)):
            item['variants'].append({
                "id": ids[i],
                "size": sizes[i],
                "color": colors[i],
                "stock": stocks[i]
            })
        products.append(item)
    return products



def update_product(connection, product_id, title, description, price, discount_price, stock):
    query = text("""
        UPDATE products 
        SET title = :title, 
            description = :description,
            price = :price, 
            discount_price = :discount_price
        WHERE product_id = :product_id
    """)
    connection.execute(query, {
        "title": title,
        "description": description,
        "price": price,
        "discount_price": discount_price,
        "product_id": product_id
    })

    stock_query = text("""
        UPDATE product_variants
        SET stock = :stock
        WHERE product_id = :product_id
    """)
    connection.execute(stock_query, {
        "stock": stock,
        "product_id": product_id
    })

    connection.commit()

def delete_product(connection, product_id):
    query = text("DELETE FROM products WHERE product_id = :product_id")
    connection.execute(query, {"product_id": product_id})
    connection.commit()


# =======
# RETURNS
# =======

def create_return_request(connection, customer_id, order_id, variant_id, title, description, demand):
    query = text("""
        INSERT INTO returns (customer_id, order_id, variant_id, title, description, demand, status)
        VALUES (:customer_id, :order_id, :variant_id, :title, :description, :demand, 'Pending')
    """)
    connection.execute(query, {
        "customer_id": customer_id,
        "order_id": order_id,
        "variant_id": variant_id,
        "title": title,
        "description": description,
        "demand": demand
    })
    connection.commit()

def get_customer_returns(connection, customer_id):
    query = text("""
        SELECT r.*, p.title as product_title 
        FROM returns r
        JOIN product_variants pv ON r.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        WHERE r.customer_id = :customer_id
        ORDER BY r.date DESC
    """)
    return connection.execute(query, {"customer_id": customer_id}).mappings().all()

def get_all_returns_admin(connection):
    query = text("""
        SELECT r.*, u.name as customer_name, p.title as product_title
        FROM returns r
        JOIN users u ON r.customer_id = u.user_id
        JOIN product_variants pv ON r.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        ORDER BY FIELD(status, 'Pending', 'Confirmed', 'Processing', 'Complete', 'Rejected')
    """)
    return connection.execute(query).mappings().all()

def update_return_status(connection, return_id, new_status):
    query = text("UPDATE returns SET status = :status WHERE return_id = :id")
    connection.execute(query, {"status": new_status, "id": return_id})
    connection.commit()


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
        SELECT 
            r.rating,
            r.description,
            u.name,
            r.variant_id
        FROM reviews r
        JOIN users u ON r.customer_id = u.user_id
        WHERE r.variant_id = :variant_id
    """)
    return connection.execute(query, {"variant_id": variant_id}).mappings().all()

# ======
# VENDOR
# ======

def get_vendor_products(connection, vendor_id):
    query = text("SELECT * FROM products WHERE vendor_id = :vendor_id")
    result = connection.execute(query, {"vendor_id": vendor_id})
    return result.mappings().all()


def get_vendor_orders(connection, vendor_id):
    query = text("""
        SELECT o.order_id, p.title, oi.quantity, oi.item_status
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN product_variants pv ON oi.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        WHERE p.vendor_id = :vendor_id
    """)
    return connection.execute(query, {"vendor_id": vendor_id}).mappings().all()


# ========
# WISHLIST
# ========

def get_wishlist(connection, customer_id):
    query = text("""
        SELECT 
            p.title,
            p.price,
            pv.variant_id,
            pv.color,
            pv.size
        FROM wishlists w
        JOIN wishlist_items wi ON w.wishlist_id = wi.wishlist_id
        JOIN product_variants pv ON wi.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        WHERE w.customer_id = :customer_id
    """)
    result = connection.execute(query, {"customer_id": customer_id})
    return result.mappings().all()


def add_to_wishlist(connection, customer_id, variant_id):
    # 1. get or create wishlist
    wishlist = connection.execute(text("""
        SELECT wishlist_id FROM wishlists WHERE customer_id = :cid
    """), {"cid": customer_id}).mappings().first()

    if not wishlist:
        result = connection.execute(text("""
            INSERT INTO wishlists (customer_id)
            VALUES (:cid)
        """), {"cid": customer_id})
        connection.commit()
        wishlist_id = result.lastrowid
    else:
        wishlist_id = wishlist["wishlist_id"]

    # 2. insert item (ignore duplicates)
    connection.execute(text("""
        INSERT IGNORE INTO wishlist_items (wishlist_id, variant_id)
        VALUES (:wid, :vid)
    """), {
        "wid": wishlist_id,
        "vid": variant_id
    })

    connection.commit()

def remove_from_wishlist(connection, customer_id, variant_id):
    query = text("""
        DELETE wi FROM wishlist_items wi
        JOIN wishlists w ON wi.wishlist_id = w.wishlist_id
        WHERE w.customer_id = :cid AND wi.variant_id = :vid
    """)
    connection.execute(query, {
        "cid": customer_id,
        "vid": variant_id
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