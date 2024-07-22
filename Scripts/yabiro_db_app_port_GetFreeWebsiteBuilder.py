import subprocess
import socket
import os
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
    query = "SELECT username, nameWebsite, website, status FROM GetFreeWebsiteBuilder"
    cursor.execute(query)

    # Parse query results and store information
    users = []
    for username, website, nameWebsite, status in cursor:
        user_info = {
            "username": username,
            "website": website,
            "nameWebsite": nameWebsite,
            "status": status

        }
        users.append(user_info)

    # Close cursor and connection
    cursor.close()
    conn.close()

    return users

# def update_user_status(username):
#     # Connect to the MySQL database
#     conn = mysql.connector.connect(
#         host="localhost",  # MySQL container hostname
#         user="root",
#         port=3307,
#         password="password",
#         database="websitesdb"
#     )


#     # Update status to true
#     cursor = conn.cursor()
#     query = "UPDATE websites SET status = true WHERE username = %s"
#     cursor.execute(query, (username,))

#     # Commit changes and close connection
#     conn.commit()
#     cursor.close()
#     conn.close()

def update_user_status(nameWebsite, db_port, app_port):
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",  # MySQL container hostname
        user="root",
        port=3307,
        password="password",  
        database="websitesdb"
    )

    # Update status, db_port, and app_port
    cursor = conn.cursor()
    query = "UPDATE GetFreeWebsiteBuilder SET status = true, db_port = %s, app_port = %s WHERE nameWebsite = %s"
    cursor.execute(query, (db_port, app_port, nameWebsite))

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()




def create_directories_for_user(nameWebsite):
    # Create directories for MySQL and WordPress volumes
    mysql_volume_path = f"/mysql-volume/{nameWebsite}"
    wordpress_volume_path = f"/wordpress-volume/{nameWebsite}"
    os.makedirs(mysql_volume_path, exist_ok=True)
    os.makedirs(wordpress_volume_path, exist_ok=True)

def create_docker_containers(users):
    for user in users:
        nameWebsite = user["nameWebsite"]
        username = user["username"]
        base_image = user["website"]
        status = user["status"]

        if not status:  # If status is false
            # Create directories for MySQL and WordPress volumes
            create_directories_for_user(nameWebsite)

            # Generate container names
            db_container_name = f"db-{nameWebsite}-container"
            app_container_name = f"app-{nameWebsite}-container"

            # Create database container with volume mounted and environment variables set
            db_port = find_available_port(3306)

 # Find an available port for the website container

            subprocess.run(["docker", "run", "-d", "--name", db_container_name,
                                        "-e", "MYSQL_DATABASE=wordpress",
                                        "-e", "MYSQL_USER=wordpress",
                                        "-p", f"{db_port}:3306",
                                        "-e", "MYSQL_PASSWORD=wordpress",
                                        "-e", "MYSQL_ROOT_PASSWORD=wordpress",
                                        "-v", f"/mysql-volume/{nameWebsite}:/var/lib/mysql",
                                        "mysql:5.7"])
            app_port = find_available_port(8000)
            subprocess.run(["docker", "run", "-d", "--name", app_container_name,
                            "-e", f"WORDPRESS_DB_HOST={db_container_name}",
                            "-e", "WORDPRESS_DB_USER=wordpress",
                            "-e", "WORDPRESS_DB_PASSWORD=wordpress",
							"-p", f"{app_port}:80",
                            "-e", "WORDPRESS_DB_NAME=wordpress",
                            "-v", f"/wordpress-volume/{nameWebsite}:/var/www/html",							
							base_image])

            # Create website container with volume mounted and environment variables set

            # Update user status
            update_user_status(nameWebsite,db_port,app_port)
            print(f"Container for user {username} successfully ---> app_ort:{app_port}--> db_port:{db_port} ")
            # Additional configuration or environment variables can be added here
        else:
            print(f"Container for user {username} already exists. Skipping creation.")

# Fetch user information from the MySQL database
users = fetch_user_information()

# Create Docker containers for users with status false
create_docker_containers(users)
