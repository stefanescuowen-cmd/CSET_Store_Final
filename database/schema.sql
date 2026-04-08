-- Core Tables (Entities)

-- User (base table)
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50),
    name VARCHAR(100),
    email VARCHAR(100) unique,
    password VARCHAR(255)
);

-- Admin (inherits from User)
CREATE TABLE admins (
    admin_id INT PRIMARY KEY,
    FOREIGN KEY (admin_id) REFERENCES users(user_id)
);

-- Customer (inherits from User)
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    FOREIGN KEY (customer_id) REFERENCES users(user_id)
);

-- Vendor (inherits from User)
CREATE TABLE vendors (
    vendor_id INT PRIMARY KEY
    FOREIGN KEY (customer_id) REFERENCES users(user_id)
);

-- Product
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100),
    description TEXT,
    images TEXT,
    warranty_period VARCHAR(50),
    available_inventory INT,
    price DECIMAL(10,2),
    discount_price DECIMAL(10,2),
    discount_time DATETIME
);

-- Cart
CREATE TABLE carts (
    cart_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Order
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    status VARCHAR(50),
    total DECIMAL(10,2),
    date DATETIME,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Review
CREATE TABLE reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    customer_id INT,
    rating INT,
    description TEXT,
    image TEXT,
    date DATETIME,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Return
CREATE TABLE returns (
    return_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100),
    date DATETIME,
    description TEXT,
    demand TEXT,
    status VARCHAR(50),
    images TEXT,
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- Product Images
CREATE TABLE product_images (
    Image_id INT PRIMARY KEY AUTO_INCREMENT,
    FOREIGN KEY (Product_id) REFERENCES products (product_id),
    Url TEXT
);

-- Relationship Tables

-- Admin manages Product (M:N)
CREATE TABLE manages (
    admin_id INT,
    product_id INT,
    PRIMARY KEY (admin_id, product_id),
    FOREIGN KEY (admin_id) REFERENCES admins(admin_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Vendor sells Products (M:N)
CREATE TABLE sells (
    vendor_id INT,
    product_id INT,
    PRIMARY KEY (vendor_id, product_id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Order contains Products
CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    size VARCHAR(20),
    color VARCHAR(20),
    quantity INT,
    PRIMARY KEY (order_id, product_id, size, color),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Cart contains Products
CREATE TABLE cart_items (
    cart_id INT,
    product_id INT,
    size VARCHAR(20),
    color VARCHAR(20),
    quantity INT,
    PRIMARY KEY (cart_id, product_id, size, color),
    FOREIGN KEY (cart_id) REFERENCES carts(cart_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Customer chats with Vendor
CREATE TABLE chats (
    chat_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT,
    vendor_id INT,
    text TEXT,
    image TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);

-- Customer chats with Admin
CREATE TABLE chats_admin (
   chat_id INT PRIMARY KEY AUTO_INCREMENT,
   customer_id INT,
   vendor_id INT,
   text TEXT,
   image TEXT,
   FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
   FOREIGN KEY (admin_id) REFERENCES admins(admin_id)
);

-- Customer places Order
-- (Already handled via orders.customer_id)

-- Customer makes Return
-- (Already handled via returns.customer_id)

-- Product Variants (colors & sizes)
CREATE TABLE product_variants (
    variant_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT,
    size VARCHAR(20),
    color VARCHAR(20),
    stock INT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);