import subprocess
import socket

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

# Predefined list of users
users = [
    {
        "username": "Akiratoon",
        "base_image": "nginx",
        "website": "web1"
    },
    {
        "username": "miloud",
        "base_image": "httpd",
        "website": "web2"
    }
]

def create_docker_containers(users):
    for user in users:
        username = user["username"]
        base_image = user["base_image"]

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
        subprocess.run(["docker", "run", "-d", "--name", app_container_name, "--link", db_container_name, "-p", f"{app_port}:80", base_image])

        # Additional configuration or environment variables can be added here

# Create Docker containers using the predefined list of users
create_docker_containers(users)
