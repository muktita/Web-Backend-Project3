# Initialize database and populate initial values:

from databases import Database

import asyncio
import json

database = Database('sqlite+aiosqlite:///wordle.db')
userDatabase = Database('sqlite+aiosqlite:///user.db')

async def init_db():
    await userDatabase.connect()

    query = "DROP TABLE IF EXISTS user"
    await userDatabase.execute(query=query)
    
    query = """
            CREATE TABLE user (
                userid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                username TEXT NOT NULL UNIQUE, 
                pwd BLOB NOT NULL
            )
            """
    await userDatabase.execute(query=query)

    print("User database has been initiailized.")

async def wordle_db():
    await database.connect()

    query = "DROP TABLE IF EXISTS games"
    await database.execute(query=query)
    query = "DROP TABLE IF EXISTS guesses"
    await database.execute(query=query)
    query = "DROP TABLE IF EXISTS secret_word"
    await database.execute(query=query)
    query = "DROP TABLE IF EXISTS valid_words"
    await database.execute(query=query)



    query = """ 
            CREATE TABLE games (
                gameid TEXT NOT NULL PRIMARY KEY ,
                username TEXT NOT NULL,
                secretWord TEXT NOT NULL,
                isActive INTEGER DEFAULT 1 NOT NULL,
                hasWon INTEGER DEFAULT 0 NOT NULL
            )
            """
    await database.execute(query=query)

    query = """
            CREATE TABLE guesses (
                guessid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                gameid INTEGER NOT NULL,
                guess TEXT NOT NULL,
                UNIQUE(gameid, guess)
            )
            """
    await database.execute(query=query)

    query = """ 
            CREATE TABLE secret_word (
                word TEXT PRIMARY KEY
            )
            """
    await database.execute(query=query)

    query = """ 
            CREATE TABLE valid_words (
                word TEXT PRIMARY KEY
            )
            """
    await database.execute(query=query)



# Uncomment in main() for this function to be able to execute: (REMEMBER)
async def populate_tables():
    # fill secret_word and valid_words with words from correct.json and valid.json respectively
    correct_json = open("share/correct.json")
    valid_json = open("share/valid.json")
    
    print("Populating secret_word table...")
    query = """
            INSERT INTO secret_word (word) VALUES (:word)
            """
    correct_words = [{"word": word} for word in json.load(correct_json)]
    await database.execute_many(query=query, values=correct_words)

    print("Populating valid_words table...")
    query = """
            INSERT INTO valid_words (word) VALUES (:word)
            """
    valid_words = [{"word": word} for word in json.load(valid_json)]
    await database.execute_many(query=query, values=valid_words)
    await database.execute_many(query=query, values=correct_words)



def main():
    asyncio.run(init_db()) 
    asyncio.run(wordle_db())
    asyncio.run(populate_tables())

if __name__ == "__main__":
    main()