USE store_db;

-- =====================================
-- AUTHENTICATION (Registration / Login)
-- =====================================

-- Check if user already exists
SELECT * FROM users WHERE email = 'alice@mail.com' OR username = 'alice';

-- Register new user
INSERT INTO users (name, email, username, password)
VALUES ('Test User', 'test@mail.com', 'testuser', 'pass');

-- Login using username
SELECT * FROM users
WHERE username = 'alice' AND password = 'pass';

-- Login using email
SELECT * FROM users
WHERE email = 'alice@mail.com' AND password = 'pass';

-- =================================
-- PRODUCTS (READ / SEARCH / FILTER)
-- =================================

-- View products with vendor names
SELECT p.title, u.name AS vendor
FROM products p
JOIN users u ON p.vendor_id = u.user_id;

-- Search by name or description
SELECT * FROM products WHERE title LIKE '%phone%';
SELECT * FROM products WHERE description LIKE '%gaming%';

-- Search by vendor dynamically
SELECT * FROM products WHERE vendor_id = (SELECT vendor_id FROM vendors WHERE vendor_id = 8);

-- Filter by variant properties
SELECT p.*
FROM products p
JOIN product_variants v ON p.product_id = v.product_id
WHERE v.color = 'Black';

SELECT p.*
FROM products p
JOIN product_variants v ON p.product_id = v.product_id
WHERE v.size = '15-inch';

-- Filter by stock
SELECT p.*
FROM products p
JOIN product_variants v ON p.product_id = v.product_id
WHERE v.stock > 0;

-- Filter by price range
SELECT p.*
FROM products p
JOIN product_variants pv ON p.product_id = pv.product_id
WHERE pv.stock > 0
  AND COALESCE(p.discount_price, p.price) BETWEEN 50 AND 500;

-- ======================
-- CART (CRUD OPERATIONS)
-- ======================

-- Add item to cart dynamically
INSERT INTO cart_items (cart_id, variant_id, quantity)
VALUES (1, 1, 2)
ON DUPLICATE KEY UPDATE quantity = quantity + 2;

-- View cart contents
SELECT c.customer_id, p.title, ci.quantity
FROM carts c
JOIN cart_items ci ON c.cart_id = ci.cart_id
JOIN product_variants pv ON ci.variant_id = pv.variant_id
JOIN products p ON pv.product_id = p.product_id;

-- Update item quantity dynamically
UPDATE cart_items ci
JOIN carts c ON ci.cart_id = c.cart_id
SET ci.quantity = 3
WHERE c.customer_id = 3 AND ci.variant_id = 1;

-- Remove item dynamically
DELETE ci
FROM cart_items ci
JOIN carts c ON ci.cart_id = c.cart_id
WHERE c.customer_id = 3 AND ci.variant_id = 2;

-- ==========================
-- WISHLIST (CRUD OPERATIONS)
-- ==========================

-- Create wishlist for a customer
INSERT INTO wishlists (customer_id) VALUES (5);

-- Add items dynamically
INSERT INTO wishlist_items (wishlist_id, variant_id)
SELECT wishlist_id, 6 FROM wishlists WHERE customer_id = 5;

-- View wishlist items for a customer
SELECT wi.*
FROM wishlist_items wi
JOIN wishlists w ON wi.wishlist_id = w.wishlist_id
WHERE w.customer_id = 3;

-- Remove wishlist item dynamically
DELETE wi
FROM wishlist_items wi
JOIN wishlists w ON wi.wishlist_id = w.wishlist_id
WHERE w.customer_id = 3 AND wi.variant_id = 2;

-- ======
-- ORDERS
-- ======

-- View orders with product details
SELECT o.order_id, p.title, oi.quantity
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN product_variants pv ON oi.variant_id = pv.variant_id
JOIN products p ON pv.product_id = p.product_id;

-- Place new order dynamically
INSERT INTO orders (customer_id, order_status) VALUES (3, 'Pending');
SET @new_order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, variant_id, quantity, item_status)
VALUES (@new_order_id, 1, 2, 'Pending');

-- Confirm order dynamically
INSERT INTO order_confirmations (order_id, variant_id, vendor_id, status)
VALUES (1, 1, 8, 'Confirmed');

-- Update order status dynamically
UPDATE orders o
SET o.order_status = 'Shipped'
WHERE o.order_id = 1 AND o.customer_id = 3 AND o.order_status = 'Pending';

-- Mark delivered dynamically
UPDATE orders o
SET o.order_status = 'Delivered', delivered_at = NOW()
WHERE o.order_id = 1 AND o.customer_id = 3 AND o.order_status = 'Shipped';

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

-- Create review
INSERT INTO reviews (variant_id, customer_id, rating, description)
VALUES (1, 3, 5, 'Great product');

-- Get reviews for product or by customer
SELECT r.rating, r.description, r.date, u.name AS customer
FROM reviews r
JOIN customers c ON r.customer_id = c.customer_id
JOIN users u ON c.customer_id = u.user_id
WHERE r.variant_id = 1;

SELECT r.rating, r.description, r.date, u.name AS customer
FROM reviews r
JOIN customers c ON r.customer_id = c.customer_id
JOIN users u ON c.customer_id = u.user_id
WHERE c.customer_id = 3;

-- Sort reviews
SELECT * FROM reviews ORDER BY rating DESC;
SELECT * FROM reviews ORDER BY date DESC;

-- Delete dynamically
DELETE FROM reviews WHERE review_id = 1;

-- ==================
-- RETURNS / WARRANTY
-- ==================

-- Create return request
INSERT INTO returns (title, description, demand, status, customer_id, order_id, variant_id)
VALUES ('Damaged item', 'Screen cracked', 'Return', 'Pending', 3, 1, 1);

-- Update return status
UPDATE returns SET status = 'Processing' WHERE return_id = 1;

-- Auto-reject if warranty expired
UPDATE returns r
JOIN orders o ON r.order_id = o.order_id
JOIN product_variants pv ON r.variant_id = pv.variant_id
JOIN products p ON pv.product_id = p.product_id
SET r.status = 'Rejected'
WHERE r.return_id > 0
  AND r.demand = 'Warranty'
  AND o.delivered_at IS NOT NULL
  AND DATE_ADD(r.date, INTERVAL p.warranty_period MONTH) < NOW();

-- Auto-reject if after 7 days
UPDATE returns r
JOIN orders o ON r.order_id = o.order_id
SET r.status = 'Rejected'
WHERE r.order_id IS NOT NULL
  AND r.demand IN ('Return','Refund') AND DATEDIFF(NOW(), o.delivered_at) > 7;

-- ===========
-- CHAT SYSTEM
-- ===========

-- Send message dynamically
INSERT INTO chats (customer_id, vendor_id, admin_id, return_id, text, image, timestamp)
VALUES
(5, 9, NULL, NULL, 'My monitor arrived damaged.', NULL, NOW()),
(5, NULL, 1, NULL, 'I need help with return process.', NULL, NOW()),
(3, 8, NULL, 1, 'Is the laptop still in stock?', NULL, NOW()),
(4, 10, NULL, NULL, 'When will my order ship?', NULL, NOW());

-- Get messages dynamically
SELECT * FROM chats WHERE vendor_id = 8;
SELECT * FROM chats WHERE customer_id = 3;

-- Delete dynamically
DELETE FROM chats WHERE chat_id = 1;

-- =====================
-- ADDITIONAL OPERATIONS
-- =====================

-- Add new product dynamically
INSERT INTO products (title, description, price, vendor_id)
VALUES ('Test Product', 'Demo item', 99.99, 8);

-- Update product pricing dynamically
UPDATE products
SET price = 899.99, discount_price = 799.99
WHERE product_id = 1;