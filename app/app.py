"""
FILE SUMMARY:
This is a Flask web application that serves as the core of the DevOps Learning Lab.
It connects to a Redis database to track and display a visit counter.
It also displays the hostname of the container it is running in, which helps
demonstrate how Kubernetes load balances traffic across multiple Pods.
"""

# Import the logging module to output application events
import logging
# Import Flask class to create the web application
from flask import Flask
# Import the redis library to interact with the Redis database
import redis
# Import os to access environment variables from the operating system
import os
# Import socket to retrieve the network name (hostname) of the machine
import socket

# Configure logging to show information-level messages in the console
# Set the minimum logging level to INFO
logging.basicConfig(level=logging.INFO)
# Create a logger instance for this specific module
logger = logging.getLogger(__name__)

# Initialize the Flask application instance
app = Flask(__name__)

# Define the Redis connection details using environment variables with local defaults
# Get 'REDIS_HOST' or default to 'localhost'
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# Get 'REDIS_PORT' and convert to integer
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Set up the Redis client and handle potential connection issues
try:
    # Attempt to execute the connection logic
    # Connect to Redis
    cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    # Send a PING command to test if the connection is actually alive
    cache.ping()
    # Log success
    logger.info("Successfully connected to Redis at %s:%s", REDIS_HOST, REDIS_PORT)
# Catch errors if Redis is unreachable
except redis.ConnectionError as e:
    # Log the specific connection error
    logger.error("Could not connect to Redis: %s", e)
    # Set cache to None so the app knows database is unavailable
    cache = None

# Define the route for the homepage (URL: /)
@app.route("/", methods=["GET"])
# This function runs when someone visits the homepage
def index():
    # Default message if the database isn't working
    hits = "Redis unavailable"
    # Check if the Redis connection was successfully established
    if cache:
        # Attempt to perform a database operation
        try:
            # Increment the 'hits' key in Redis and get the new value
            hits = cache.incr("hits")
        # Catch any errors that occur during the increment
        except redis.RedisError as e:
            # Log the database operation error
            logger.error("Redis operation failed: %s", e)

    # Retrieve the container's hostname to show which specific Pod is serving the request
    # Get the name of the current machine/container
    hostname = socket.gethostname()

    # Return the HTML content to be displayed in the user's browser
    return f"""
    <html>
        <!-- Start of the HTML document -->
        <head>
            <!-- Header section for metadata and styling -->
            <title>DevOps Learning Lab</title>
            <!-- The title shown on the browser tab -->
            <style>
                /* Internal CSS for styling the page */
                body {{ 
                    /* Modern font stack */
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    /* Light grey/blue background */
                    background-color: #f0f2f5;
                    /* Dark grey text for readability */
                    color: #333;
                    /* Center-align all text on the page */
                    text-align: center;
                    /* Add space at the very top */
                    padding-top: 50px;
                }}
                .container {{ 
                    /* White background for the main content box */
                    background: white;
                    /* Space inside the box */
                    padding: 40px;
                    /* Rounded corners for a modern look */
                    border-radius: 12px;
                    /* Subtle shadow for depth */
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    /* Make the box only as wide as its content */
                    display: inline-block;
                }}
                /* Blue color for the main heading */
                h1 {{ color: #007bff; }}
                .count {{ 
                    /* Large text for the hit counter */
                    font-size: 48px;
                    /* Bold text for emphasis */
                    font-weight: bold;
                    /* Green color to represent 'growth/hits' */
                    color: #28a745;
                }}
                .info {{ 
                    /* Space above the pod info */
                    margin-top: 20px;
                    /* Slightly smaller text for metadata */
                    font-size: 14px;
                    /* Muted grey color */
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <!-- Visible part of the web page -->
            <div class="container">
                <!-- Wrapper for the central content card -->
                <h1>Welcome to DevOps Lab!</h1>
                <!-- Main welcome message -->
                <p>This page has been viewed</p>
                <!-- Description text -->
                <div class="count">{hits}</div>
                <!-- Dynamic hit counter from Redis -->
                <p>times.</p>
                <!-- Suffix for the counter -->
                <div class="info">Served by Pod/Container: <b>{hostname}</b></div>
                <!-- Shows which backend pod handled the request -->
            </div>
        </body>
    </html>
    """

# Check if the script is being run directly (not imported)
if __name__ == "__main__":
    # Determine the host and port for the server to listen on
    # nosec - Use env var or listen on all interfaces
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0") # nosec
    # Use env var or default to port 5000
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    # Start the Flask development web server
    # Run the application with the specified host and port
    app.run(host=host, port=port)


