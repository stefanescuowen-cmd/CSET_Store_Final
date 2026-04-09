USE store_db;

-- =====================================
-- AUTHENTICATION (Registration / Login)
-- =====================================

-- Check if user already exists
SELECT * FROM users WHERE email = 'alice@mail.com';SET @user_email = 'alice@mail.com';
SET @user_id = (SELECT user_id FROM users WHERE email = @user_email);

-- Register new user
INSERT INTO users (name, email, username, password)
VALUES ('Test User', 'test@mail.com', 'testuser', 'pass');

-- Login using username
SELECT * FROM users WHERE user_id = @user_id AND password = 'pass';

-- Login using email
SELECT * FROM users
WHERE email = 'alice@mail.com' AND password = 'pass';


-- =================================
-- PRODUCTS (READ / SEARCH / FILTER)
-- =================================

-- View products with vendor names
SELECT p.title, u.name AS vendor
FROM products p
JOIN vendors v ON p.vendor_id = v.vendor_id
JOIN users u ON v.vendor_id = u.user_id;

-- Search products by name
SELECT * FROM products
WHERE title LIKE '%phone%';

-- Search products by description
SELECT * FROM products
WHERE description LIKE '%gaming%';

-- Search products by vendor
SELECT * FROM products
WHERE vendor_id = 8;

-- Filter products by color
SELECT p.*
FROM products p
JOIN product_variants v ON p.product_id = v.product_id
WHERE v.color = 'Black';

-- Filter products by size
SELECT p.*
FROM products p
JOIN product_variants v ON p.product_id = v.product_id
WHERE v.size = '15-inch';

-- Filter products by availability (in stock)
SELECT p.*
FROM products p
JOIN product_variants v ON p.product_id = v.product_id
WHERE v.stock > 0;


-- =====================================
-- PRODUCT VARIANTS & IMAGES (CRUD)
-- =====================================

-- Add a new variant
SET @product_title = 'Test Product';
SET @product_id = (SELECT product_id FROM products WHERE title=@product_title LIMIT 1);
INSERT INTO product_variants (product_id, size, color, stock)

-- Update a variant
UPDATE product_variants
SET stock = 8, color = 'Space Gray'
WHERE variant_id = 1;

-- Delete a variant
DELETE FROM product_variants
WHERE variant_id = 2;

-- Add product image
INSERT INTO product_images (product_id, image_url)
VALUES (1, 'laptop1.jpg');

UPDATE product_images
SET image_url = 'laptop1_updated.jpg'
WHERE image_id = 1;

UPDATE product_images
SET url = 'laptop1_updated.jpg'
WHERE image_id = 1;

-- Delete product image
DELETE FROM product_images
WHERE image_id = 2;


-- ======================
-- CART (CRUD OPERATIONS)
-- ======================

-- Add item to cart
INSERT INTO cart_items VALUES (1, 1, 2);

-- View cart contents
SELECT c.customer_id, p.title, ci.quantity
FROM carts c
JOIN cart_items ci ON c.cart_id = ci.cart_id
JOIN product_variants pv ON ci.variant_id = pv.variant_id
JOIN products p ON pv.product_id = p.product_id;

-- Update item quantity in cart
UPDATE cart_items
SET quantity = 3
WHERE cart_id = 1 AND variant_id = 1;

-- Remove item from cart
DELETE FROM cart_items
WHERE cart_id = 1 AND variant_id = 2;


-- ==========================
-- WISHLIST (CRUD OPERATIONS)
-- ==========================

-- Create wishlist for a customer
INSERT INTO wishlists (customer_id) VALUES (3);

-- Add item to wishlist
INSERT INTO wishlist_items VALUES (1, 2);

-- View wishlist items
SELECT * FROM wishlist_items WHERE wishlist_id = 1;

-- Remove item from wishlist
DELETE FROM wishlist_items
WHERE wishlist_id = 1 AND variant_id = 2;


-- ======
-- ORDERS
-- ======

-- View orders with product details
SELECT o.order_id, p.title, oi.quantity
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN product_variants pv ON oi.variant_id = pv.variant_id
JOIN products p ON pv.product_id = p.product_id;

-- Place a new order
INSERT INTO orders (customer_id, order_status)
VALUES (3, 'Pending');

-- Add items to order
INSERT INTO order_items (order_id, variant_id, quantity, status)
VALUES
(2, 1, 1, 'Pending'),
(2, 3, 2, 'Pending');

INSERT INTO order_confirmations (order_id, vendor_id, status)
VALUES
(2, 8, 'Confirmed'),
(2, 9, 'Confirmed');

-- Confirm order by vendor
UPDATE order_confirmations
SET status = 'Confirmed'
WHERE order_id = 1 AND vendor_id = 8;

-- Update order status to shipped
UPDATE orders
SET order_status = 'Shipped'
WHERE order_id = 1;

-- Mark order as delivered
UPDATE orders
SET order_status = 'Delivered', delivered_at = NOW()
WHERE order_id = 1;


-- =================================
-- MULTI-VENDOR ORDER EXAMPLE
-- =================================

-- Place multi-vendor order
INSERT INTO orders (customer_id, order_status) VALUES (3, 'Pending');

-- Add items from different vendors
INSERT INTO order_items VALUES (2, 1, 1, 'Pending'); -- vendor 8
INSERT INTO order_items VALUES (2, 3, 2, 'Pending'); -- vendor 9

-- Confirm per vendor
INSERT INTO order_confirmations VALUES (2, 8, 'Confirmed');
INSERT INTO order_confirmations VALUES (2, 9, 'Confirmed');


-- =======================
-- TOTAL PRICE CALCULATION
-- =======================

SELECT o.order_id,
SUM(oi.quantity * COALESCE(p.discount_price, p.price)) AS total_price
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN product_variants pv ON oi.variant_id = pv.variant_id
JOIN products p ON pv.product_id = p.product_id
GROUP BY o.order_id;


-- ============================
-- REVIEWS (CRUD AND FILTERING)
-- ============================

-- Create a review
INSERT INTO reviews (product_id, customer_id, rating, description)
VALUES (1, 3, 5, 'Great product');

-- Get reviews for a product
SELECT * FROM reviews WHERE product_id = 1;

-- Get reviews by a customer
SELECT * FROM reviews WHERE customer_id = 3;

-- Sort reviews by rating
SELECT * FROM reviews ORDER BY rating DESC;

-- Sort reviews by date
SELECT * FROM reviews ORDER BY date DESC;

-- Delete a review
DELETE FROM reviews WHERE review_id = 1;


-- ==================
-- RETURNS / WARRANTY
-- ==================

-- Create return request
INSERT INTO returns (title, description, demand, status, customer_id, order_id, variant_id)
VALUES ('Damaged item', 'Screen cracked', 'Return', 'Pending', 3, 1, 1);

-- Update return status
UPDATE returns
SET status = 'Processing'
WHERE return_id = 1;

-- Check warranty validity
SELECT o.order_id, p.title, 
DATEDIFF(NOW(), o.delivered_at) AS days_since_delivery,
p.warranty_period,
CASE 
    WHEN DATE_ADD(o.delivered_at, INTERVAL p.warranty_period MONTH) >= NOW() THEN 'Warranty Valid'
    ELSE 'Warranty Expired'
END AS warranty_status
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN product_variants pv ON oi.variant_id = pv.variant_id
JOIN products p ON pv.product_id = p.product_id
WHERE o.order_id = 1;


-- ===========
-- CHAT SYSTEM
-- ===========

-- Send message to vendor
INSERT INTO chats (customer_id, vendor_id, text, timestamp)
VALUES (3, 8, 'Hello, is this available?', NOW());

-- Send message regarding return/warranty
INSERT INTO chats (customer_id, admin_id, text, timestamp)
VALUES (3, 1, 'I have a problem with my laptop warranty claim.', NOW());

-- Get messages sent to a vendor
SELECT * FROM chats WHERE vendor_id = 8;

-- Get messages sent by a customer
SELECT * FROM chats WHERE customer_id = 3;

-- Retrieve all messages for a particular return
SELECT c.*
FROM chats c
JOIN returns r ON c.customer_id = r.customer_id
WHERE r.return_id = 1;

-- Delete a message
DELETE FROM chats WHERE chat_id = 1;


-- =====================
-- ADDITIONAL OPERATIONS
-- =====================

-- Add new product
INSERT INTO products (title, description, price, vendor_id)
VALUES ('Test Product', 'Demo item', 99.99, 8);

-- Update product pricing
UPDATE products
SET price = 899.99, discount_price = 799.99
WHERE product_id = 1;