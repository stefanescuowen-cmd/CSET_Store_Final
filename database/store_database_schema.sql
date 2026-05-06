DROP DATABASE IF EXISTS store_db;
CREATE DATABASE store_db;
USE store_db;

-- USERS
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- ROLES
CREATE TABLE admins (
    admin_id INT PRIMARY KEY,
    FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    FOREIGN KEY (customer_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE vendors (
    vendor_id INT PRIMARY KEY AUTO_INCREMENT,
    FOREIGN KEY (vendor_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- PRODUCTS
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    warranty_period INT NOT NULL DEFAULT 12, 
    price DECIMAL(10,2) NOT NULL,
    discount_price DECIMAL(10,2),
    discount_deadline DATETIME,
    vendor_id INT NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    CHECK (discount_price IS NULL OR discount_price < price),
    FULLTEXT(title, description) 
);

CREATE TABLE product_images (
    image_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    image_url TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE TABLE product_variants (
    variant_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    size VARCHAR(20) NOT NULL,
    color VARCHAR(20) NOT NULL,
    stock INT NOT NULL CHECK (stock >= 0),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- CART
CREATE TABLE carts (
    cart_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL UNIQUE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

CREATE TABLE cart_items (
    cart_id INT NOT NULL,
    variant_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (cart_id, variant_id),
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE CASCADE
);

-- Create Orders with the total_price column
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_status ENUM('Pending','Confirmed','Handed to delivery partner','Shipped','Delivered','Cancelled', 'Denied') NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    ordered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivered_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- Create Order Items
CREATE TABLE order_items (
    order_id INT NOT NULL,
    variant_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price_paid DECIMAL(10, 2) NOT NULL,
    item_status ENUM('Pending','Confirmed','Handed to delivery partner','Shipped','Delivered','Cancelled', 'Denied') NOT NULL,
    PRIMARY KEY (order_id, variant_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE CASCADE
);

-- Create Order Confirmations
CREATE TABLE order_confirmations (
    order_id INT,
    vendor_id INT,
    variant_id INT,
    status VARCHAR(50) NOT NULL,
    PRIMARY KEY (order_id, variant_id, vendor_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE CASCADE
);

-- REVIEWS
CREATE TABLE reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    description TEXT NOT NULL,
    image TEXT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (product_id, customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- RETURNS
CREATE TABLE returns (
    return_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL,
    demand ENUM('Return', 'Refund', 'Warranty') NOT NULL,
    status VARCHAR(50) NOT NULL,
    images TEXT,
    customer_id INT NOT NULL,
    order_id INT,
    variant_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE CASCADE
);

-- CHAT
CREATE TABLE chats (
    chat_id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT NOT NULL,
    customer_id INT NOT NULL,
    vendor_id INT,
    admin_id INT,
    return_id INT,
    text TEXT NOT NULL,
    image TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES admins(admin_id) ON DELETE CASCADE,
    FOREIGN KEY (return_id) REFERENCES returns(return_id) ON DELETE CASCADE,
    CHECK (
        (vendor_id IS NOT NULL AND admin_id IS NULL) OR
        (vendor_id IS NULL AND admin_id IS NOT NULL) OR
        (vendor_id IS NOT NULL AND admin_id IS NOT NULL)
    )
);

-- WISHLIST
CREATE TABLE wishlists (
    wishlist_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

CREATE TABLE wishlist_items (
    wishlist_id INT NOT NULL,
    variant_id INT NOT NULL,
    PRIMARY KEY (wishlist_id, variant_id),
    FOREIGN KEY (wishlist_id) REFERENCES wishlists(wishlist_id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE CASCADE
);

-- ADDRESS
CREATE TABLE addresses (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    receiver_name VARCHAR(100) NOT NULL,
    contact_number VARCHAR(20) NOT NULL,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    address_type ENUM('Home', 'Office') DEFAULT 'Home',
    is_default BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);