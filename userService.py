# userService:
import databases
import toml
import base64

from typing import Tuple
from quart import Quart, jsonify, g, request, abort, make_response
from quart_schema import QuartSchema, validate_request

app = Quart(__name__)
QuartSchema(app)
# Configurations and database setup: 
app.config.from_file(f"./config/app.toml", toml.load)

async def _connect_db():
    database = databases.Database(app.config["DATABASES"]["USER"])
    await database.connect()
    return database
def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db
@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
        await db.disconnect()
#

def jsonify_message(message):
    return {"message": message}

async def is_user_exists(db, username) -> bool:
    query = "SELECT username FROM user WHERE username = :username"
    app.logger.info(query), app.logger.warning(query)
    user = await db.fetch_all(query=query, values={"username": username})
    return True if user and len(user) > 0 else False

async def insert_user(db, username, password) -> None:
    query = "INSERT INTO user(username, pwd) VALUES(:username, :pwd)"
    values = {"username": username, "pwd": password}
    await db.execute(query=query, values=values)

def get_username_password_from_header(req) -> Tuple[str, str]:
    if "Authorization" not in request.headers:
        return "",""
    hashBytes = req.headers["Authorization"].split()[1]
    username, passsword = base64.b64decode(hashBytes).decode("utf-8").split(":")
    return username, passsword

@app.route("/", methods=["GET"])
async def home():
    # username = ''
    # password = ''
    # if request.authorization:
    #     username = request.authorization.username
    #     password = request.authorization.password
    #     return username
    # else:
    #     return 'Could not Verify',401,{'www-Authenticate':'Basic realm = "Login Required"'}
    """
    Home
    
    This is just the welcome message.
    """
    
    return jsonify_message("Welcome to userService.")

@app.route("/login", methods=["GET"])
async def login():
    """"
    Login
    
    Authenticate user from username & password pass through the header.
    """
    username = ''
    password = ''
    if request.authorization:
        username = request.authorization.username
        password = request.authorization.password
        db = await _get_db()
        query = "SELECT username, pwd FROM user WHERE username = :username AND pwd = :pwd"
        app.logger.info(query), app.logger.warning(query)
        user = await db.fetch_one(query=query, values={"username": username, "pwd": password})
        print(request.authorization)
        if not user:
            return jsonify_message("Invalid/ Missing username or password. Send based64(username:password) in Authorization header"), 401, {"WWW-Authenticate": "Basic"}
        return {"authenticated": True}, 200
    else:
        return 'Could not Verify',401,{'www-Authenticate':'Basic realm = "Login Required"'}
    
    # if request.method == "GET":
    #     return jsonify_message("Send as POST with based64(username:password) in Authorization header.")
    # else:


@app.route("/register", methods=["GET", "POST"])
async def register():
    """
    Register
    
    Register a user. 
    Note: Use HTTPie to test this route (not /docs or /redocs). See README.md for more info.
    """

    if request.method == "GET":
        return jsonify_message("Pass in username and password in POST request!!!")
    else:
        data = await request.get_json()
        db =  await _get_db()

        if not data or 'username' not in data or 'password' not in data:
            return jsonify_message("Required username and password"), 400
        is_user = await is_user_exists(db, data['username'])
        if is_user :
            return jsonify_message("Username not availabe"), 400

        await insert_user(db, data["username"], data["password"])
        return jsonify_message("User registered")
