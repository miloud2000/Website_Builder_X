import mysql.connector
import subprocess
import time

# Function to fetch websites to resume from suspension
def fetch_websites_to_resume():
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
    query = "SELECT username, nameWebsite FROM Website_reprendre_suspendre WHERE statut = 0"
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

# Function to update Statu_du_website to 1 in Website_reprendre_suspendre
def update_resume_status(username, nameWebsite):
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",  # MySQL container hostname
        user="root",
        port=3307,
        password="password",
        database="websitesdb"
    )

    # Update Statu_du_website to 1 in Website_reprendre_suspendre
    cursor = conn.cursor()
    query = "UPDATE Website_reprendre_suspendre SET statut = 1 WHERE username = %s AND nameWebsite = %s"
    cursor.execute(query, (username, nameWebsite))

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()

# Function to start Docker container
def start_docker_container(nameWebsite):
    subprocess.run(["docker", "start", nameWebsite])
    print(f"Docker container {nameWebsite} has been started.")

# Main function to resume suspended websites
def resume_websites():
    # Fetch websites to resume
    websites = fetch_websites_to_resume()

    # Loop through each website
    for website in websites:
        username = website["username"]
        nameWebsite = website["nameWebsite"]

        # Start Docker container
        start_docker_container(nameWebsite)

        # Update website status in Website_reprendre_suspendre
        update_resume_status(username, nameWebsite)

        print(f"Website for user {username} with container {nameWebsite} has been resumed and status updated.")

# Run the script periodically
while True:
    resume_websites()
    time.sleep(3600)  # Check every hour (3600 seconds)
