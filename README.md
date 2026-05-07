# CSET_Store_Final

## Description

This is a full-stack e-commerce web application built with Flask, designed as a final project for CSET 180. The application allows users to browse products, manage wishlists, place orders, and handle returns. It supports multiple user roles: customers, vendors, and administrators.

## Features

- **User Authentication**: Login, signup, and password management for customers, vendors, and admins.
- **Product Management**: Vendors can add, edit, and manage products with variants (size, color, stock).
- **Shopping Cart**: Add items to cart, update quantities, and checkout.
- **Wishlist**: Save favorite products for later.
- **Order Management**: View order history, track status, and handle returns.
- **Reviews and Ratings**: Customers can leave reviews on products.
- **Admin Dashboard**: Manage users, products, and orders.
- **Vendor Dashboard**: Manage own products and orders.
- **Search and Filtering**: Search products by name, filter by category, color, size, and availability.
- **Discounts**: Support for product discounts with deadlines.
- **Chat System**: Communication between customers, vendors, and admins regarding orders or returns.

## Technologies Used

- **Backend**: Python, Flask
- **Database**: MySQL (via SQLAlchemy)
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS
- **Authentication**: Werkzeug for password hashing
- **Session Management**: Flask sessions
- **File Uploads**: For product images

## Installation

1. **Clone the repository**:
   ```
   git clone https://github.com/stefanescuowen-cmd/CSET_Store_Final.git
   cd CSET_Store_Final
   ```

2. **Install Python dependencies**:
   ```
   pip install -r requirements.txt
   ```
   (Note: You may need to create a `requirements.txt` file with dependencies like Flask, SQLAlchemy, etc.)

3. **Set up the database**:
   - Ensure MySQL is installed and running.
   - Create a database named `store_db`.
   - Run the SQL scripts in `database/` to set up tables and seed data:
     ```
     mysql -u your_username -p store_db < database/store_database_schema.sql
     mysql -u your_username -p store_db < database/queries.sql
     mysql -u your_username -p store_db < database/seed_data.sql
     ```

4. **Configure the application**:
   - Update `config.py` with your database credentials.
   - Set up any environment variables if needed.

## Running the Application

1. **Start the Flask app**:
   ```
   python main.py
   ```

2. **Access the application**:
   - Open your browser and go to `http://localhost:5000`

## Usage

- **As a Customer**: Register/login, browse products, add to cart/wishlist, place orders, leave reviews.
- **As a Vendor**: Login, add/manage products, view orders related to your products.
- **As an Admin**: Login, manage all users, products, orders, and returns.

## Project Structure

- `main.py`: Main Flask application file.
- `config.py`: Configuration settings.
- `database.py`: Database connection and queries.
- `extensions.py`: Flask extensions setup.
- `app_utils.py`: Utility functions.
- `blueprints/`: Modular blueprints for different user roles (auth, admin, vendor, customer).
- `templates/`: HTML templates for the frontend.
- `static/`: CSS, JavaScript, and image files.
- `database/`: SQL schema and seed data.

## Contributing

This is a school project, but feel free to fork and contribute improvements.

## License

This project is for educational purposes only.
