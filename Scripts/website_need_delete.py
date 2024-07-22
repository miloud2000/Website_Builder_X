import mysql.connector
import subprocess
import os
import time

# Function to fetch websites to delete
def fetch_websites_to_delete():
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",  # MySQL container hostname
        user="root",
        port=3307,
        password="password",
        database="websitesdb"
    )

    # Execute query to fetch websites with Statu_du_website = 0
    cursor = conn.cursor()
    query = "SELECT username, nameWebsite FROM Websites_Need_Delete WHERE statut = 0"
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

# Function to update Statu_du_website to 1 for a specific container
def update_website_status(nameWebsite):
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",  # MySQL container hostname
        user="root",
        port=3307,
        password="password",
        database="websitesdb"
    )

    # Update Statu_du_website to 1
    cursor = conn.cursor()
    query = "UPDATE Websites_Need_Delete SET statut = 1 WHERE nameWebsite = %s"
    cursor.execute(query, (nameWebsite, ))

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()

# Function to delete Docker container
def delete_docker_container(nameWebsite):
    subprocess.run(["docker", "stop", nameWebsite])
    subprocess.run(["docker", "rm", nameWebsite])
    print(f"Docker container {nameWebsite} has been deleted.")

# Function to delete user directories
def delete_user_directories(nameWebsite):
    mysql_volume_path = f"/mysql-volume/{nameWebsite}"
    wordpress_volume_path = f"/wordpress-volume/{nameWebsite}"

    if os.path.exists(mysql_volume_path):
        os.rmdir(mysql_volume_path)
        print(f"Directory {mysql_volume_path} has been deleted.")
    
    if os.path.exists(wordpress_volume_path):
        os.rmdir(wordpress_volume_path)
        print(f"Directory {wordpress_volume_path} has been deleted.")

# Main function to delete websites
def delete_websites():
    # Fetch websites to delete
    websites = fetch_websites_to_delete()

    # Loop through each website
    for website in websites:
        username = website["username"]
        nameWebsite = website["nameWebsite"]

        # Delete Docker container
        delete_docker_container(nameWebsite)

        # Delete user directories
        delete_user_directories(nameWebsite)

        # Update website status
        update_website_status(nameWebsite)
        print(f"Website for user {username} with container {nameWebsite} has been deleted and status updated.")

# Run the script periodically
# while True:
#     delete_websites()
#     time.sleep(3600)  # Check every hour (3600 seconds)
