import mysql.connector
from flask import Flask, jsonify, request, abort
from flask_httpauth import HTTPTokenAuth

# Create a Flask app
app = Flask(__name__)

# Create an HTTP token auth object
auth = HTTPTokenAuth()

# Load API keys from a file
api_keys = {}
with open("api_keys.txt", "r") as f:
    for line in f:
        api_key, user = line.strip().split(",")
        api_keys[api_key] = user

# Decorator to authenticate requests
def authenticate(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("Authorization")
        if api_key not in api_keys:
            abort(401, "Invalid API key")
        user = api_keys[api_key]
        return fn(user, *args, **kwargs)
    return decorated

# Connect to the MySQL database
db = mysql.connector.connect(host="localhost", user="root", password="", database="news_api")

# Get the cursor object
cursor = db.cursor()

# Endpoint to search for news articles
@app.route("/news/search", methods=["GET"])
@authenticate
def news_search(user):
    # Get the query string and other parameters from the request
    query = request.args.get("query")
    category = request.args.get("category")
    country = request.args.get("country")
    language = request.args.get("language")

    # Construct the SQL query
    sql = """
        SELECT *
        FROM news_articles
        WHERE title LIKE %s OR description LIKE %s
    """
    params = (f"%{query}%", f"%{query}%")

    # Execute the SQL query
    cursor.execute(sql, params)

    # Get the results
    results = cursor.fetchall()

    # Convert the results to JSON format
    articles = []
    for row in results:
        article = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "url": row[3]
        }
        articles.append(article)

    # Return the results in JSON format
    return jsonify({"articles": articles})

# Endpoint to get the top headlines
@app.route("/news/top-headlines", methods=["GET"])
@authenticate
def news_top_headlines(user):
    # Get the country and language from the request
    country = request.args.get("country")
    language = request.args.get("language")

    # Construct the SQL query
    sql = """
        SELECT *
        FROM news_articles
        WHERE country = %s AND language = %s
        ORDER BY published_at DESC
        LIMIT 10
    """
    params = (country, language)

    # Execute the SQL query
    cursor.execute(sql, params)

    # Get the results
    results = cursor.fetchall()

    # Convert the results to JSON format
    articles = []
    for row in results:
        article = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "url": row[3]
        }
        articles.append(article)

    # Return the results in JSON format
    return jsonify({"articles": articles})

# Endpoint to get a list of all available news categories
@app.route("/news/categories", methods=["GET"])
@authenticate
def news_categories(user):
    # Construct the SQL query
    sql = """
        SELECT DISTINCT category
        FROM news_articles
    """

    # Execute the SQL query
    cursor.execute(sql)

    # Get the results
    results = cursor.fetchall()

    # Convert the results to a list
    categories = []
    for row in results:
        categories.append(row[0])

    # Return the results in JSON format
    return jsonify(categories)

# Endpoint to add a new news article
@app.route("/news/add", methods=["POST"])
@authenticate
def news_add(user):
    # Get the title, description, and URL of the new news article from the request
    title = request.json.get("title")
    description = request.json
