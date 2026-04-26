"""
FILE SUMMARY:
This is a Flask web application that serves as the core of the DevOps Learning Lab.
It connects to a Redis database to track and display a visit counter.
It also displays the hostname of the container it is running in, which helps
demonstrate how Kubernetes load balances traffic across multiple Pods.
"""

import logging # Import the logging module to output application events
from flask import Flask # Import Flask class to create the web application
import redis # Import the redis library to interact with the Redis database
import os # Import os to access environment variables from the operating system
import socket # Import socket to retrieve the network name (hostname) of the machine

# Configure logging to show information-level messages in the console
logging.basicConfig(level=logging.INFO) # Set the minimum logging level to INFO
logger = logging.getLogger(__name__) # Create a logger instance for this specific module

app = Flask(__name__) # Initialize the Flask application instance

# Define the Redis connection details using environment variables with local defaults
REDIS_HOST = os.getenv("REDIS_HOST", "localhost") # Get 'REDIS_HOST' or default to 'localhost'
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379)) # Get 'REDIS_PORT' and convert to integer

# Set up the Redis client and handle potential connection issues
try: # Attempt to execute the connection logic
    cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True) # Connect to Redis
    cache.ping() # Send a PING command to test if the connection is actually alive
    logger.info("Successfully connected to Redis at %s:%s", REDIS_HOST, REDIS_PORT) # Log success
except redis.ConnectionError as e: # Catch errors if Redis is unreachable
    logger.error("Could not connect to Redis: %s", e) # Log the specific connection error
    cache = None # Set cache to None so the app knows database is unavailable

@app.route("/", methods=["GET"]) # Define the route for the homepage (URL: /)
def index(): # This function runs when someone visits the homepage
    hits = "Redis unavailable" # Default message if the database isn't working
    if cache: # Check if the Redis connection was successfully established
        try: # Attempt to perform a database operation
            hits = cache.incr("hits") # Increment the 'hits' key in Redis and get the new value
        except redis.RedisError as e: # Catch any errors that occur during the increment
            logger.error("Redis operation failed: %s", e) # Log the database operation error

    # Retrieve the container's hostname to show which specific Pod is serving the request
    hostname = socket.gethostname() # Get the name of the current machine/container

    # Return the HTML content to be displayed in the user's browser
    return f"""
    <html> <!-- Start of the HTML document -->
        <head> <!-- Header section for metadata and styling -->
            <title>DevOps Learning Lab</title> <!-- The title shown on the browser tab -->
            <style> /* Internal CSS for styling the page */
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Modern font stack */
                    background-color: #f0f2f5; /* Light grey/blue background */
                    color: #333; /* Dark grey text for readability */
                    text-align: center; /* Center-align all text on the page */
                    padding-top: 50px; /* Add space at the very top */
                }}
                .container {{ 
                    background: white; /* White background for the main content box */
                    padding: 40px; /* Space inside the box */
                    border-radius: 12px; /* Rounded corners for a modern look */
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* Subtle shadow for depth */
                    display: inline-block; /* Make the box only as wide as its content */
                }}
                h1 {{ color: #007bff; }} /* Blue color for the main heading */
                .count {{ 
                    font-size: 48px; /* Large text for the hit counter */
                    font-weight: bold; /* Bold text for emphasis */
                    color: #28a745; /* Green color to represent 'growth/hits' */
                }}
                .info {{ 
                    margin-top: 20px; /* Space above the pod info */
                    font-size: 14px; /* Slightly smaller text for metadata */
                    color: #666; /* Muted grey color */
                }}
            </style>
        </head>
        <body> <!-- Visible part of the web page -->
            <div class="container"> <!-- Wrapper for the central content card -->
                <h1>Welcome to DevOps Lab!</h1> <!-- Main welcome message -->
                <p>This page has been viewed</p> <!-- Description text -->
                <div class="count">{hits}</div> <!-- Dynamic hit counter from Redis -->
                <p>times.</p> <!-- Suffix for the counter -->
                <div class="info">Served by Pod/Container: <b>{hostname}</b></div> <!-- Shows which backend pod handled the request -->
            </div>
        </body>
    </html>
    """ # End of the HTML string and return statement

if __name__ == "__main__": # Check if the script is being run directly (not imported)
    # Determine the host and port for the server to listen on
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0") # nosec - Use env var or listen on all interfaces
    port = int(os.getenv("FLASK_RUN_PORT", 5000)) # Use env var or default to port 5000
    # Start the Flask development web server
    app.run(host=host, port=port) # Run the application with the specified host and port


