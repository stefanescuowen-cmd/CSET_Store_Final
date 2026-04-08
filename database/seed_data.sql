USE store_db;

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

INSERT INTO cart_items VALUES
(1, 1, 1),
(1, 2, 2),
(2, 3, 1),
(3, 5, 1);

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