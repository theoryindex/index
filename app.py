from flask import Flask, render_template
import database

app = Flask(__name__, static_folder='templates/static')

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/authors')
def authors():
    query = "SELECT * FROM authors"
    results = database.execute_query(query, ())
    return render_template('authors.html', authors=results)

@app.route('/books')
def books():
    # TODO: Implement books page
    return render_template('books.html')

@app.route('/global_index')
def global_index():
    # TODO: Implement global index page
    return render_template('global_index.html')

@app.route('/author/<int:author_id>')
def author_index(author_id):
    author_query = "SELECT * FROM authors WHERE id = %s"
    author_result = database.execute_query(author_query, (author_id,))
    author = author_result[0] if author_result else None

    term_query = '''
        SELECT DISTINCT term, term_id
        FROM books
        WHERE author_id = %s AND type = 'index'
    '''
    term_results = database.execute_query(term_query, (author_id,))

    return render_template('author_index.html', author=author, terms=term_results)

@app.route('/author/<int:author_id>/<term>')
def term_index(author_id, term):
    author_query = "SELECT name FROM authors WHERE id = %s"
    author_result = database.execute_query(author_query, (author_id,))
    author_name = author_result[0]['name']

    # Get the book titles and publishers
    book_query = "SELECT book_title, publisher FROM books WHERE author_id = %s AND term = %s ORDER BY publication_date ASC"
    book_results = database.execute_query(book_query, (author_id, term))

    # Group the book titles and publishers by book
    books = {}
    for book_result in book_results:
        book_title = book_result['book_title']
        publisher = book_result['publisher']
        if book_title not in books:
            books[book_title] = {'publisher': publisher, 'pages': []}

    # Get all pages for the index term and each book
    term_id_query = "SELECT term_id FROM books WHERE author_id = %s AND term = %s LIMIT 1"
    term_id_result = database.execute_query(term_id_query, (author_id, term))
    term_id = term_id_result[0]['term_id']

    for book_title, book_data in books.items():
        pages_query = "SELECT page FROM books WHERE author_id = %s AND term_id = %s AND book_title = %s AND publisher = %s"
        pages_results = database.execute_query(pages_query, (author_id, term_id, book_title, book_data['publisher']))
        pages = [result['page'] for result in pages_results]
        books[book_title]['pages'] = pages

    # Get all index and sub-index terms for this author
    term_query = '''SELECT term, page, type FROM books WHERE author_id = %s AND type IN ('index', 'sub-index')'''
    term_results = database.execute_query(term_query, (author_id,))

    # Group the results by index term and sub-index terms
    index_terms = []
    current_index_term = None

    for result in term_results:
        if result['type'] == 'index':
            current_index_term = {'term': result['term'], 'pages': result['page'], 'sub_index_terms': []}
            index_terms.append(current_index_term)
        elif current_index_term is not None:
            current_index_term['sub_index_terms'].append({'term': result['term'], 'pages': result['page']})

    # Find the index term that was clicked
    selected_index_term = None
    for index_term in index_terms:
        if index_term['term'] == term:
            selected_index_term = index_term
            break

    return render_template('term_index.html', author_name=author_name, term=term, books=books, index_term=selected_index_term, book_title=book_title)

if __name__ == '__main__':
    app.run(debug=True)