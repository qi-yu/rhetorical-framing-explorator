import json
import psycopg2
from flask import Flask, jsonify
from flask_cors import CORS

# PostgreSQL connection parameters
db_params = {
    'dbname': 'rhetorical-framing-explorator',
    'user': 'postgres',
    'password': 'rfe2023',
    'host': 'localhost',
    'port': '5432'
}

app = Flask(__name__)
CORS(app)

def create_table():
    # Connect to the database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS rhetorical_framing_features (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        dimension TEXT NOT NULL,
        CONSTRAINT unique_name_dimension PRIMARY KEY (name, dimension)
    )
    '''
    cursor.execute(create_table_query)


def read_data_from_database():
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Retrieve data from the database
        select_query = '''
        SELECT name, dimension FROM rhetorical_framing_features
        '''
        cursor.execute(select_query)

        # Fetch all data and store in a list of dictionaries
        data = [{'name': row[0], 'dimension': row[1]} for row in cursor.fetchall()]

        # Close the connection
        cursor.close()
        conn.close()

        return data

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/')
def read_json_and_insert():
    try:
        # Read data from the JSON file
        with open('../backend/assets/features.json', 'r') as json_file:
            data = json.load(json_file)

        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Insert data into the database
        for item in data:
            insert_query = '''
            INSERT INTO rhetorical_framing_features (name, dimension) VALUES (%s, %s)
            ON CONFLICT (name, dimension) DO NOTHING
            '''
            cursor.execute(insert_query, (item['name'], item['dimension']))

        # Commit changes and close the connection
        conn.commit()
        cursor.close()
        conn.close()

        # Return the data added to the database
        return jsonify(read_data_from_database())

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    create_table()  # Create the table when the script is executed
    app.run(debug=True)