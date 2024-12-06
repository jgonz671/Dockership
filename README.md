# Dockership Application

This application is designed to manage the loading, unloading, and weight balancing of freight ships. It provides a GUI for user interactions such as login, file upload, and processing instructions, along with visualizing empty spaces on the ship.

## Table of Contents
- [Dockership Application](#dockership-application)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Running the Application](#running-the-application)
  - [Project Structure](#project-structure)
  - [Development Workflow](#development-workflow)
  - [Additional Notes](#additional-notes)

## Features

- User authentication
- File upload and download
- Automated processing of ship loading instructions
- Real-time 2D visualization of the ship's grid
- Detailed event logging

## Getting Started

### Prerequisites

Make sure the following software is installed on your machine:

1. **Docker**: [Download Docker Desktop](https://www.docker.com/products/docker-desktop) to manage containers.
2. **Git**: [Download Git](https://git-scm.com/downloads) for version control.

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/jgonz671/Dockership.git
   cd Dockership
   ```

2. **Build the Docker container**:
   ```bash
   docker compose up --build
   ```

### Running the Application

- After building the Docker container, the application will be accessible at `http://localhost:8501`.
- Follow the in-app instructions to upload a ship load file and receive loading or unloading guidance.

## Project Structure

The following is the directory structure of the **Dockership** project:

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
│   ├── balancing.py           # Ship balancing logic
│   ├── loading.py             # Loading operation module
│   └── operation.py           # Other operations logic
│
├── tests/                     # Unit tests
│   ├── test_file_handler.py   # Test script for file handling
│   └── test_visualizer.py     # Test script for visualizer functionality
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
    │   ├── loading.py         # Loading task page
    │   └── balancing.py       # Balancing task page
    │
    └── components/             # Common components for the pages
        ├── buttons.py         # Common button components for pages
        ├── grid.py            # Grid-related components
        └── textboxes.py       # Textbox components
```

## Development Workflow

- **Code Changes**: Any changes to the project should be done through proper Git workflows, ensuring that all modifications are pulled into the project via pull requests after code review.
- **Testing**: Ensure to run the application through rigorous tests after every significant change to any module.
- **Logs**: Keep an eye on the log files for any unusual activity, especially during the testing phase.

## Additional Notes

- **Environment Variables**: For the Docker environment, you can set necessary variables within the Dockerfile or docker-compose.yml, depending on the requirement of the project.
- **Security**: Always ensure that user authentication and data handling are secure and up to industry standards.
- **Updates**: Regularly update the Docker images and dependencies to keep up with the latest security patches and features.