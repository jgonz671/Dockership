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

```plaintext
Dockership/
│
├── app.py                # Main Streamlit application script
├── Dockerfile            # Dockerfile for building the Docker image
├── requirements.txt      # Python package dependencies
├── docker-compose.yml    # Docker compose configuration
│
├── data/                 # Directory for any data files, e.g., ship layouts
│   └── ship_layout.csv   # Example layout data (Sample)
│
├── logs/                 # Directory for log files
│   └── events.log        # Log file for application events (Sample)
│
├── modules/              # Python modules for additional functionality
│   ├── login.py          # Module for login functionality (Sample)
│   ├── file_handler.py   # Module for file upload and download handling (Sample)
│   └── visualizer.py     # Module for generating 2D graphics of the ship (Sample)
│
└── README.md             # Instructions and information about the application
```

## Development Workflow

- **Code Changes**: Any changes to the project should be done through proper Git workflows, ensuring that all modifications are pulled into the project via pull requests after code review.
- **Testing**: Ensure to run the application through rigorous tests after every significant change to any module.
- **Logs**: Keep an eye on the log files for any unusual activity, especially during the testing phase.

## Additional Notes

- **Environment Variables**: For the Docker environment, you can set necessary variables within the Dockerfile or docker-compose.yml, depending on the requirement of the project.
- **Security**: Always ensure that user authentication and data handling are secure and up to industry standards.
- **Updates**: Regularly update the Docker images and dependencies to keep up with the latest security patches and features.