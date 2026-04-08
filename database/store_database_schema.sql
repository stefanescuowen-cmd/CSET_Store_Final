CREATE DATABASE store_db;

USE store_db;

-- USERS
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
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
    vendor_id INT PRIMARY KEY,
    FOREIGN KEY (vendor_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- PRODUCTS
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100),
    description TEXT,
    warranty_period INT,
    price DECIMAL(10,2) NOT NULL,
    discount_price DECIMAL(10,2),
    discount_deadline DATETIME,
    vendor_id INT NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE
);

-- PRODUCT IMAGES (FIXED)
CREATE TABLE product_images (
    image_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    url TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- PRODUCT VARIANTS
CREATE TABLE product_variants (
    variant_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    size VARCHAR(20),
    color VARCHAR(20),
    stock INT CHECK (stock >= 0),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- CARTS
CREATE TABLE carts (
    cart_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL UNIQUE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

CREATE TABLE cart_items (
    cart_id INT,
    variant_id INT,
    quantity INT,
    PRIMARY KEY (cart_id, variant_id),
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE CASCADE
);

-- ORDERS
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_status ENUM('Pending','Processing','Shipped','Delivered','Cancelled'),
    ordered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivered_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- ORDER ITEMS (MULTI-VENDOR SUPPORT)
CREATE TABLE order_items (
    order_id INT,
    variant_id INT,
    quantity INT,
    item_status VARCHAR(50),
    PRIMARY KEY (order_id, variant_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (variant_id) REFERENCES product_variants(variant_id) ON DELETE CASCADE
);

-- ORDER CONFIRMATIONS (PER VENDOR)
CREATE TABLE order_confirmations (
    order_id INT,
    vendor_id INT,
    status VARCHAR(50),
    PRIMARY KEY (order_id, vendor_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE
);

-- REVIEWS (FIXED)
CREATE TABLE reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    description TEXT,
    image TEXT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- RETURNS / WARRANTY
CREATE TABLE returns (
    return_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100),
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    demand TEXT,
    status VARCHAR(50),
    images TEXT,
    customer_id INT NOT NULL,
    order_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);

-- CHATS
CREATE TABLE chats (
    chat_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    vendor_id INT,
    admin_id INT,
    text TEXT,
    image TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES admins(admin_id) ON DELETE CASCADE
);