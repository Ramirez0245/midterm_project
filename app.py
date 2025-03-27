from pymongo import MongoClient 
from flask import Flask, request, render_template, make_response, redirect, request, jsonify, abort, session
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from dotenv import load_dotenv
import jwt
import os

load_dotenv()

client = MongoClient(os.getenv('CONNECTION_STRING'))
database = client['mid_projct']
collection = database['user_info']

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
app.config['extentions'] = ['.pdf']

@app.route('/register', methods=['POST', 'GET'])
def register():
    print('START: register()')
    if request.method == "GET":
        return render_template('register.html' )
    
    if request.method == "POST":
        if collection.find_one({'username': request.form['username']}):
            return jsonify({'message': 'user already exist'})
        else:
            encypt_jwt = jwt.encode({'password': request.form['password']}, app.config['SECRET_KEY'], algorithm='HS256')
            data = {'username': request.form['username'], 'password': encypt_jwt}
            collection.insert_one(data)
            return jsonify({'message': 'user has been registered'}), 200

# Login route to generate JWT token
@app.route('/login', methods=['POST'])
def login():
    print('START: /login')
    auth = request.get_json()
    db_user = collection.find_one({'username': auth['username'] })
    token = jwt.decode(db_user['password'], app.config['SECRET_KEY'], algorithms=['HS256'])

    if auth and auth['password'] == token['password']:
        session['token'] = db_user['password']
        session['user'] = db_user['username']
        return jsonify({'token': db_user['password']}), 200
    
    return jsonify({'message': 'Incorrect username or password'}), 401

@app.route('/file_upload', methods=['POST', 'GET'])
def file_upload():
    print('START: fileupload()')
    print_info(request, 'request = ')
    print_info(request.files, 'request.files = ')
    if request.method == 'GET':
        return render_template('upload.html')
    
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename

        if os.path.splitext(filename)[1] not in app.config['extentions']:
            return jsonify({'message': 'Incorrectly uploaded file extension.'}), 406
        if file:
            file_upload_path = os.path.join('./uploads', file.filename)
            file.save(file_upload_path, 5000)

            return jsonify({'message': 'File has been uploaded!'}), 401
        return jsonify({'message': 'Incorrect username or password'}), 401
    return jsonify({'message': 'Incorrect method'}), 500

@app.route('/public', methods=['GET'])
def public():
    file_names = os.listdir('./uploads')
    data = os.listdir('./uploads')
    return render_template('public.html', data=data)

@app.route('/protected', methods=['GET'])
def protected():
    try:
        auth = request.get_json()

        if session:
            current_session_user = collection.find_one({'username': session['user']})

            token_password = jwt.decode(auth['token'], app.config['SECRET_KEY'], algorithms=['HS256'])
            session_password = jwt.decode(current_session_user['password'], app.config['SECRET_KEY'], algorithms=['HS256'])

            if token_password['password'] == session_password['password']:
                return render_template('private.html', data=current_session_user)

            return jsonify({'message': 'Incorrect username or password'}), 401
        return jsonify({'message': 'You are not logged in.'}), 400
    except NameError:
        return jsonify({'message': 'You are not logged in.'}), 400

# Homepage (/): Display all notes in the database
@app.route('/', methods=['GET'])
def home():
    try:
        return render_template('home.html' )
    except NameError:
        return "Error"    
@app.route('/logout', methods=['GET'])
def logout():
    if not session:
        return jsonify({'message': 'not session.clear()'}), 401
    else:
        session.clear()
        return jsonify({'message': 'session.clear()'}), 401



@app.route('/update_delete', methods=['GET', 'PUT', 'DELETE'])
def update_delete():
    print("START: update_delete()")
    auth = request.headers.get('token')

    print_info(auth, "auth = ")
    if session:  
        current_session_user = collection.find_one({'username': session['user']})
        token_password = jwt.decode(auth, app.config['SECRET_KEY'], algorithms=['HS256'])
        session_password = jwt.decode(current_session_user['password'], app.config['SECRET_KEY'], algorithms=['HS256'])

        if token_password['password'] == session_password['password']:
            if request.method == 'GET':
                return render_template('update_delete')   
            if request.method == 'PUT':
                collection.update_one( {'username': session['user']}, {'$set':   {'username': request.form['username'] }} )     
                session['user'] = request.form['username']
                return jsonify({'message': f'username updated to {session['user']}'}), 200
            if request.method == "DELETE":
                collection.delete_one({'username': session['user']})
                session.clear()
                return jsonify({'message': 'deleted user'}), 200

            print("if token_password['password'] == session_password['password']: ")
        return jsonify({'message': 'internal error'}), 500
    return jsonify({'message': 'you are not logged in'}), 401
@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist'    
    
    
def print_info(data, name):
    print('\nPrinting Data Info: ')
    print(f'{name}: ', data)
    print(f'type({name}): ', type(data))


if __name__ == '__main__':
    print("main")
    app.run(debug=True)
    os.getenv('CONNECTION_STRING')

