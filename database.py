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


def confirm_vendor_item(connection, order_id, variant_id):
    # Update the status of the specific item
    query = text("""
        UPDATE order_items 
        SET item_status = 'Confirmed' 
        WHERE order_id = :oid AND variant_id = :vid
    """)
    connection.execute(query, {"oid": order_id, "vid": variant_id})

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


# ======
# CHAT
# ======

def get_chat_history(connection, customer_id=None, vendor_id=None, admin_id=None):
    """Fetches messages for a specific user role."""
    query_str = "SELECT * FROM chats WHERE 1=1"
    params = {}

    if customer_id:
        query_str += " AND customer_id = :customer_id"
        params["customer_id"] = customer_id
    if vendor_id:
        query_str += " AND vendor_id = :vendor_id"
        params["vendor_id"] = vendor_id
    if admin_id:
        query_str += " AND admin_id = :admin_id"
        params["admin_id"] = admin_id

    query_str += " ORDER BY timestamp ASC"
    
    result = connection.execute(text(query_str), params)
    return result.mappings().all()

def send_chat_message(connection, sender_id, customer_id, text_content, vendor_id=None, admin_id=None, return_id=None):
    """Inserts a new message into the database."""
    query = text("""
        INSERT INTO chats (sender_id, customer_id, vendor_id, admin_id, return_id, text)
        VALUES (:sender_id, :customer_id, :vendor_id, :admin_id, :return_id, :text)
    """)
    connection.execute(query, {
        "sender_id": sender_id,
        "customer_id": customer_id,
        "vendor_id": vendor_id,
        "admin_id": admin_id,
        "return_id": return_id,
        "text": text_content
    })
    connection.commit()

def get_chat_list(connection, user_id, role):
    #Join users table to get names for everyone
    query_str = """
        SELECT
            c.customer_id, cu.name as customer_name,
            c.vendor_id, vu.name as vendor_name,
            MAX(c.admin_id) as admin_id, 
            MAX(au.name) as admin_name,
            MAX(c.return_id) as return_id
        FROM chats c
        JOIN users cu ON c.customer_id = cu.user_id
        LEFT JOIN users vu ON c.vendor_id = vu.user_id
        LEFT JOIN users au ON c.admin_id = au.user_id
    """

    if role == 'customer':
        query_str += " WHERE c.customer_id = :uid"
    elif role == 'vendor':
        query_str += " WHERE c.vendor_id = :uid"
    
    # GROUP BY ensures we don't get duplicates in the sidebar
    query_str += " GROUP BY c.customer_id, c.vendor_id, c.admin_id, c.return_id"

    return connection.execute(text(query_str), {"uid": user_id}).mappings().all()

def get_specific_chat_history(connection, customer_id, vendor_id=None, admin_id=None, return_id=None):
    base_query = """
        SELECT 
            c.*, 
            u.name as sender_name
        FROM chats c
        JOIN users u ON c.sender_id = u.user_id
        WHERE c.customer_id = :cid
    """

    params = {"cid": customer_id}

    if return_id:
        base_query += " AND c.return_id = :rid"
        params["rid"] = return_id
    elif vendor_id:
        base_query += " AND c.vendor_id = :vid AND c.return_id IS NULL"
        params["vid"] = vendor_id
    else:
        base_query += " AND c.admin_id = :aid AND c.vendor_id IS NULL AND c.return_id IS NULL"
        params["aid"] = admin_id

    base_query += " ORDER BY c.timestamp ASC"

    return connection.execute(text(base_query), params).mappings().all()
                

def get_all_vendors(connection):
    return connection.execute(text("SELECT vendor_id as id, name FROM vendors JOIN users ON vendor_id = user_id")).mappings().all()

def get_all_admins(connection):
    return connection.execute(text("SELECT admin_id as id, name FROM admins JOIN users ON admin_id = user_id")).mappings().all()

def get_all_customers(connection):
    return connection.execute(text("SELECT customer_id as id, name FROM customers JOIN users ON customer_id = user_id")).mappings().all()

def get_vendor_customers(connection, vendor_id):
    query = text("""
        SELECT DISTINCT o.customer_id as id, u.name
        FROM order_items oi
        JOIN products p ON oi.variant_id = (SELECT variant_id FROM product_variants pv WHERE pv.product_id = p.product_id LIMIT 1)
        JOIN orders o ON oi.order_id = o.order_id
        JOIN users u ON o.customer_id = u.user_id
        WHERE p.vendor_id = :vid
    """)
    return connection.execute(query, {"vid": vendor_id}).mappings().all()

def get_user_name(connection, user_id):
    query = text("SELECT name FROM users WHERE user_id = :uid")
    return connection.execute(query, {"uid": user_id}).scalar()

def get_return_title(connection, return_id):
    query = text("""
        SELECT p.title 
        FROM returns r
        JOIN product_variants pv ON r.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        WHERE r.return_id = :rid
    """)
    return connection.execute(query, {"rid": return_id}).scalar()


# ======
# ORDERS
# ======

def create_order(connection, customer_id, total_price):
    query = text("""
        INSERT INTO orders (customer_id, order_status, total_price)
        VALUES (:customer_id, 'Pending', :total)
    """)
    result = connection.execute(query, {"customer_id": customer_id, "total": total_price})
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
        SELECT o.order_id, 
               o.total_price,
               o.ordered_at,
               o.order_status,
               GROUP_CONCAT(p.title SEPARATOR ', ') as product_titles
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN product_variants pv ON oi.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        WHERE o.customer_id = :customer_id
        GROUP BY o.order_id
        ORDER BY o.ordered_at DESC;
    """)
    result = connection.execute(query, {"customer_id": customer_id})
    return result.mappings().all()

def get_order_items(connection, order_id):
    query = text("""
        SELECT 
            oi.variant_id, 
            oi.quantity, 
            oi.item_status, 
            p.title, 
            pv.size, 
            pv.color
        FROM order_items oi
        JOIN product_variants pv ON oi.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        WHERE oi.order_id = :order_id
    """)
    result = connection.execute(query, {"order_id": order_id})
    return result.mappings().all()


# ========
# PRODUCTS
# ========

def add_new_product(connection, vendor_id, title, description, price, 
                    discount_price, discount_end, variants, images, category, warranty): 
    
    # 2. Add 'warranty_period' (or whatever your SQL column is) to the query
    query = text("""
        INSERT INTO products (vendor_id, title, description, price, 
                             discount_price, discount_deadline, category, warranty_period)
        VALUES (:vendor_id, :title, :description, :price, 
                :discount_price, :discount_deadline, :category, :warranty)
    """)
    
    result = connection.execute(query, {
        "vendor_id": vendor_id,
        "title": title,
        "description": description,
        "price": price,
        "discount_price": discount_price,
        "discount_deadline": discount_end,
        "category": category,
        "warranty": warranty
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
    # 1. DEFINE the query variable first
    query = text("""
        SELECT 
            p.product_id, p.title, p.description, p.price, p.discount_price, p.discount_deadline,
            AVG(r.rating) as avg_rating,
            COUNT(r.review_id) as review_count,
            GROUP_CONCAT(DISTINCT v.variant_id) as v_ids,
            GROUP_CONCAT(DISTINCT v.size) as v_sizes,
            GROUP_CONCAT(DISTINCT v.color) as v_colors,
            GROUP_CONCAT(DISTINCT v.stock) as v_stocks
        FROM products p
        LEFT JOIN product_variants v ON p.product_id = v.product_id
        LEFT JOIN reviews r ON r.product_id = p.product_id 
        GROUP BY p.product_id
    """)
    
    # 2. EXECUTE the query (This is where your error was likely triggered)
    result = connection.execute(query).mappings().all()

    products = []
    for row in result:
        item = dict(row)
        item['variants'] = []
        
        if item.get('v_ids'):
            # Convert Group_Concat strings into lists
            ids = str(item['v_ids']).split(',')
            sizes = str(item['v_sizes']).split(',')
            colors = str(item['v_colors']).split(',')
            stocks = str(item['v_stocks']).split(',')

            for i in range(len(ids)):
                item['variants'].append({
                    "id": ids[i],
                    "size": sizes[i] if i < len(sizes) else "N/A",
                    "color": colors[i] if i < len(colors) else "N/A",
                    # The int() here fixes the template addition error
                    "stock": int(stocks[i]) if i < len(stocks) else 0
                })
        
        products.append(item)
    return products

def get_product_images(connection):
    query = text("SELECT * FROM product_images")
    result = connection.execute(query)
    return result.mappings().all()


def get_product_images_by_id(connection, product_id):
    query = text("SELECT image_url FROM product_images WHERE product_id = :product_id")
    result = connection.execute(query, {"product_id": product_id})
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

def get_filtered_products(connection, search="", vendor="", color="", size="", availability="", category=""):
    sql = """
        SELECT 
            p.product_id, p.title, p.description, p.price, p.discount_price, p.discount_deadline,
            u.name as vendor_name,
            AVG(r.rating) as avg_rating,
            GROUP_CONCAT(v.variant_id) as v_ids,
            GROUP_CONCAT(v.size) as v_sizes,
            GROUP_CONCAT(v.color) as v_colors,
            GROUP_CONCAT(v.stock) as v_stocks
        FROM products p
        JOIN product_variants v ON p.product_id = v.product_id
        JOIN users u ON p.vendor_id = u.user_id
        LEFT JOIN reviews r ON p.product_id = r.product_id
        WHERE 1=1
    """
    params = {}

    if search:
        sql += " AND (p.title LIKE :search OR p.description LIKE :search)"
        params['search'] = f"%{search}%"

    if category:
        sql += " AND p.category = :category"
        params['category'] = category

    if vendor:
        sql += " AND u.name LIKE :vendor"
        params['vendor'] = f"%{vendor}%"

    if color:
        sql += " AND v.color = :color"
        params['color'] = color

    if size:
        sql += " AND v.size = :size"
        params['size'] = size

    # Handle Availability (In Stock vs Out of Stock)
    if availability == "in_stock":
        sql += " AND v.stock > 0"
    elif availability == "out_of_stock":
        sql += " AND v.stock = 0"

    sql += " GROUP BY p.product_id"
    
    raw_results = connection.execute(text(sql), params).mappings().all()
    
    products = []
    for row in raw_results:
        item = dict(row)
        item['variants'] = []
        if item.get('v_ids'):
            ids = str(item['v_ids']).split(',')
            sizes = str(item['v_sizes']).split(',')
            colors = str(item['v_colors']).split(',')
            stocks = str(item['v_stocks']).split(',')
            for i in range(len(ids)):
                item['variants'].append({
                    "id": ids[i],
                    "size": sizes[i],
                    "color": colors[i],
                    "stock": int(stocks[i])
                })
        products.append(item)
    return products

def update_product(connection, product_id, vendor_id, title, description, price, discount_price, discount_end=None, category=None, warranty=None):
    query = text("""
        UPDATE products 
        SET title = :title, 
            description = :description,
            price = :price, 
            discount_price = :discount_price,
            discount_deadline = :discount_end,
            category = :category,
            warranty_period = :warranty,
            vendor_id = :vendor_id
        WHERE product_id = :product_id
    """)
    connection.execute(query, {
        "title": title,
        "description": description,
        "price": price,
        "discount_price": discount_price,
        "product_id": product_id,
        "discount_end": discount_end,
        "category": category,
        "warranty": warranty,
        "vendor_id": vendor_id
    })

    connection.commit()

def update_variants(connection, variant_ids, colors, sizes, stocks):
    for i in range(len(variant_ids)):
        query = text("""
            UPDATE product_variants
            SET color = :color, size = :size, stock = :stock
            WHERE variant_id = :variant_id
        """)
        connection.execute(query, {
            "color": colors[i],
            "size": sizes[i],
            "stock": stocks[i],
            "variant_id": variant_ids[i]
        })
    connection.commit()

def update_product_images(connection, product_id, image_urls):
    # 1. Delete existing images for the product
    delete_query = text("DELETE FROM product_images WHERE product_id = :product_id")
    connection.execute(delete_query, {"product_id": product_id})

    # 2. Insert new images
    insert_query = text("""
        INSERT INTO product_images (product_id, image_url)
        VALUES (:product_id, :image_url)
    """)

    for url in image_urls:
        connection.execute(insert_query, {
            "product_id": product_id,
            "image_url": url
        })

    connection.commit()


def get_product_variants(connection, product_id):
    query = text("SELECT * FROM product_variants WHERE product_id = :product_id")
    result = connection.execute(query, {"product_id": product_id})
    return result.mappings().all()


def delete_product(connection, product_id):
    query = text("DELETE FROM products WHERE product_id = :product_id")
    connection.execute(query, {"product_id": product_id})
    connection.commit()


def get_unique_colors(connection):
    query = text("SELECT DISTINCT color FROM product_variants WHERE color IS NOT NULL")
    return [row[0] for row in connection.execute(query).fetchall()]

def get_unique_categories(connection):
    query = text("SELECT DISTINCT category FROM products WHERE category IS NOT NULL")
    return [row[0] for row in connection.execute(query).fetchall()]


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

def get_all_pending_returns(connection):
    query = text("""
        SELECT r.*, u.name as customer_name, p.title as product_title
        FROM returns r
        JOIN users u ON r.customer_id = u.user_id
        JOIN product_variants pv ON r.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        ORDER BY r.date DESC
    """)
    return connection.execute(query).mappings().all()

get_all_returns_admin = get_all_pending_returns

def update_return_status(connection, return_id, new_status):
    query = text("UPDATE returns SET status = :status WHERE return_id = :id")
    connection.execute(query, {"status": new_status, "id": return_id})
    connection.commit()


# =======
# REVIEWS
# =======

def add_review(connection, variant_id, customer_id, rating, description):
    query = text("""
        INSERT INTO reviews (product_id, customer_id, rating, description)
        VALUES (:v_id, :c_id, :rate, :desc)
    """)
    connection.execute(query, {
        "v_id": variant_id,    # This is the data from Python
        "c_id": customer_id,
        "rate": rating,
        "desc": description
    })
    connection.commit()


def get_reviews_for_product(connection, product_id):
    """
    Fetches reviews for a specific product.
    Using 'product_id' as defined in your reviews table schema.
    """
    query = text("""
        SELECT 
            r.rating,
            r.description,
            u.name,
            r.product_id  -- Changed from r.variant_id
        FROM reviews r
        JOIN users u ON r.customer_id = u.user_id
        WHERE r.product_id = :product_id  -- Changed from r.variant_id
    """)
    # Ensure we use the correct key in the parameter dictionary
    return connection.execute(query, {"product_id": product_id}).mappings().all()

def get_all_reviews(connection, product_id=None, sort_by='date', filter_rating=None):
    sql = """
        SELECT r.*, p.title AS product_name, u.name AS reviewer_name
        FROM reviews r
        JOIN product_variants v ON r.product_id = v.variant_id -- Fixed: r.product_id
        JOIN products p ON v.product_id = p.product_id
        JOIN users u ON r.customer_id = u.user_id
        WHERE 1=1
    """
    params = {}

    if product_id:
        sql += " AND p.product_id = :p_id"
        params["p_id"] = product_id
    
    if filter_rating:
        sql += " AND r.rating = :rating"
        params["rating"] = filter_rating

    if sort_by == 'date':
        sql += " ORDER BY r.date DESC"
    elif sort_by == 'rating_high':
        sql += " ORDER BY r.rating DESC"
    elif sort_by == 'rating_low':
        sql += " ORDER BY r.rating ASC"
    
    return connection.execute(text(sql), params).mappings().all()

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

def get_products_by_vendor(connection, vendor_id):
    """
    Fetches only the products belonging to a specific vendor.
    Used for the Portappliances vendor dashboard.
    """
    query = text("""
        SELECT 
            p.product_id, 
            p.title, 
            p.description, 
            p.warranty_period,
            p.price, 
            p.discount_price,
            p.discount_deadline,
            p.vendor_id
        FROM products p
        WHERE p.vendor_id = :vendor_id
    """)
    
    # Executing the query with the vendor_id parameter for security
    result = connection.execute(query, {"vendor_id": vendor_id}).mappings().all()
    
    return result

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