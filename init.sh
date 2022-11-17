#!/bin/sh

echo "Initializing wordle_app database..."
python3 ./init_db.py

# Get the options
while getopts ":d" option; do
    case $option in
        d)  # -d - Development option. Populate user, games and guesses tables with dummy data.
            echo "-d option passed. Populating user, games and guesses tables with test data."
            sqlite3 ./wordle_app.db < ./share/dev_data.sql  
    esac
done

echo "Finished initializing database."

exit