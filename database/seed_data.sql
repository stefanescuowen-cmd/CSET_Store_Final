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
(6, 7, 1, 'Delivered');

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
INSERT INTO returns (title, date, description, demand, status, images, customer_id, order_id) VALUES
('Broken Screen', NOW(), 'Screen cracked after delivery', 'Replacement', 'In Progress', 'img4.jpg', 5, 3);

-- CHATS
INSERT INTO chats (customer_id, vendor_id, admin_id, text, image, timestamp) VALUES
(5, 9, NULL, 'My monitor arrived damaged.', NULL, NOW()),
(5, NULL, 1, 'I need help with return process.', NULL, NOW()),
(3, 8, NULL, 'Is the laptop still in stock?', NULL, NOW()),
(4, 10, NULL, 'When will my order ship?', NULL, NOW());

-- WISHLIST DATA
INSERT INTO wishlists (customer_id) VALUES (3), (4);

INSERT INTO wishlist_items VALUES
(1, 2),
(1, 3),
(2, 5);

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

-- Filter by price range
SELECT p.*
FROM products p
JOIN product_variants pv ON p.product_id = pv.product_id
WHERE pv.stock > 0 AND COALESCE(p.discount_price, p.price) BETWEEN 50 AND 500;

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
INSERT INTO order_items VALUES (1, 1, 2, 'Pending');

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
INSERT INTO returns (title, description, demand, status, customer_id, order_id)
VALUES ('Damaged item', 'Screen cracked', 'Return', 'Pending', 3, 1);

-- Update return status
UPDATE returns
SET status = 'Processing'
WHERE return_id = 1;

-- Automatically reject if warranty expired
UPDATE returns r
JOIN products p ON p.product_id = r.product_id
SET r.status = 'Rejected'
WHERE r.demand = 'Warranty' AND DATE_ADD(r.date, INTERVAL p.warranty_period MONTH) < NOW();

-- Automatically reject if return/refund after 7 days
UPDATE returns r
JOIN orders o ON r.order_id = o.order_id
SET r.status = 'Rejected'
WHERE r.demand IN ('Return', 'Refund') AND DATEDIFF(NOW(), o.delivered_at) > 7;

-- ===========
-- CHAT SYSTEM
-- ===========

-- Send message to vendor
INSERT INTO chats (customer_id, vendor_id, text)
VALUES (3, 8, 'Hello, is this available?');

-- Get messages sent to a vendor
SELECT * FROM chats WHERE vendor_id = 8;

-- Get messages sent by a customer
SELECT * FROM chats WHERE customer_id = 3;

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