CREATE DATABASE store_db;

USE store_db;

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE admins (
    admin_id INT PRIMARY KEY,
    FOREIGN KEY (admin_id) REFERENCES users(user_id)
);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    FOREIGN KEY (customer_id) REFERENCES users(user_id)
);

CREATE TABLE vendors (
    vendor_id INT PRIMARY KEY,
    FOREIGN KEY (vendor_id) REFERENCES users(user_id)
);

CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100),
    description TEXT,
    warranty_period INT,
    price DECIMAL(10,2),
    discount_price DECIMAL(10,2),
    discount_deadline DATETIME,
    vendor_id INT NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors (vendor_id)
);

CREATE TABLE carts (
    cart_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL UNIQUE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_status VARCHAR(50),
    ordered_at DATETIME,
    delivered_at DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    customer_id INT NOT NULL,
    rating INT,
    description TEXT,
    image TEXT,
    date DATETIME,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE returns (
    return_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100),
    date DATETIME,
    description TEXT,
    demand TEXT,
    status VARCHAR(50),
    images TEXT,
    customer_id INT NOT NULL,
    order_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE product_images (
    Image_id INT PRIMARY KEY AUTO_INCREMENT,
    Product_id INT,
    image_url TEXT,
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);


CREATE TABLE product_variants (
    variant_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    variant_size VARCHAR(20),
    variant_color VARCHAR(20),
    variant_stock INT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE order_items (
    order_id INT,
    variant_id INT,
    quantity INT,
    item_status VARCHAR(50),
    PRIMARY KEY (order_id, variant_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (variant_id) REFERENCES product_variants (variant_id)
);

CREATE TABLE cart_items (
    cart_id INT,
    variant_id INT,
    quantity INT,
    PRIMARY KEY (cart_id, variant_id),
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id),
    FOREIGN KEY (variant_id) REFERENCES product_variants (variant_id)
);

CREATE TABLE chats (
    chat_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    vendor_id INT,
    admin_id INT,
    chat_message TEXT,
    image TEXT,
    timestamp DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (admin_id) REFERENCES admins (admin_id)
);


CREATE TABLE order_confirmations (
    order_id INT,
    vendor_id INT,
    status VARCHAR(50),
    PRIMARY KEY (order_id, vendor_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

