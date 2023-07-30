import json, os
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

# PostgreSQL connection parameters
db_params = {
    'dbname': 'rhetorical-framing-explorator',
    'user': 'postgres',
    'password': 'rfe2023',
    'host': 'localhost',
    'port': '5432'
}

UPLOAD_FOLDER = 'upload'

app = Flask(__name__)
CORS(app)


def create_feature_table():
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


def read_feature_from_database():
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


def create_file_upload_folder():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def read_json_and_insert_features():
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
        return jsonify(read_feature_from_database())

    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if the POST request has the file part
        if 'myfile' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['myfile']

        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        
        # Create the 'upload' folder if it doesn't exist
        create_file_upload_folder()

        # Save the uploaded file to the specified folder
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            file_size = os.path.getsize(file_path)

            return jsonify({'filename': filename, 'size': file_size})

    except Exception as e:
        return jsonify({'error': str(e)})
    


@app.route('/upload')
def get_uploaded_files():
    try:
        uploaded_files = []

        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file_size = os.path.getsize(file_path)
            uploaded_files.append({'filename': filename, 'size': file_size})
        
        return jsonify(uploaded_files)
    
    except Exception as e:
        return jsonify({'error': str(e)})
    

if __name__ == '__main__':
    create_feature_table()  # Create the table when the script is executed
    app.run(debug=True)