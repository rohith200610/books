from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import sqlite3


app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['DATABASE'] = 'users.db'

# Database helper functions
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            account_type TEXT,
            password TEXT NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL
        )''')
        db.commit()

init_db()






# JWT token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[-1]
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (data['username'],))
            user_row = cursor.fetchone()
            if not user_row:
                return jsonify({'error': 'User not found!'}), 401
            current_user = {
                'id': user_row[0],
                'username': user_row[1],
                'email': user_row[2],
                'account_type': user_row[3],
                'password': user_row[4]
            }
        except Exception as e:
            return jsonify({'error': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        email = data.get('email')
        account_type = data.get('account_type')
        password = data.get('password')
        valid_types = ['viewer', 'author', 'admin']
        if not username or not password or not account_type:
            return jsonify({'error': 'Username, password, and account_type required'}), 400
        if account_type not in valid_types:
            return jsonify({'error': f"account_type must be one of {valid_types}"}), 400
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return jsonify({'error': 'User already exists'}), 409
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, email, account_type, password) VALUES (?, ?, ?, ?)",
                       (username, email, account_type, hashed_password))
        db.commit()
        return jsonify({'message': 'User registered successfully', 'user': {'username': username, 'account_type': account_type, 'email': email}}), 201
    else:
        return jsonify({'message': 'Send a POST request with username and password to register.'})


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        if user_row and check_password_hash(user_row[4], password):
            token = jwt.encode({
                'username': user_row[1],
                'account_type': user_row[3],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            return jsonify({'message': 'Login successful', 'token': token, 'user': {'username': user_row[1], 'account_type': user_row[3]}}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    else:
        return jsonify({'message': 'Send a POST request with username and password to login.'})




@app.route('/books', methods=['GET'])
@token_required
def get_books(current_user):
    if current_user['account_type'] not in ['viewer', 'author', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM books')
    books = [{'id': row[0], 'title': row[1], 'author': row[2]} for row in cursor.fetchall()]
    return jsonify(books)




@app.route('/books/<int:book_id>', methods=['GET'])
@token_required
def get_book(current_user, book_id):
    if current_user['account_type'] not in ['viewer', 'author', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    row = cursor.fetchone()
    if row:
        book = {'id': row[0], 'title': row[1], 'author': row[2]}
        return jsonify(book)
    else:
        return jsonify({'error': 'Book not found'}), 404




@app.route('/books', methods=['GET','POST'])
@token_required
def add_book(current_user):
    if current_user['account_type'] not in ['author', 'admin']:
        return jsonify({'error': 'Only authors and admins can add books'}), 403
    data = request.json
    title = data.get('title')
    author = data.get('author')
    if not title or not author:
        return jsonify({'error': 'Title and author required'}), 400
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO books (title, author) VALUES (?, ?)', (title, author))
    db.commit()
    new_id = cursor.lastrowid
    return jsonify({'id': new_id, 'title': title, 'author': author}), 201




@app.route('/books/<int:book_id>', methods=['PUT'])
@token_required
def update_book(current_user, book_id):
    if current_user['account_type'] not in ['author', 'admin']:
        return jsonify({'error': 'Only authors and admins can update books'}), 403
    data = request.json
    title = data.get('title')
    author = data.get('author')
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE books SET title = ?, author = ? WHERE id = ?', (title, author, book_id))
    db.commit()
    cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    row = cursor.fetchone()
    if row:
        book = {'id': row[0], 'title': row[1], 'author': row[2]}
        return jsonify(book)
    else:
        return jsonify({'error': 'Book not found'}), 404




@app.route('/books/<int:book_id>', methods=['DELETE'])
@token_required
def delete_book(current_user, book_id):
    if current_user['account_type'] not in ['admin', 'author']:
        return jsonify({'error': 'Only admins and authors can delete books'}), 403
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
    db.commit()
    return jsonify({'message': 'Book deleted successfully'}), 200


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
