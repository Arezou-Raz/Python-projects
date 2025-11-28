import sqlite3
import os
from flask import Flask, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash

# --- Global Configuration & Database Setup ---
# FIX 1: Database name must be a string literal.
DATABASE = 'library.db'
app = Flask(__name__)
app.secret_key = 'super_secret_key_for_session' # Insecure, use environment variable in production

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Closes the database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database schema."""
    with app.app_context():
        db = get_db()
        # Create users table for authentication
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hash TEXT NOT NULL
            )
        ''')
        # Create items table for the library catalog
        # FIX 2: Ensure schema aligns with 'Book' and 'Audiobook' only (no rating).
        db.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                author TEXT,
                item_type TEXT NOT NULL, -- e.g., 'Book', 'Audiobook'
                status TEXT NOT NULL,    -- e.g., 'Owned', 'Wishlist', 'Loaned Out'
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        db.commit()

# Ensure the database is initialized when the application starts
init_db()

# --- HTML TEMPLATES (Embedded due to single-file constraint) ---

def render_template(title, content):
    """Generates the full HTML page structure with embedded Tailwind CSS."""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body {{ font-family: 'Inter', sans-serif; background-color: #f7f9fb; }}
    </style>
</head>
<body class="min-h-screen p-4 sm:p-8">
    <div class="max-w-7xl mx-auto">
        <header class="flex justify-between items-center py-4 border-b border-gray-200 mb-6">
            <h1 class="text-3xl font-bold text-gray-800">My Library Manager (Books & Audiobooks)</h1>
            <nav class="flex space-x-4">
                {'<a href="/library" class="text-indigo-600 hover:text-indigo-800 font-medium">My Library</a>' if 'user_id' in session else ''}
                {'<a href="/add" class="text-indigo-600 hover:text-indigo-800 font-medium">Add Item</a>' if 'user_id' in session else ''}
                {'<a href="/logout" class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg text-sm font-semibold transition duration-150 shadow-md">Logout</a>' if 'user_id' in session else '<a href="/login" class="text-indigo-600 hover:text-indigo-800 font-medium">Login</a>'}
            </nav>
        </header>

        <main class="bg-white p-6 sm:p-10 rounded-xl shadow-lg">
            {content}
        </main>
    </div>
</body>
</html>
"""

def form_content(title, endpoint, fields, submit_text, error=None):
    """Generates the HTML for a form (used for login, register, and add/edit item)."""
    form_html = f'<h2 class="text-2xl font-semibold mb-6 text-gray-800">{title}</h2>'
    if error:
        form_html += f'<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert"><p>{error}</p></div>'

    form_html += f'<form method="POST" action="{endpoint}" class="space-y-4">'
    for label, name, input_type, value in fields:
        value = value if value is not None else ''

        form_html += f"""
            <div>
                <label for="{name}" class="block text-sm font-medium text-gray-700">{label}</label>
        """

        if input_type == 'select':
            form_html += f'<select id="{name}" name="{name}" class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border">'

            # FIX 3: Updated item_type options to only include 'Book' and 'Audiobook'.
            if name == 'item_type':
                options = ['Book', 'Audiobook']
            # Status options (remain the same)
            elif name == 'status':
                options = ['Owned', 'Wishlist', 'Loaned Out']
            else:
                options = []

            for option in options:
                selected = 'selected' if str(option) == str(value) else ''
                form_html += f'<option value="{option}" {selected}>{option}</option>'

            form_html += '</select>'
        else:
            form_html += f"""
                <input type="{input_type}" id="{name}" name="{name}" value="{value}" class="mt-1 block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border" required>
            """

        form_html += '</div>'


    form_html += f"""
        <button type="submit" class="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg transition duration-150 shadow-lg hover:shadow-xl">
            {submit_text}
        </button>
    </form>
    """
    return form_html

# --- Application Routes ---

@app.before_request
def load_user():
    """Check if the user is logged in before every request."""
    g.user_id = session.get('user_id')

@app.route('/')
def index():
    """Index page: redirects to library if logged in, otherwise to login."""
    if g.user_id:
        return redirect(url_for('library'))
    return redirect(url_for('login'))

# --- AUTHENTICATION ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user_exists = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()

        if not username or not password:
            error = "Must provide username and password"
        elif user_exists:
            error = "Username already taken"
        else:
            try:
                db.execute(
                    "INSERT INTO users (username, hash) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                db.commit()
                # Auto-login after registration
                user_id = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()['id']
                session['user_id'] = user_id
                return redirect(url_for('library'))
            except sqlite3.Error as e:
                error = f"Database error during registration: {e}"

    fields = [
        ('Username', 'username', 'text', ''),
        ('Password', 'password', 'password', '')
    ]
    content = form_content('Register', '/register', fields, 'Register', error)
    content += '<p class="mt-6 text-center text-gray-600">Already have an account? <a href="/login" class="text-indigo-600 hover:text-indigo-800 font-semibold">Log In</a></p>'
    return render_template('Register', content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user is None:
            error = "Invalid username or password"
        elif not check_password_hash(user['hash'], password):
            error = "Invalid username or password"
        else:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('library'))

    fields = [
        ('Username', 'username', 'text', ''),
        ('Password', 'password', 'password', '')
    ]
    content = form_content('Log In', '/login', fields, 'Log In', error)
    content += '<p class="mt-6 text-center text-gray-600">Need an account? <a href="/register" class="text-indigo-600 hover:text-indigo-800 font-semibold">Register</a></p>'
    return render_template('Log In', content)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- LIBRARY MANAGEMENT ROUTES ---

@app.route('/library', methods=['GET'])
def library():
    """Displays the user's library with filtering and search."""
    if not g.user_id:
        return redirect(url_for('login'))

    db = get_db()

    # Get filter and search parameters from URL
    search_term = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    item_type_filter = request.args.get('type', '').strip()

    query = "SELECT * FROM items WHERE user_id = ?"
    params = [g.user_id]

    # Build query dynamically based on filters/search
    if search_term:
        query += " AND (title LIKE ? OR author LIKE ?)"
        # Note: Using %term% allows searching anywhere in the title/author
        params.extend([f"%{search_term}%", f"%{search_term}%"])

    if item_type_filter: # Filter by type (Book or Audiobook)
        query += " AND item_type = ?"
        params.append(item_type_filter)

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY title ASC"

    items = db.execute(query, params).fetchall()

    # Create HTML content for filters and the item table
    filter_options = """
    <form method="GET" action="/library" class="mb-8 p-4 bg-gray-50 rounded-lg flex flex-wrap gap-4 items-end shadow-inner">
        <div>
            <label for="q" class="block text-sm font-medium text-gray-700">Search Title/Author</label>
            <input type="text" id="q" name="q" value="{search_term}" placeholder="e.g., Dune, Python" class="mt-1 p-2 border border-gray-300 rounded-lg w-full">
        </div>

        <div>
            <label for="type" class="block text-sm font-medium text-gray-700">Filter by Type</label>
            <select id="type" name="type" class="mt-1 p-2 border border-gray-300 rounded-lg">
                <option value="">All Types</option>
                <option value="Book" {selected_book_filter}>Book</option>
                <option value="Audiobook" {selected_audiobook_filter}>Audiobook</option>
            </select>
        </div>

        <div>
            <label for="status" class="block text-sm font-medium text-gray-700">Filter by Status</label>
            <select id="status" name="status" class="mt-1 p-2 border border-gray-300 rounded-lg">
                <option value="">All Statuses</option>
                <option value="Owned" {selected_owned}>Owned</option>
                <option value="Wishlist" {selected_wishlist}>Wishlist</option>
                <option value="Loaned Out" {selected_loaned}>Loaned Out</option>
            </select>
        </div>

        <button type="submit" class="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition duration-150 shadow-md">
            Apply Filters
        </button>
        <a href="/library" class="text-gray-600 hover:text-gray-800 py-2 px-4">Clear</a>
    </form>
    """.format(
        search_term=search_term,
        # FIX 4: Updated item_type options in the /library filter section.
        selected_book_filter='selected' if item_type_filter == 'Book' else '',
        selected_audiobook_filter='selected' if item_type_filter == 'Audiobook' else '',
        # Status filters
        selected_owned='selected' if status_filter == 'Owned' else '',
        selected_wishlist='selected' if status_filter == 'Wishlist' else '',
        selected_loaned='selected' if status_filter == 'Loaned Out' else '',
    )

    table_rows = ""
    if items:
        for item in items:
            # Set color based on status
            status_color = {'Owned': 'bg-green-100 text-green-800', 'Wishlist': 'bg-yellow-100 text-yellow-800', 'Loaned Out': 'bg-red-100 text-red-800'}.get(item['status'], 'bg-gray-100 text-gray-800')

            table_rows += f"""
            <tr class="border-b hover:bg-gray-50">
                <td class="px-6 py-4 font-medium text-gray-900">{item['title']}</td>
                <td class="px-6 py-4 text-gray-700">{item['author'] or 'N/A'}</td>
                <td class="px-6 py-4 text-gray-700">{item['item_type']}</td>
                <td class="px-6 py-4">
                    <span class="text-xs font-medium me-2 px-2.5 py-0.5 rounded-full {status_color}">
                        {item['status']}
                    </span>
                </td>
                <td class="px-6 py-4">
                    <a href="{url_for('edit_item', item_id=item['id'])}" class="text-indigo-600 hover:text-indigo-900 font-semibold">Edit</a>
                </td>
            </tr>
            """
    else:
        table_rows = '<tr><td colspan="5" class="px-6 py-8 text-center text-gray-500">No items found matching your criteria. <a href="/add" class="text-indigo-600 hover:underline">Add one?</a></td></tr>'


    content = f"""
        <h2 class="text-3xl font-bold mb-6 text-gray-800">Your Book & Audiobook Catalog</h2>
        {filter_options}

        <div class="overflow-x-auto shadow-md rounded-lg">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Author/Creator</th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    {table_rows}
                </tbody>
            </table>
        </div>
        <p class="mt-6 text-center">
            <a href="/add" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition duration-150">
                Add New Item
            </a>
        </p>
    """
    return render_template('My Library', content)


@app.route('/add', methods=['GET', 'POST'])
def add_item():
    """Route to add a new item to the library."""
    if not g.user_id:
        return redirect(url_for('login'))

    error = None
    if request.method == 'POST':
        title = request.form['title']
        author = request.form.get('author')
        item_type = request.form['item_type']
        status = request.form['status']

        if not title or not item_type or not status:
            error = "Title, Type, and Status are required fields."
        else:
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO items (user_id, title, author, item_type, status) VALUES (?, ?, ?, ?, ?)",
                    (g.user_id, title, author, item_type, status)
                )
                db.commit()
                return redirect(url_for('library'))
            except sqlite3.Error as e:
                error = f"Database error: {e}"

    # Default values for GET request
    fields = [
        ('Title', 'title', 'text', ''),
        ('Author/Creator', 'author', 'text', ''),
        ('Type', 'item_type', 'select', 'Book'), # Default to Book
        ('Status', 'status', 'select', 'Owned'),  # Default to Owned
    ]
    content = form_content('Add New Item', '/add', fields, 'Add Item', error)
    return render_template('Add Item', content)


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    """Route to edit or delete an existing item."""
    if not g.user_id:
        return redirect(url_for('login'))

    db = get_db()
    item = db.execute(
        "SELECT * FROM items WHERE id = ? AND user_id = ?", (item_id, g.user_id)
    ).fetchone()

    if not item:
        content = '<p class="text-red-500">Item not found or unauthorized access.</p>'
        return render_template('Error', content), 404

    error = None

    if request.method == 'POST':
        # Check for delete operation (using a hidden field)
        if 'delete_confirm' in request.form:
            try:
                db.execute("DELETE FROM items WHERE id = ?", (item_id,))
                db.commit()
                # Redirect to library on successful delete
                return redirect(url_for('library'))
            except sqlite3.Error as e:
                error = f"Database error during deletion: {e}"
        else:
            # Handle Update operation
            title = request.form['title']
            author = request.form.get('author')
            item_type = request.form['item_type']
            status = request.form['status']

            if not title or not item_type or not status:
                error = "Title, Type, and Status are required fields."
            else:
                try:
                    db.execute(
                        "UPDATE items SET title = ?, author = ?, item_type = ?, status = ? WHERE id = ?",
                        (title, author, item_type, status, item_id)
                    )
                    db.commit()
                    return redirect(url_for('library'))
                except sqlite3.Error as e:
                    error = f"Database error during update: {e}"

        # If update failed, reload item data for form
        item = db.execute(
            "SELECT * FROM items WHERE id = ? AND user_id = ?", (item_id, g.user_id)
        ).fetchone()


    # Fields for GET request or error state
    fields = [
        ('Title', 'title', 'text', item['title']),
        ('Author/Creator', 'author', 'text', item['author'] if item['author'] else ''),
        ('Type', 'item_type', 'select', item['item_type']),
        ('Status', 'status', 'select', item['status']),
    ]

    # Generate the form for editing
    edit_form = form_content(f'Edit Item: {item["title"]}', url_for('edit_item', item_id=item_id), fields, 'Update Item', error)

    # Add delete functionality
    delete_section = f"""
    <div class="mt-8 border-t pt-4 border-red-200">
        <h3 class="text-xl font-semibold text-red-600 mb-2">Danger Zone</h3>
        <p class="text-sm text-gray-600 mb-4">Permanently remove this item from your library. This action cannot be undone.</p>

        <form method="POST" action="{url_for('edit_item', item_id=item_id)}" onsubmit="return confirm('Are you sure you want to delete this item?')" class="inline-block">
            <input type="hidden" name="delete_confirm" value="1">
            <button type="submit" class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition duration-150 shadow-lg">
                Delete Item
            </button>
        </form>
    </div>
    """


    content = edit_form + delete_section
    return render_template('Edit Item', content)


# --- Run the Application ---
if __name__ == '__main__':
    # Initialize the database file if it doesn't exist
    if not os.path.exists(DATABASE):
        init_db()

    # Run the application (accessible via http://127.0.0.1:5000/)
    print("--- Library Manager is running. Access it at http://127.0.0.1:5000/ ---")
    app.run(debug=True)
