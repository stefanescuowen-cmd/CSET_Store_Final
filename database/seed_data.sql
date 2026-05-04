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
INSERT INTO products (title, description, warranty_period, price, discount_price, discount_deadline, vendor_id, category) VALUES
('Laptop', 'Gaming laptop with high-performance specs', 24, 1200, 1000, NULL, 8, 'Computers'),
('Mouse', 'Wireless ergonomic mouse', 12, 50, 40, '2026-05-01', 8, 'Accessories'),
('Keyboard', 'Mechanical RGB keyboard', 12, 100, NULL, NULL, 9, 'Accessories'),
('Monitor', '4K UHD Monitor', 24, 400, 350, '2026-04-20', 9, 'Monitors'),
('Phone', 'Latest flagship smartphone', 12, 800, NULL, NULL, 10, 'Phones'),
('Headphones', 'Active noise-cancelling headphones', 12, 200, 150, NULL, 10, 'Audio'),
('Tablet', '10-inch Android tablet', 12, 300, NULL, NULL, 8, 'Tablets'),
('Camera', 'DSLR camera with 18-55mm lens', 24, 900, NULL, NULL, 9, 'Cameras'),
('Speaker', 'Waterproof Bluetooth speaker', 12, 120, 90, '2026-04-25', 10, 'Audio'),
('Watch', 'Smartwatch with heart rate monitor', 12, 250, NULL, NULL, 8, 'Wearables');

-- VARIANTS
INSERT INTO product_variants (product_id, size, color, stock) VALUES
(1, '15-inch', 'Black', 10),
(1, '17-inch', 'Silver', 5),
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
(1, '/static/images/products/laptop.jpg'),
(1, '/static/images/products/laptop-2.jpg'),
(2, '/static/images/products/white-mouse.webp'),
(3, '/static/images/products/keyboard.jpg'),
(4, '/static/images/products/monitor.jpg'),
(5, '/static/images/products/phone-blue.jpg'),
(6, '/static/images/products/headphones.jpg'),
(7, '/static/images/products/tablet.jpg'),
(8, '/static/images/products/camera.jpg'),
(9, '/static/images/products/speaker.jpg'),
(10, '/static/images/products/smartwatch.jpg');

-- CARTS
INSERT INTO carts (customer_id) VALUES (3), (4), (5);

INSERT INTO cart_items (cart_id, variant_id, quantity) VALUES
(1, 1, 2),
(1, 2, 1),
(2, 3, 1),
(3, 5, 2);

-- ADDRESSES
INSERT INTO addresses (user_id, receiver_name, contact_number, address_line1, address_line2, city, state, zip_code, address_type, is_default) VALUES
(3, 'Alice Smith', '555-0101', '123 Maple Ave', 'Apt 4B', 'Lancaster', 'PA', '17603', 'Home', TRUE),
(3, 'Alice Smith', '555-0102', 'Tech Hub Plaza', 'Suite 200', 'Philadelphia', 'PA', '19104', 'Office', FALSE),
(4, 'Robert Miller', '555-0202', '456 Oak Lane', NULL, 'Lancaster', 'PA', '17601', 'Home', TRUE);

-- ORDERS
INSERT INTO orders (customer_id, order_status, total_price, ordered_at, delivered_at) VALUES
(3, 'Confirmed', 120.50, NOW(), NULL),
(4, 'Shipped', 85.00, NOW(), NULL),
(5, 'Delivered', 210.00, NOW(), NOW()),
(6, 'Cancelled', 45.00, NOW(), NULL),
(7, 'Handed to delivery partner', 300.00, NOW(), NULL),
(3, 'Delivered', 95.50, NOW(), NOW()),
(4, 'Pending', 15.00, NOW(), NULL),
(5, 'Shipped', 130.00, NOW(), NULL),
(6, 'Shipped', 75.00, NOW(), NULL),
(3, 'Cancelled', 55.00, NOW(), NULL);

-- ORDER ITEMS
INSERT INTO order_items (order_id, variant_id, quantity, item_status) VALUES
(1, 1, 1, 'Confirmed'),
(1, 3, 1, 'Confirmed'),
(2, 2, 2, 'Shipped'),
(3, 4, 1, 'Delivered'),
(3, 5, 1, 'Delivered'),
(5, 6, 1, 'Handed to delivery partner'),
(6, 7, 1, 'Delivered'),
(7, 1, 1, 'Pending'),
(7, 4, 2, 'Pending'),
(8, 2, 1, 'Shipped'),
(8, 3, 1, 'Shipped'),
(9, 5, 2, 'Shipped'),
(9, 3, 1, 'Shipped'),
(10, 1, 1, 'Cancelled');

-- ORDER CONFIRMATIONS
INSERT INTO order_confirmations (order_id, variant_id, vendor_id, status) VALUES
(1, 1, 8, 'Confirmed'),
(1, 3, 9, 'Confirmed'),
(3, 4, 9, 'Confirmed');

-- REVIEWS
INSERT INTO reviews (product_id, customer_id, rating, description, image, date) VALUES
(5, 5, 5, 'Amazing monitor, very clear display!', 'img1.jpg', NOW()),
(6, 5, 4, 'Good phone but battery could be better.', 'img2.jpg', NOW()),
(8, 3, 3, 'Tablet is okay for the price.', 'img4.jpg', NOW());

-- RETURNS

INSERT INTO returns (title, description, demand, status, customer_id, order_id, variant_id, images)
VALUES 
-- Laptop (Variant 1)
('Damaged Laptop', 'Screen flickers on arrival', 'Return', 'Pending', 3, 1, 1, 'img_damaged.jpg'),

-- Monitor (Variant 5) - Fixed from 4 to 5
('Monitor Display', 'Dead pixels after one day', 'Warranty', 'Processing', 5, 3, 5, 'img_warranty.jpg'),

-- Laptop 17-inch (Variant 2)
('Wrong Size', 'Ordered 15-inch, received 17-inch', 'Refund', 'Pending', 4, 2, 2, 'img_refund.jpg'),

-- Tablet (Variant 8) - Fixed from 7 to 8
('Tablet Defective', 'Will not charge', 'Return', 'Pending', 3, 6, 8, 'img_tablet.jpg');

-- CHATS
INSERT INTO chats (sender_id, customer_id, vendor_id, admin_id, return_id, text, image, timestamp) VALUES
(3, 3, NULL, 2, 1, 'My phone screen is cracked.', NULL, NOW()),
(4, 4, 8, NULL, NULL, 'When will the monitor be back in stock?', NULL, NOW()),
(5, 5, 9, NULL, NULL, 'I need help with my order.', NULL, NOW()),
(5, 5, NULL, 1, 4, 'My monitor arrived damaged.', NULL, NOW()),
(5, 5, NULL, 1, 2, 'I need help with return process.', NULL, NOW()),
(6, 6, 10, NULL, NULL, 'Is the tablet still in stock?', NULL, NOW()),
(7, 7, 8, NULL, NULL, 'When will my order ship?', NULL, NOW());

-- Create wishlists for customers
INSERT INTO wishlists (customer_id) VALUES (3), (4);

-- Add items to wishlists using correct wishlist IDs
INSERT INTO wishlist_items (wishlist_id, variant_id)
SELECT wishlist_id, 2 FROM wishlists WHERE customer_id = 3;

INSERT INTO wishlist_items (wishlist_id, variant_id)
SELECT wishlist_id, 3 FROM wishlists WHERE customer_id = 3;

INSERT INTO wishlist_items (wishlist_id, variant_id)
SELECT wishlist_id, 5 FROM wishlists WHERE customer_id = 4;