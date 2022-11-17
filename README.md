# CPSC 449 - Project 1 - Wordle Mock Backend

This is the main repository for the Wordle Mock Backend App. This README describes how to run the app and test the various access points.

### Authors
Section 02
Group 20
Members: 
- Divyansh Mohan Rao (divyanshrao@csu.fullerton.edu)
- Ken Cue (kencue@csu.fullerton.edu)
- Sam Le (hle406@csu.fullerton.edu)
- Sam Truong (samtruonh@csu.fullerton.edu)


## Setup
### Requirements
- Python 3 (with pip)
- Quart
- SQLite 3
- Databases
- SQLAlchemy (==v1.4.41) *see [Known Issues](#known-issues) section*
- Foreman
- Quart-Schema
- HTTPie
- PyTest (including pytest-asyncio)

Run the following commands if any of the required libraries are missing:
```
$ sudo snap install httpie
$ sudo apt update
$ sudo apt install --yes python3-pip ruby-foreman sqlite3

$ python3 -m pip install --upgrade quart[dotenv] click markupsafe Jinja2
$ python3 -m pip install sqlalchemy==1.4.41
$ python3 -m pip install databases[aiosqlite]
$ python3 -m pip install pytest pytest-asyncio
```

### Initializing the Database
Before running the app, run the following command to initialize the database and populate the tables for the correct and valid words.
```
$ ./init.sh
```

Pass the `-d` option if you wish to populate the `user`, `games` and `guesses` tables with test data.
```
$ ./init.sh -d
```

### Launching the App
Use the following command to start the app. Take note of the URI of the app in the output.
```
$ foreman start
```


## Database Structure
The app database currently has five total tables.
- `user`
    - used for authentication
    - contains the `username` and `pwd` fields
- `games`
    - the main game entry
    - a user can have as many games
    - apart from storing the `gameid` and `secretWord`, it also has the `isActive` and `hasWon` flags for tracking the state of the game.
    - `gameid` is the primary key, while `userid` is a foreign key
- `guesses`
    - each game can have as many guesses (currently capped at **six** based on project requirements)
    - `gameid` is a foreign key
- `secret_words`
    - this is a lookup table for potential secret words
    - imported from the official Wordle JSON
- `valid_words`
    - this is a lookup table for valid words
    - imported from the official Wordle JSON
    - this includes the secret_words (in contrast to the official Wordle JSON that does not include the secret words in its valid words list)



## Running the App
The HTTPie commands listed in this section run under the assumption that the default localhost URI `127.0.0.1` is used and that the port value of `3000` in `.env` has not been changed. 

### User Authentication Routes
#### Logging In
```
http POST http://127.0.0.1:3000/login --auth <username>:<password>
```
Using a `GET` request will display a message asking to use `POST`. It will return a `401` error if incorrectly guessed, and will return `{"authenticated": True}` if properly authenticated.

#### Registering a new user
```
http POST http://127.0.0.1:3000/register username=<new username> password=<new password>
```
Using a `GET` request will display a message asking to use `POST`. It will also give a `400` error when the username already exists.

### Wordle Game Routes
#### Starting a game
```
http POST http://127.0.0.1:3000/wordle/start username=<username>
```
This will only create a game. It will return the game ID, if successful. You will need to pass a valid username or else it will respond with a `400` error. It can also respond with a `409` error if any database issue happens.

#### List active games
```
http GET http://127.0.0.1:3000/wordle/<username>/games
```
This lists all the game IDs of the active games of the user. Note that this only lists **active** games -- unfinished games that are below the 6 guess limit.

#### Get the status of a specific game by ID
```
http GET http://127.0.0.1:3000/wordle/<username>/<gameid>/status
```
This retrieves all the relevant information of a particular **active** game. It provides a JSON string in the with the number guesses for the the current game along with all the previous guesses tied to that particular game. Each guess entry contains hints on which letters are in the secret word and in the correct spot or wrong spot.

Return JSON is in the form of:
```
{
    "num_guesses": num_guesses,
    "max_attempts": max_number_of_attempts,
    "guesses": [
        {
            "guess": guess_word,
            "correct_letters": [list of correct letters],
            "correct_indices": [list of correct indices]
        }
    ]
}
```

#### Making a guess
```
http POST http://127.0.0.1:3000/wordle/<string:username>/<int:gameid>/guess guess=<guess_word>
```
After verifying that the game is active and is owned by the username in the request, the `guess_word` is processed accordingly. 

First, the app verifies if it is a valid 5-letter string by checking if it exists in the `valid_words` table. If it does not exist, it will throw an error message accordingly, informing the user that the word is invalid. Invalid words do not affect the number of attempts.

If `guess_word` is valid, the app goes through a series of checks to see if the word is the secret word. If it is not the secret word, it will show the the hints (i.e. which letters in the wrong index and correct index). It will also record this guess as a valid attempt. If the number of guesses reaches the threshold number of attempts, it will end/lock the game (i.e. `isActive = False`). If the the guess was the secret word, it will set the `hasWon` flag to `True`.


## Error Routes
Any other routes or request types not specified above will get a `404` error, along with the following message:
```
{
    "error": "The resource could not be found"
}
```
`409` conflict errors are also caught with its corresponding error messages displayed accordingly.


## Quart-Schema Auto-Generated API Endpoint
Opening the following link `http://127.0.0.1:3000/docs` or `http://127.0.0.1:3000/redocs` in the browser while the server is running will show the API Schema (generated by Quart-Schema). You can test all of the routes specified above without needing to use HTTPie.


## Known Issues
- There seems to be an issue with SQLAlchemy v1.4.42 that breaks Databases. Downgrading to v1.4.41 seems to remove this issue as mentioned in [this StackOverflow entry](https://stackoverflow.com/questions/74089620/python-databases-library-cant-fetch-all-from-mysql-database).


## Relevant Links & Sources
- [Official Wordle Game](https://www.nytimes.com/games/wordle/index.html)
- [CPSC 449 Course Website](https://sites.google.com/view/cpsc-449)
- [Quart Documentation](https://quart.palletsprojects.com/en/latest/index.html)