from flask import Flask, request, jsonify

app = Flask(__name__)


books = [
    {"id": 1, "title": "Harry Potter", "author": "J.K. Rowling"},
    {"id": 2, "title": "The Alchemist", "author": "Paulo Coelho"}
]


@app.route('/')
def home():
    return "<h2>Welcome to the Books API!</h2><p>Use <code>/books</code> to view all books.</p>"


@app.route('/books', methods=['GET','POST'])
def get_books():
    return jsonify(books)


@app.route('/books/<int:book_id>', methods=['GET','POST'])
def get_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    return jsonify(book) if book else (jsonify({"error": "Book not found"}), 404)


@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    new_id = max([b["id"] for b in books]) + 1 if books else 1
    new_book = {"id": new_id, "title": data["title"], "author": data["author"]}
    books.append(new_book)
    return jsonify(new_book), 201


@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    for book in books:
        if book["id"] == book_id:
            book["title"] = data.get("title", book["title"])
            book["author"] = data.get("author", book["author"])
            return jsonify(book)
    return jsonify({"error": "Book not found"}), 404


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    books = [b for b in books if b["id"] != book_id]
    return jsonify({"message": "Book deleted successfully"}), 200


if __name__ == '__main__':
    app.run(debug=True)
