import json, os, logging, shutil
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

logging.basicConfig(level=logging.INFO)

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


def create_uploaded_files_table():
    # Connect to the database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Check if the table exists
    cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'uploaded_files')")
    table_exists = cursor.fetchone()[0]

    # Delete table if it already exists
    if table_exists:
        drop_table_query = '''
        DROP TABLE IF EXISTS uploaded_files
        '''
        cursor.execute(drop_table_query)
        conn.commit()

    create_table_query = '''
    CREATE TABLE uploaded_files (
        id SERIAL PRIMARY KEY,
        filename TEXT NOT NULL,
        size INTEGER NOT NULL,
        selectedForAnalyses BOOLEAN NOT NULL
    )
    '''
    cursor.execute(create_table_query)
    conn.commit()
    logging.info("Table 'uploaded_files' created.")
       
    cursor.close()
    conn.close()



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

        # Get the list of uploaded files
        files = request.files.getlist('myfile')

        if not files:
            return jsonify({'error': 'No selected files'})

        # Create the 'upload' folder if it doesn't exist
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        uploaded_files_info = []

        for file in files:
            if file.filename == '':
                return jsonify({'error': 'No file selected'})

            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            file_size = os.path.getsize(file_path)
            selectedForAnalyses = True

            # ----- Insert the file details into the 'uploaded_files' table -----
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()

            ## Check if the file already exists in the database
            select_query = '''
            SELECT id FROM uploaded_files WHERE filename = %s
            '''
            cursor.execute(select_query, (filename,))
            result = cursor.fetchone()

            if not result: 
                insert_query = '''
                INSERT INTO uploaded_files (filename, size, selectedForAnalyses) VALUES (%s, %s, %s)
                '''

                cursor.execute(insert_query, (filename, file_size, selectedForAnalyses))
                conn.commit()

            cursor.close()
            conn.close()

            uploaded_files_info.append({'filename': filename, 'size': file_size, 'selectedForAnalyses': selectedForAnalyses})

        return jsonify(uploaded_files_info)

    except Exception as e:
        return jsonify({'error': str(e)})

    

@app.route('/uploaded_files')
def get_uploaded_files():
    try:
        uploaded_files = []

        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Retrieve the file details from the database
        select_query = '''
        SELECT id, filename, size, selectedForAnalyses FROM uploaded_files
        '''
        cursor.execute(select_query)
        results = cursor.fetchall()

        for result in results:
            file_id, filename, size, selected_for_analyses = result
            uploaded_files.append({'id': file_id, 'filename': filename, 'size': size, 'selectedForAnalyses': selected_for_analyses})

        cursor.close()
        conn.close()

        return jsonify(uploaded_files)
    
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Retrieve the file details from the database
        select_query = '''
        SELECT filename FROM uploaded_files WHERE filename = %s
        '''
        cursor.execute(select_query, (filename,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'File not found'})

        filename = result[0]
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Delete the file from the server's upload folder
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"File '{filename}' deleted from the server.")
        else:
            logging.warning(f"File '{filename}' not found on the server.")


        # Delete the file record from the database
        delete_query = '''
        DELETE FROM uploaded_files WHERE filename = %s
        '''
        cursor.execute(delete_query, (filename,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'File deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)

    create_feature_table()  # Create the table when the script is executed
    create_uploaded_files_table()  # Create the 'uploaded_files' table when the script is executed
    app.run(debug=True)