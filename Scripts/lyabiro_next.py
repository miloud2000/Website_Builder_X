import subprocess
import socket
import mysql.connector

# Function to check if a port is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Function to find an available port
def find_available_port(start_port):
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

# Function to fetch user information from the MySQL database
def fetch_user_information():
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",  # MySQL container hostname
        user="root",
        port=3307,
        password="password",
        database="websitesdb"
    )

    # Execute query to fetch user information
    cursor = conn.cursor()
    query = "SELECT username, website FROM websites"
    cursor.execute(query)

    # Parse query results and store information
    users = []
    for username, website in cursor:
        user_info = {
            "username": username,
            "website": website
        }
        users.append(user_info)

    # Close cursor and connection
    cursor.close()
    conn.close()

    return users

def create_docker_containers(users):
    for user in users:
        username = user["username"]
        base_image = user["website"]

        # Generate container names
        db_container_name = f"db-{username}-container"
        app_container_name = f"app-{username}-container"

        # Find an available port for the database container
        db_port = find_available_port(3306)

        # Find an available port for the website container
        app_port = find_available_port(8080)

        # Create database container
        subprocess.run(["docker", "run", "-d", "--name", db_container_name, "-p", f"{db_port}:3306", "-e", "MYSQL_ROOT_PASSWORD=password", "mysql:latest"])

        # Create website container and link it to the database container
        subprocess.run(["docker", "run", "-d", "--name", app_container_name, "-p", f"{app_port}:80", base_image])

        # Additional configuration or environment variables can be added here

# Fetch user information from the MySQL database
users = fetch_user_information()

# Create Docker containers using the fetched information
create_docker_containers(users)
