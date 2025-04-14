# PhiMart E-Commerce API

PhiMart is an e-commerce backend API built using Django Rest Framework (DRF). It provides functionality for managing products, orders, and users, with JWT-based authentication for secure access.

## Features

- **Products**: Create, update, delete, and view product details.
- **Orders**: Place orders, view order and manage order details, <br> Create, Update, and Delete carts.
- **Users**: User registration, login, profile management, and authentication using JWT.
- **API Documentation**: Interactive API documentation using `drf-yasg`.
- **Authentication**: Secure JWT-based authentication with `djoser`.

## Technologies Used

- **Backend Framework**: Django Rest Framework (DRF)
- **Authentication**: JSON Web Tokens (JWT) with `djoser`
- **API Documentation**: `drf-yasg`

## Project Structure

The project is divided into the following apps:

1. **Product**: Handles all operations related to product listings and management.
2. **Order**: Manages order placement, retrieval, and history.
3. **Users**: Handles user authentication, registration, and profile-related functionalities.

## Installation

Follow the steps below to set up and run the PhiMart API locally:

1. Clone the repository:

   ```bash
   git clone https://github.com/achibhossengit/PhiMart
   cd phimart
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:

   ```bash
   python manage.py migrate
   ```

5. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`.

## API Documentation

Interactive API documentation is available at:

- Swagger UI: `http://127.0.0.1:8000/swagger/`
- Redoc: `http://127.0.0.1:8000/redoc/`

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:

   ```bash
   git checkout -b feature-name
   ```

3. Commit your changes and push them to your fork.
4. Create a pull request to the main repository.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact

For questions or support, please contact [Achib Hossen](mail.achibhossen@gmail.com).

