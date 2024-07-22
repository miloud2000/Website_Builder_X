import mysql.connector
import subprocess

# Function to fetch websites with Statu_du_website set to 0
def fetch_websites_to_suspend():
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
    query = "SELECT username, nameWebsite FROM Websites_location_payment_delay WHERE statut = 0"
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

# Function to update Statu_du_website to 1
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
    query = "UPDATE Websites_location_payment_delay SET statut = 1 WHERE nameWebsite = %s"
    cursor.execute(query, (nameWebsite,))

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()

# Function to stop Docker container
def stop_docker_container(nameWebsite):
    subprocess.run(["docker", "stop", nameWebsite])
    print(f"Docker container {nameWebsite} has been stopped.")

# Main function to suspend websites
def suspend_websites():
    # Fetch websites to suspend
    websites = fetch_websites_to_suspend()

    # Loop through each website
    for website in websites:
        username = website["username"]
        container_name = website["nameWebsite"]

        # Stop Docker container
        stop_docker_container(container_name)

        # Update website status
        update_website_status(username)
        print(f"Website for user {username} has been suspended and status updated.")

# Suspend websites based on payment delay
suspend_websites()
