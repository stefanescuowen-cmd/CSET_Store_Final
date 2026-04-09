USE store_db;

-- =====================================
-- SEED DATA
-- =====================================

-- USERS
INSERT INTO users (name, email, username, password) VALUES
('Admin One', 'admin1@mail.com', 'admin1', 'pass'),
('Admin Two', 'admin2@mail.com', 'admin2', 'pass'),
('Alice', 'alice@mail.com', 'alice', 'pass'),
('Bob', 'bob@mail.com', 'bob', 'pass'),
('Charlie', 'charlie@mail.com', 'charlie', 'pass'),
('Diana', 'diana@mail.com', 'diana', 'pass'),
('Ethan', 'ethan@mail.com', 'ethan', 'pass'),
('Vendor A', 'vendorA@mail.com', 'vendorA', 'pass'),
('Vendor B', 'vendorB@mail.com', 'vendorB', 'pass'),
('Vendor C', 'vendorC@mail.com', 'vendorC', 'pass');

-- ROLES
INSERT INTO admins VALUES (1), (2);
INSERT INTO customers VALUES (3), (4), (5), (6), (7);
INSERT INTO vendors VALUES (8), (9), (10);

-- PRODUCTS
INSERT INTO products (title, description, warranty_period, price, discount_price, discount_deadline, vendor_id) VALUES
('Laptop', 'Gaming laptop', 24, 1200, 1000, NULL, 8),
('Mouse', 'Wireless mouse', 12, 50, 40, '2026-05-01', 8),
('Keyboard', 'Mechanical keyboard', 12, 100, NULL, NULL, 9),
('Monitor', '4K Monitor', 24, 400, 350, '2026-04-20', 9),
('Phone', 'Smartphone', 12, 800, NULL, NULL, 10),
('Headphones', 'Noise cancelling', 12, 200, 150, NULL, 10),
('Tablet', 'Android tablet', 12, 300, NULL, NULL, 8),
('Camera', 'DSLR camera', 24, 900, NULL, NULL, 9),
('Speaker', 'Bluetooth speaker', 12, 120, 90, '2026-04-25', 10),
('Watch', 'Smartwatch', 12, 250, NULL, NULL, 8);

-- VARIANTS
INSERT INTO product_variants (product_id, size, color, stock) VALUES
(1, '15-inch', 'Black', 10),
(2, 'Standard', 'White', 50),
(3, 'Full', 'RGB', 30),
(4, '27-inch', 'Black', 20),
(5, '128GB', 'Blue', 25),
(6, 'Standard', 'Black', 40),
(7, '10-inch', 'Gray', 15),
(8, 'Standard', 'Black', 10),
(9, 'Standard', 'Blue', 35),
(10, 'Standard', 'Black', 20);

-- IMAGES
INSERT INTO product_images (product_id, image_url) VALUES
(1, 'laptop_front.jpg'),
(1, 'laptop_back.jpg'),
(2, 'mouse_top.jpg'),
(2, 'mouse_side.jpg'),
(4, 'monitor_front.jpg'),
(4, 'monitor_side.jpg');

-- CARTS
INSERT INTO carts (customer_id) VALUES (3), (4), (5);

INSERT INTO cart_items (cart_id, variant_id, quantity) VALUES
(1, 1, 2),
(1, 2, 1),
(2, 3, 1),
(3, 5, 2);

-- ORDERS
INSERT INTO orders (customer_id, order_status, ordered_at, delivered_at) VALUES
(3, 'Processing', NOW(), NULL),
(4, 'Shipped', NOW(), NULL),
(5, 'Delivered', NOW(), NOW()),
(6, 'Cancelled', NOW(), NULL),
(7, 'Delivered', NOW(), NOW()),
(3, 'Delivered', NOW(), NOW()),
(4, 'Pending', NOW(), NULL);

-- ORDER ITEMS
INSERT INTO order_items VALUES
(1, 1, 1, 'Processing'),
(1, 3, 1, 'Processing'),
(2, 2, 2, 'Shipped'),
(3, 4, 1, 'Delivered'),
(3, 5, 1, 'Delivered'),
(5, 6, 1, 'Delivered'),
(6, 7, 1, 'Delivered'),
(7, 1, 1, 'Pending'),
(7, 4, 2, 'Pending');

-- ORDER CONFIRMATIONS
INSERT INTO order_confirmations VALUES
(1, 8, 'Confirmed'),
(1, 9, 'Confirmed'),
(3, 10, 'Confirmed');

-- REVIEWS
INSERT INTO reviews (product_id, customer_id, rating, description, image, date) VALUES
(4, 5, 5, 'Amazing monitor, very clear display!', 'img1.jpg', NOW()),
(5, 5, 4, 'Good phone but battery could be better.', 'img2.jpg', NOW()),
(6, 7, 5, 'Excellent sound quality!', 'img3.jpg', NOW());

-- RETURNS
INSERT INTO returns (title, description, demand, status, customer_id, order_id, variant_id, images)
VALUES ('Damaged item', 'Screen cracked', 'Return', 'Pending', 3, 1, 1, 'img_damaged.jpg');

-- CHATS
INSERT INTO chats (customer_id, vendor_id, admin_id, text, image, timestamp) VALUES
(5, 9, NULL, 'My monitor arrived damaged.', NULL, NOW()),
(5, NULL, 1, 'I need help with return process.', NULL, NOW()),
(3, 8, NULL, 'Is the laptop still in stock?', NULL, NOW()),
(4, 10, NULL, 'When will my order ship?', NULL, NOW());

-- Create wishlists for customers
INSERT INTO wishlists (customer_id) VALUES (3), (4);

-- Add items to wishlists using correct wishlist IDs
INSERT INTO wishlist_items (wishlist_id, variant_id)
SELECT wishlist_id, 2 FROM wishlists WHERE customer_id = 3;

INSERT INTO wishlist_items (wishlist_id, variant_id)
SELECT wishlist_id, 3 FROM wishlists WHERE customer_id = 3;

INSERT INTO wishlist_items (wishlist_id, variant_id)
SELECT wishlist_id, 5 FROM wishlists WHERE customer_id = 4;


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
JOIN vendors v ON p.vendor_id = v.vendor_id
JOIN users u ON v.vendor_id = u.user_id;

-- Search by name or description
SELECT * FROM products WHERE title LIKE '%phone%';
SELECT * FROM products WHERE description LIKE '%gaming%';

-- Search by vendor dynamically
SELECT * FROM products WHERE vendor_id = (SELECT vendor_id FROM vendors WHERE user_id = 8);

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
SELECT c.cart_id, pv.variant_id, 2
FROM carts c
JOIN product_variants pv ON pv.variant_id = 1
WHERE c.customer_id = 3;

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

INSERT INTO order_items (order_id, variant_id, quantity, status)
VALUES (@new_order_id, 1, 2, 'Pending');

-- Confirm order dynamically
UPDATE order_confirmations oc
JOIN orders o ON oc.order_id = o.order_id
SET oc.status = 'Confirmed'
WHERE o.customer_id = 3 AND oc.vendor_id = 8;

-- Update order status dynamically
UPDATE orders o
SET o.order_status = 'Shipped'
WHERE o.customer_id = 3 AND o.order_status = 'Pending';

-- Mark delivered dynamically
UPDATE orders o
SET o.order_status = 'Delivered', delivered_at = NOW()
WHERE o.customer_id = 3 AND o.order_status = 'Shipped';

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
INSERT INTO reviews (product_id, customer_id, rating, description)
VALUES (1, 3, 5, 'Great product');

-- Get reviews for product or by customer
SELECT * FROM reviews WHERE product_id = 1;
SELECT * FROM reviews WHERE customer_id = 3;

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
JOIN product_variants pv ON r.variant_id = pv.variant_id
JOIN products p ON pv.product_id = p.product_id
SET r.status = 'Rejected'
WHERE r.demand = 'Warranty'
  AND DATE_ADD(r.date, INTERVAL p.warranty_period MONTH) < NOW();

-- Auto-reject if after 7 days
UPDATE returns r
JOIN orders o ON r.order_id = o.order_id
SET r.status = 'Rejected'
WHERE r.demand IN ('Return','Refund') AND DATEDIFF(NOW(), o.delivered_at) > 7;

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