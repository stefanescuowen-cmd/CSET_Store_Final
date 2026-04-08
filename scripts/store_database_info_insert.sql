INSERT INTO users (name, email, username, password) 
VALUES 
    ('Admin User', 'admin@example.com', 'admin', 'pass123'),
    ('Admin 2', 'admin2@example.com', 'admin2', 'pass456'),
    ('John Doe', 'john.doe@example.com', 'johndoe', 'pass012'),
    ('Jane Smith', 'jane.smith@example.com', 'janesmith', 'pass345'),
    ('Richard Roe', 'richard.roe@example.com', 'richardroe', 'pass456'),
    ('Vendor One', 'vendor1@example.com', 'vendor1', 'pass678'),
    ('Vendor Two', 'vendor2@example.com', 'vendor2', 'pass901');

INSERT INTO admins (admin_id) 
VALUES 
    (1),
    (2);

INSERT INTO customers (customer_id)
VALUES 
    (3),
    (4),
    (5);

INSERT INTO vendors (vendor_id)
VALUES
    (6),
    (7);

INSERT INTO products (title, description, warranty_period, price, discount_price, discount_deadline, vendor_id)
VALUES
    ('Smartphone', 'A high-end smartphone with a great camera.', 24, 699.99, 599.99, NULL, 6),
    ('Laptop', 'A powerful laptop for work and gaming.', 36, 1299.99, 1099.99, NULL, 7),
    ('Headphones', 'Noise-cancelling over-ear headphones.', 12, 199.99, NULL, NULL, 6),
    ('Smartwatch', 'A smartwatch with fitness tracking features.', 18, 249.99, 199.99, '2026-10-31 23:59:59', 7),
    ('Tablet', 'A lightweight tablet for entertainment and productivity.', 24, 499.99, 449.99, '2026-12-15 23:59:59', 6),
    ('Gaming Console', 'A next-gen gaming console with stunning graphics.', 36, 499.99, NULL, NULL, 7),
    ('Wireless Earbuds', 'Compact wireless earbuds with great sound quality.', 12, 149.99, 129.99, '2026-11-30 23:59:59', 6),
    ('4K Monitor', 'A 27-inch 4K monitor for professionals and gamers.', 24, 399.99, NULL, NULL, 7),
    ('External Hard Drive', 'A 2TB external hard drive for backup and storage.', 36, 89.99, NULL, NULL, 6),
    ('Bluetooth Speaker', 'A portable Bluetooth speaker with deep bass.', 12, 59.99, 49.99, '2026-10-31 23:59:59', 7),
    ('Fitness Tracker', 'A fitness tracker with heart rate monitoring.', 18, 99.99, 79.99, '2026-11-30 23:59:59', 6),
    ('E-reader', 'A lightweight e-reader with a high-resolution display.', 24, 129.99, NULL, NULL, 7),
    ('Smart Home Hub', 'A smart home hub to control all your devices.', 36, 149.99, NULL, NULL, 6),
    ('Action Camera', 'A rugged action camera for outdoor adventures.', 12, 299.99, NULL, NULL, 7),
    ('VR Headset', 'An immersive VR headset for gaming and entertainment.', 24, 399.99, 349.99, '2026-11-30 23:59:59', 6);

INSERT INTO product_images (product_id, image_url)
VALUES
    (1, 'https://example.com/images/smartphone.jpg'),
    (2, 'https://example.com/images/laptop.jpg'),
    (3, 'https://example.com/images/headphones.jpg'),
    (4, 'https://example.com/images/smartwatch.jpg'),
    (5, 'https://example.com/images/tablet.jpg'),
    (6, 'https://example.com/images/gaming_console.jpg'),
    (7, 'https://example.com/images/wireless_earbuds.jpg'),
    (8, 'https://example.com/images/4k_monitor.jpg'),
    (9, 'https://example.com/images/external_hard_drive.jpg'),
    (10, 'https://example.com/images/bluetooth_speaker.jpg'),
    (11, 'https://example.com/images/fitness_tracker.jpg'),
    (12, 'https://example.com/images/e_reader.jpg'),
    (13, 'https://example.com/images/smart_home_hub.jpg'),
    (14, 'https://example.com/images/action_camera.jpg'),
    (15, 'https://example.com/images/vr_headset.jpg');

INSERT INTO product_variants (product_id, variant_size, variant_color, variant_stock)
VALUES
    (1, 'Color', 'Black', 10),
    (1, 'Color', 'White', 15),
    (2, 'RAM', '16GB', 5),
    (2, 'RAM', '32GB', 8),
    (3, 'Color', 'Red', 20),
    (3, 'Color', 'Blue', 25),
    (4, 'Band Material', 'Silicone', 30),
    (4, 'Band Material', 'Leather', 35),
    (5, 'Storage', '64GB', 40),
    (5, 'Storage', '128GB', 45),
    (6, 'Color', 'Black', 12),
    (6, 'Color', 'White', 18),
    (7, 'Color', 'Black', 22),
    (7, 'Color', 'White', 28),
    (8, 'Size', '27-inch', 10),
    (8, 'Size', '32-inch', 15),
    (9, 'Capacity', '2TB', 20),
    (9, 'Capacity', '4TB', 25),
    (10, 'Color', 'Black', 30),
    (10, 'Color', 'Blue', 35),
    (11, 'Color', 'Black', 40),
    (11, 'Color', 'White', 45),
    (12, 'Storage', '8GB', 50),
    (12, 'Storage', '16GB', 55),
    (13, 'Color', 'Black', 60),
    (13, 'Color', 'White', 65),
    (14, 'Color', 'Black', 70),
    (14, 'Color', 'Red', 75),
    (15, 'Color', 'Black', 80),
    (15, 'Color', 'White', 85);

INSERT INTO carts (customer_id)
VALUES
    (3),
    (4),
    (5);

INSERT INTO cart_items (cart_id, variant_id, quantity)
VALUES
    (1, 1, 1),
    (1, 3, 2),
    (2, 2, 1),
    (2, 4, 1),
    (3, 5, 1),
    (3, 6, 1);

INSERT INTO orders (customer_id, order_status, ordered_at, delivered_at)
VALUES
    (3, 'Processing', '2026-09-01 10:00:00', NULL),
    (4, 'Shipped', '2026-08-25 14:30:00', NULL),
    (5, 'Shipped', '2026-08-20 09:15:00', NULL),
    (3, 'Shipped', '2026-08-20 12:15:00', NULL),
    (5, 'Delivered', '2026-08-20 09:15:00', '2026-08-27 16:45:00');

INSERT INTO order_items (order_id, variant_id, quantity, item_status)
VALUES
    (1, 1, 1, 'Pending'),
    (1, 3, 2, 'Pending'),
    (2, 2, 1, 'Confirmed'),
    (2, 4, 1, 'Confirmed'),
    (3, 5, 1, 'Shipped'),
    (3, 6, 1, 'Shipped'),
    (4, 7, 1, 'Shipped'),
    (4, 8, 1, 'Shipped'),
    (5, 9, 1, 'Delivered'),
    (5, 10, 2, 'Delivered');

INSERT INTO reviews (product_id, customer_id, rating, description, image, date)
VALUES
    (1, 3, 5, 'Amazing smartphone with excellent camera quality!', NULL, '2026-09-05 12:00:00'),
    (2, 4, 4, 'Great laptop for work, but a bit heavy for gaming.', NULL, '2026-08-30 15:45:00'),
    (3, 5, 3, 'Decent headphones but not very comfortable for long use.', NULL, '2026-08-28 11:20:00'),
    (4, 3, 5, 'Love this smartwatch! It has all the features I need.', NULL, '2026-09-10 09:30:00');

INSERT INTO returns (title, date, description, demand, status, images, customer_id, order_id)
VALUES
    ('Defective Smartphone', '2026-09-15 14:00:00', 'The smartphone I received has a defective camera.', 'Refund', 'Pending', NULL, 3, 1),
    ('Wrong Laptop Model', '2026-08-31 10:30:00', 'I received the wrong laptop model than what I ordered.', 'Exchange', 'Approved', NULL, 4, 2),
    ('Headphones Not Comfortable', '2026-08-29 16:45:00', 'The headphones are not comfortable for long use.', 'Refund', 'Rejected', NULL, 5, 3);

INSERT INTO chats (customer_id, vendor_id, admin_id, chat_message, image, timestamp)
VALUES
    (3, 6, NULL, 'Hi, I have a question about the smartphone I ordered.', NULL, '2026-09-01 11:00:00'),
    (5, 7, NULL, 'Sure! What would you like to know?', NULL, '2026-09-01 11:05:00'),
    (3, 6, NULL, 'Is the smartphone compatible with all carriers?', NULL, '2026-09-01 11:10:00'),
    (5, 7, NULL, 'Yes, it is compatible with all major carriers.', NULL, '2026-09-01 11:15:00'),
    (4, 7, NULL, 'Hello, I have a question about the laptop I ordered.', NULL, '2026-08-25 15:00:00'),
    (3, NULL, 1, 'Hi! What can I help you with?', NULL, '2026-08-25 15:05:00'),
    (4, 7, NULL, 'I received the wrong laptop model. Can I exchange it?', NULL, '2026-08-25 15:10:00'),
    (3, 6, NULL, 'I apologize for the inconvenience. We will arrange an exchange for you.', NULL, '2026-08-25 15:15:00'),
    (5, NULL, 2, 'Hi, I have a question about the headphones I ordered.', NULL, '2026-08-28 12:00:00'),
    (5, 7, NULL, 'Hello! What can I assist you with?', NULL, '2026-08-28 12:05:00'),
    (5, 6, NULL, 'The headphones are not comfortable for long use. Can I return them?', NULL, '2026-08-28 12:10:00'),
    (4, NULL, 2, 'I am sorry to hear that. We will process your return request.', NULL, '2026-08-28 12:15:00'),
    (3, NULL, 2, 'I would like to return the defective smartphone. What is the process?', NULL, '2026-09-15 14:30:00'),
    (3, 7, NULL, 'Please send the smartphone back to us and we will issue a refund once we receive it.', NULL, '2026-09-15 14:45:00'),
    (4, 7, NULL, 'I have sent the wrong laptop back. When can I expect the exchange?', NULL, '2026-09-05 10:00:00'),
    (5, 6, NULL, 'We have received the returned laptop and will ship the correct model to you within 3 business days.', NULL, '2026-09-05 10:15:00'),
    (5, 6, NULL, 'I have sent the headphones back. When can I expect the refund?', NULL, '2026-08-30 09:00:00'),
    (4, NULL, 1, 'We have received the returned headphones and will process your refund within 5 business days.', NULL, '2026-08-30 09:15:00'),
    (3, NULL, 2, 'I have sent the defective smartphone back. When can I expect the refund?', NULL, '2026-09-20 14:00:00'),
    (4, 6, NULL, 'We have received the returned smartphone and will process your refund within 5 business days.', NULL, '2026-09-20 14:15:00');