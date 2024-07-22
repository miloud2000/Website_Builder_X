import mysql.connector
import subprocess
import os
import shutil
import time

# Function to fetch websites to reset
def fetch_websites_to_reset():
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",  # MySQL container hostname
        user="root",
        port=3307,
        password="password",
        database="websitesdb"
    )

    # Execute query to fetch websites with statut = 0
    cursor = conn.cursor()
    query = "SELECT username, nameWebsite FROM website_need_reset WHERE statut = 0"
    cursor.execute(query)

    # Parse query results and store information
    websites = []
    for username, nameWebsite in cursor:
        website_info = {
            "username": username,
            "nameWebsite": nameWebsite
        }
        websites.append(website_info)

    # Close cursor and connection
    cursor.close()
    conn.close()

    return websites

# Function to update statut to 1 in website_need_reset
def update_reset_status(username, container_name):
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",  # MySQL container hostname
        user="root",
        port=3307,
        password="password",
        database="websitesdb"
    )

    # Update statut to 1 in website_need_reset
    cursor = conn.cursor()
    query = "UPDATE website_need_reset SET statut = 1 WHERE username = %s AND nameWebsite = %s"
    cursor.execute(query, (username, container_name))

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()

# Function to stop and remove Docker container
def stop_remove_docker_container(nameWebsite):
    subprocess.run(["docker", "stop", nameWebsite])
    subprocess.run(["docker", "rm", nameWebsite])
    print(f"Docker container {nameWebsite} has been stopped and removed.")

# Function to reset Docker container volumes
def reset_docker_container_volumes(nameWebsite):
    mysql_volume_path = f"/mysql-volume/{nameWebsite}"
    wordpress_volume_path = f"/wordpress-volume/{nameWebsite}"

    # Remove the volume directories
    if os.path.exists(mysql_volume_path):
        shutil.rmtree(mysql_volume_path)
    if os.path.exists(wordpress_volume_path):
        shutil.rmtree(wordpress_volume_path)

    # Recreate the volume directories
    os.makedirs(mysql_volume_path, exist_ok=True)
    os.makedirs(wordpress_volume_path, exist_ok=True)

    print(f"Volumes for user {username} have been reset.")

# Function to recreate and start Docker containers
def recreate_docker_containers(username, nameWebsite):
    # Recreate database container
    db_container_name = f"db-{nameWebsite}-container"
    subprocess.run(["docker", "run", "-d", "--name", db_container_name,
                    "-e", "MYSQL_DATABASE=wordpress",
                    "-e", "MYSQL_USER=wordpress",
                    "-e", "MYSQL_PASSWORD=wordpress",
                    "-e", "MYSQL_ROOT_PASSWORD=wordpress",
                    "-v", f"/mysql-volume/{nameWebsite}:/var/lib/mysql",
                    "mysql:5.7"])

    # Recreate WordPress container
    app_container_name = f"app-{nameWebsite}-container"
    subprocess.run(["docker", "run", "-d", "--name", app_container_name,
                    "-e", f"WORDPRESS_DB_HOST={db_container_name}",
                    "-e", "WORDPRESS_DB_USER=wordpress",
                    "-e", "WORDPRESS_DB_PASSWORD=wordpress",
                    "-e", "WORDPRESS_DB_NAME=wordpress",
                    "-v", f"/wordpress-volume/{nameWebsite}:/var/www/html",
                    "wordpress"])

    print(f"Docker containers for user {username} have been recreated.")

# Main function to reset websites
def reset_websites():
    # Fetch websites to reset
    websites = fetch_websites_to_reset()

    # Loop through each website
    for website in websites:
        username = website["username"]
        nameWebsite = website["nameWebsite"]

        # Stop and remove Docker container
        stop_remove_docker_container(nameWebsite)

        # Reset Docker container volumes
        reset_docker_container_volumes(username)

        # Recreate and start Docker containers
        recreate_docker_containers(username, nameWebsite)

        # Update website status in website_need_reset
        update_reset_status(username, nameWebsite)

        print(f"Website for user {username} with container {nameWebsite} has been reset and status updated.")

# # Run the script periodically
# while True:
#     reset_websites()
#     time.sleep(3600)  # Check every hour (3600 seconds)
