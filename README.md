# Blog Post API with Frontend

## Overview

This is a simple blog post application that provides both backend and frontend functionality. The backend is built with Flask and provides a RESTful API for creating, reading, updating, deleting, and searching blog posts. The frontend is a simple HTML and JavaScript interface that interacts with the API.

## Features

- **User Registration and Login**: Users can register and log in to create and manage their blog posts.
- **CRUD Operations**: Users can create, read, update, and delete blog posts.
- **JWT Authentication**: Secure user authentication using JSON Web Tokens (JWT).
- **Sorting and Filtering**: Blog posts can be sorted by title, author, or date in ascending or descending order.
- **Search**: Users can search for blog posts by title or content.

## Project Structure

project_root/
│
├── backend/
│ ├── routes/
│ │ ├── init.py # Initialize blueprint and import routes
│ │ ├── auth.py # Authentication-related routes
│ │ ├── posts.py # Post-related routes
│ │ └── utils.py # Utility functions (pagination, etc.)
│ ├── init.py # Backend package initialization
│ ├── backend_app.py # Main entry point for the Flask app
│ ├── config.py # Configuration settings
│ ├── models.py # Models and custom exceptions
│ ├── posts.json # Data file for storing posts
│
├── frontend/
│ ├── static/
│ │ ├── main.js # JavaScript for frontend
│ │ └── styles.css # CSS for frontend
│ ├── templates/
│ │ └── index.html # Frontend HTML
│ └── frontend_app.py # Entry point for running a frontend development server
│
└── requirements.txt # List of dependencies

## Setup and Installation

### Backend Setup


1. **Create and Activate a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

   ```

2. **Install Dependencies:**

   ```bash
   pip install -r ../requirements.txt

   ```

3. **Navigate to the Backend Directory:**

   ```bash
   cd backend

   ```


4. **Run the Flask Backend Application:**

   ```bash
   python backend_app.py
   ```

### Frontend Setup

1. **Navigate to the Frontend Directory:**

   ```bash
   cd ../frontend

   ```

2. **Open the index.html File:**
   Open index.html located in the templates directory in your web browser. The frontend will interact with the backend API running at http://127.0.0.1:5002/api.

### Running the Frontend Development Server (Optional)

If you have a frontend_app.py file set up to run a simple Flask server to serve the frontend, you can do the following:

1. **Run the Frontend Application:**

   ```bash
   python frontend_app.py

   ```

2. **Access the Frontend:**
   Visit http://127.0.0.1:5001 in your web browser to view and interact with the frontend.


## Usage

### Registration

1. Enter a username and password in the registration section.
2. Click the "Register" button to create a new account.

### Login

1. Enter your username and password in the login section.
2. Click the "Login" button to log in and retrieve your JWT token.

### Creating a Post

1. Enter a title and content in the "Add Post" section.
2. Click the "Add Post" button to create a new blog post.


###  Viewing Posts

- Click "Load Posts" to retrieve and display all blog posts.

### Searching Posts

1. Enter a search query in the "Search by title or content" field.
2. Click the "Search" button to filter posts based on the search query.

### Sorting Post

1. Select a sort criterion (Title, Author, Date) and direction (Ascending, Descending).
2. Click the "Sort" button to sort the posts accordingly.

### Deleting a Post

- Click the "Delete" button next to a post to remove it.

## Dependencies

- Flask
- Flask-CORS
- Flask-JWT-Extended
- Flask-Limiter
- Flask-Bcrypt
- Flasgger

Install dependencies using the command:

    ```bash
    pip install -r requirements.txt

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.


## Contact

For questions or issues, please contact developer@alexkummerer.de

