# Dockership Application

Dockership is a containerized application designed for efficiently managing the loading, unloading, and weight balancing of freight ships. The application features a user-friendly GUI that supports user authentication, file handling, automated task processing, and real-time 2D visualization of ship operations.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Additional Notes](#additional-notes)

## Features

- **User Authentication**: Secure login and registration features.
- **File Handling**: Upload and download files for ship manifest and transfer lists.
- **Automated Processing**: Intelligent loading, unloading, and balancing instructions.
- **Real-Time Visualization**: Visualize ship grid layout, including empty and occupied spaces.
- **Detailed Logging**: Track user activity and system events for auditing purposes.

---

## Prerequisites

Ensure the following tools are installed on your machine:

1. **Docker**: [Download Docker Desktop](https://www.docker.com/products/docker-desktop).
2. **Python**: [Download Python](https://www.python.org/downloads/) (if running locally without Docker).
3. **Git**: [Download Git](https://git-scm.com/downloads) for version control.
4. **Web Browser**: Any modern browser (e.g., Chrome, Firefox) for accessing the application.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Aditya-gam/Dockership.git
   cd Dockership
   ```

2. **Create a Virtual Environment** (optional, if running locally):
   ```bash
   python -m venv dockership_env
   source dockership_env/bin/activate   # Linux/MacOS
   ./dockership_env/Scripts/activate   # Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Docker Containers**:
   Build and run the application using Docker Compose:
   ```bash
   docker compose up --build
   ```

---

## Environment Setup

Create a `.env` file in the root directory with the following content. Replace placeholders with your actual MongoDB credentials:

```plaintext
# MongoDB configuration
MONGO_USERNAME=username
MONGO_PASSWORD=password
MONGO_DBNAME=database_name

# MongoDB Atlas connection
MONGO_URI=connection_string
```

---

## Running the Application

1. **Run with Docker**:
   After executing `docker compose up --build`, the application will be accessible at:
   ```plaintext
   http://localhost:8501
   ```

2. **Run Locally** (without Docker):
   Execute the following command:
   ```bash
   streamlit run app.py
   ```

   The application will open in your default web browser.

---

## Project Structure

Here’s an overview of the project structure:

```
DOCKERSHIP/
│
├── app.py                     # Main application script
├── Dockerfile                 # Dockerfile for building the Docker image
├── requirements.txt           # Python package dependencies
├── docker-compose.yml         # Docker Compose configuration
├── .env                       # Environment variables (actual file)
├── .env.example               # Example environment variable file
├── .gitignore                 # Git ignore file
├── README.md                  # Project documentation
│
├── data/                      # Directory for data files
│   └── ship_layout.csv        # Ship layout data (Sample)
│
├── auth/                      # Authentication-related scripts
│   ├── login.py               # Login functionality module
│   └── register.py            # Registration functionality module
│
├── config/                    # Configuration-related scripts
│   └── db_config.py           # Database configuration script
│
├── tasks/                     # Task-related modules
│   ├── balancing_utils.py     # Ship balancing logic
|   ├── ship_balancer.py
│   ├── ship_loader.py         # Loading operation module
│   └── operation.py           # Other operations logic
│
├── tests/                     # Unit tests
|   ├── loading_task_test_cases.py   
│   ├── test_file_handler.py   # Test script for file handling
│   └── test_visualizer.py     # Test script for visualizer functionality
|
├── tests/
|   ├── components/
|   |   ├── buttons.py
|   |   └── textboxes.py
|   ├── file_handler.py
|   ├── grid_utils.py
|   ├── logging.py
|   ├── state_manager.py
|   ├── validators.py
|   └── visualizer.py
│
└── pages/                     # Page-related modules organized by functionality
    ├── auth/                  # Authentication pages (login, register)
    │   ├── login.py           # Login page functionality
    │   └── register.py        # Register page functionality
    │
    ├── file_handler/          # File handler page
    │   └── file_handler.py    # File handler page functionality
    │
    ├── tasks/                  # Task pages (operation, loading, balancing)
    │   ├── operation.py       # Operations task page
    │   ├── loading.py          # Loading task page
    |   └── balancing.py       # Balancing task page
    └──        
```

---

## Development Workflow

1. **Branching**: Use feature-specific branches and create pull requests for review before merging into the main branch.
2. **Testing**: Run tests before pushing changes:
   ```bash
   pytest
   ```
3. **Code Reviews**: Collaborate through GitHub for code reviews and maintain high code quality.

---

## Testing

Run the test suite to ensure the application is functioning correctly:
```bash
pytest tests/
```

Make sure to add new test cases for any significant functionality added.

---

## Troubleshooting

1. **Port Already in Use**: Stop any application running on port 8501:
   ```bash
   docker ps
   docker stop <container_id>
   ```

2. **MongoDB Connection Issues**: Verify the `.env` file contains the correct credentials.

3. **Docker Build Errors**: Ensure all dependencies in `requirements.txt` are compatible and properly listed.

---

## Additional Notes

- **Environment Variables**: Never commit `.env` files to version control. Use `.env.example` for sharing environment variable structure.
- **Security Best Practices**: Validate user input rigorously and encrypt sensitive data.
- **Performance**: Monitor resource usage when running the application in production.
