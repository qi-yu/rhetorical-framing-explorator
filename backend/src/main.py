import json, os, logging, shutil, subprocess
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from src.config import Config
from src.annotation.annotating import RunAnnotation

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

logging.basicConfig(level=logging.INFO)


def create_feature_table():
    # Connect to the database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    drop_table_query = '''
    DROP TABLE IF EXISTS rhetorical_framing_features
    '''
    cursor.execute(drop_table_query)
    conn.commit()

    # Create the table if it doesn't exist
    create_table_query = '''
    CREATE TABLE rhetorical_framing_features (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        dimension TEXT NOT NULL,
        annotation_method TEXT NOT NULL,
        CONSTRAINT unique_name_dimension UNIQUE (name, dimension)
    )
    '''
    cursor.execute(create_table_query)
    conn.commit()

    # Insert data into the database
    with open(Config.FEATURE_CONFIG_PATH, 'r') as json_file:
        data = json.load(json_file)

    for item in data:
        insert_query = '''
        INSERT INTO rhetorical_framing_features (name, dimension, annotation_method) VALUES (%s, %s, %s)
        ON CONFLICT (name, dimension) DO NOTHING
        '''
        cursor.execute(insert_query, (item['name'], item['dimension'], item['annotation_method']))

    conn.commit()

    cursor.close()
    conn.close()
    logging.info('Table rhetorical_framing_features is created.')


def create_uploaded_files_table():
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
        logging.info("The old table 'uploaded_files' is deleted.")

    create_table_query = '''
    CREATE TABLE uploaded_files (
        id SERIAL PRIMARY KEY,
        filename TEXT NOT NULL,
        format TEXT NOT NULL,
        size INTEGER NOT NULL,
        selectedForAnalyses BOOLEAN NOT NULL
    )
    '''
    cursor.execute(create_table_query)
    conn.commit()
    logging.info("New table 'uploaded_files' is created.")
       
    cursor.close()
    conn.close()


@app.route('/')
def get_features():
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Retrieve data from the database
        select_query = '''
        SELECT * FROM rhetorical_framing_features
        '''
        cursor.execute(select_query)

        # Fetch all data and store in a list of dictionaries
        data = [{'id': row[0], 'name': row[1], 'dimension': row[2], 'annotation_method': row[3]} for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify(data)

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

        uploaded_files_info = []

        for file in files:
            if file.filename == '':
                return jsonify({'error': 'No file selected'})

            filename = secure_filename(file.filename).split('.')[0]
            file_path = os.path.join(Config.RAW_FILE_PATH, secure_filename(file.filename))
            file.save(file_path)

            file_format = '.' + file.filename.split('.')[-1]
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
                INSERT INTO uploaded_files (filename, format, size, selectedForAnalyses) VALUES (%s, %s, %s, %s)
                '''
                cursor.execute(insert_query, (filename, file_format, file_size, selectedForAnalyses))
                conn.commit()

            cursor.close()
            conn.close()

            uploaded_files_info.append({'filename': filename, 'format': file_format, 'size': file_size, 'selectedForAnalyses': selectedForAnalyses})

        return jsonify(uploaded_files_info)

    except Exception as e:
        return jsonify({'error': str(e)})

    
@app.route('/uploaded_files')
def get_uploaded_files():
    try:
        uploaded_files = []

        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        select_query = '''
        SELECT id, filename, format, size, selectedForAnalyses FROM uploaded_files
        ORDER BY id
        '''
        cursor.execute(select_query)
        results = cursor.fetchall()

        for result in results:
            file_id, filename, format, size, selected_for_analyses = result
            uploaded_files.append({'id': file_id, 'filename': filename, 'format': format, 'size': size, 'selectedForAnalyses': selected_for_analyses})

        cursor.close()
        conn.close()

        return jsonify(uploaded_files)
    
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/delete/<id>', methods=['DELETE'])
def delete_file(id):
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        select_query = '''
        SELECT * FROM uploaded_files WHERE id = %s
        '''
        cursor.execute(select_query, (id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'File not found'})

        filename = result[1]
        file_format = result[2]
        file_path = os.path.join(Config.RAW_FILE_PATH, filename + file_format)

        # Delete the file from the server's upload folder
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"File '{filename}' deleted from the server.")
        else:
            logging.warning(f"File '{filename}' not found on the server.")


        # Delete the file from the database
        delete_query = '''
        DELETE FROM uploaded_files WHERE id = %s
        '''
        cursor.execute(delete_query, (id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'message': 'File deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/rename/<id>', methods=['PUT'])
def rename_file(id):
    try:
        new_filename = request.json.get('filename')

        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        select_query = '''
        SELECT filename, format FROM uploaded_files WHERE id = %s
        '''
        cursor.execute(select_query, (id,))
        old_filename, format = cursor.fetchone()

        # Rename the file at the database
        update_query = '''
        UPDATE uploaded_files
        SET filename = %s
        WHERE id = %s
        '''
        cursor.execute(update_query, (new_filename, id))
        conn.commit()
        cursor.close()
        conn.close()

        # Rename the file at the server's upload folder
        os.rename(os.path.join(Config.RAW_FILE_PATH, old_filename + format), os.path.join(Config.RAW_FILE_PATH, new_filename + format))

        return jsonify({'message': 'File name updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/annotate', methods=['POST'])
def annotate():
    selected_features = request.json.get('selected_features')
    logging.info('Start annotation...')

    run_annotation = RunAnnotation()

    try:
        subprocess.run(['python', Config.PREPROCESSING_SCRIPT_PATH, 'preprocessing'])

        for feature in selected_features:
            run_annotation.annotate_feature(feature['annotation_method'])
            
        return jsonify({'message': 'Script executed successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/progress', methods=['GET'])
def get_progress():
    progress_folder = os.path.join(Config.PROGRESS_PATH)
    progress = {}

    try:
        for feature_file in os.listdir(progress_folder):
            feature_name = os.path.splitext(feature_file)[0]
            feature_progress_file = os.path.join(progress_folder, feature_file)

            with open(feature_progress_file, 'r') as file:
                feature_progress = float(file.read())
            
            progress[feature_name] = feature_progress
        
        return jsonify(progress)
    
    except Exception as e:
        return jsonify({'error': str(e)})
    

if __name__ == '__main__':
    for folder in [Config.RAW_FILE_PATH, Config.PREPROCESSED_FILE_PATH, Config.PROGRESS_PATH]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.mkdir(folder)

    create_feature_table()
    create_uploaded_files_table()
    app.run(debug=True)