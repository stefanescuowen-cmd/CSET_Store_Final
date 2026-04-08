USE store_db;

-- READ

-- Products with vendors
SELECT p.title, u.name AS vendor
FROM products p
JOIN vendors v ON p.vendor_id = v.vendor_id
JOIN users u ON v.vendor_id = u.user_id;

-- Orders with products
SELECT o.order_id, p.title, oi.quantity
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN product_variants pv ON oi.variant_id = pv.variant_id
JOIN products p ON pv.product_id = p.product_id;

-- Customer carts
SELECT c.customer_id, p.title, ci.quantity
FROM carts c
JOIN cart_items ci ON c.cart_id = ci.cart_id
JOIN product_variants pv ON ci.variant_id = pv.variant_id
JOIN products p ON pv.product_id = p.product_id;

-- UPDATE

-- Mark order delivered
UPDATE orders
SET order_status = 'Delivered', delivered_at = NOW()
WHERE order_id = 1;

-- Reduce stock
UPDATE product_variants
SET stock = stock - 1
WHERE variant_id = 1;

-- DELETE

-- Remove item from cart
DELETE FROM cart_items
WHERE cart_id = 1 AND variant_id = 2;

-- Delete a review
DELETE FROM reviews
WHERE review_id = 1;

-- EXTRA INSERT (CREATE)

INSERT INTO products (title, description, price, vendor_id)
VALUES ('Test Product', 'Demo item', 99.99, 8);