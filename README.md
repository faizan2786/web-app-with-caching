# Web Application with Caching and deployed using Docker

This project is a basic web application written in python using `Flask`. It uses `Postgres` as it persistent storage layer and  uses `Redis` as it **caching** layer. The application and all of its related components (i.e. postgres and redis instance) are deployed using `Docker Compose`.

The purpose of this project is to mainly demonstrate following concept in modern web app development:
- How to use in-memory caching to **improve the performance** of a web application. The project caches mapping of user email to its user id in Redis to optimize the performance of user id retrieval by email.
- How to build and deploy **a self-contained web application with multiple services** using Docker and Docker Compose.


## Project Structure

Here is a brief overview of the project's structure:
- `src/`: This directory contains the main application code.
- `Dockerfile`: This file is used to build the Docker image for our web application.
- `docker-compose.yml`: This file is used to define all the required services including our web-app and run them as **multi-container Docker applications**.
- `users_table.psql`: This file contains the SQL command to create the Users table in the Postgres DB.
- `users.csv`: This file contains the user data in CSV format, which can be loaded to the Users table.

## Installation

Follow these steps to install and run the project using Docker Compose:

1. Install Docker and Docker Compose on your machine. Visit [Docker's website](https://www.docker.com/) for installation instructions.

2. Clone this repository to your local machine.

    ```bash
    git clone https://github.com/username/project.git
    ```

3. Navigate to the project directory.

    ```bash
    cd web-app-with-caching
    ```

4. Run the Docker Compose command to build and start the services defined in `docker-compose.yml`.

    ```bash
    docker-compose up [-d]
5. Load the User data in db container:
    - Copy the `users.csv` file to the db container using the following command:
        ```bash
        docker cp users.csv user-api-db:/
    - Open a new terminal window and navigate to the project directory.
    - Run the following command to login to the db container and connect to the Postgres database:
        ```bash
        docker exec -it user-api-db psql -U <postgres_username> user_db
    - Now create a table in the database using command given in the `USERS_TABLE.sql` file:
        ```sql
        CREATE TABLE Users (username varchar(10) PRIMARY KEY, name varchar(30) NOT NULL, email varchar(30) UNIQUE, dob date, passwordhash varchar);
    - Now import the data from the `users.csv` file to the `Users` table using following command:
        ```sql
        COPY Users FROM '/users.csv' DELIMITER ',' CSV HEADER;
## Usage

Once the containers are up and running and data is loaded to the DB, you can access the web application by visiting `http://localhost:5001` in your web browser. The application will display a greeting message saying `Welcome to the User API Web-Application!`.

You may visit following** GET request routes** to interact with the application:
- `/users/<user_name>`: This route will display the details of the user with the given `user_name`.
- `/users/email/<user_name>`: This route will display the email of the user with the given `user_name`.
- `/users/username/<email>`: This route will display the username of the user with the given `email`.