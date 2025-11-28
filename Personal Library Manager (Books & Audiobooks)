Personal Library Manager (Books & Audiobooks)

▶️ Video Demo: i need to do that

<(https://drive.google.com/file/d/1pZ4sjOd2qEuvwJFFZ2Zg_5VIX5wRpUto/view?usp=sharing)>

Personal Library Manager (Books & Audiobooks)

📚 About the Project

This is my Personal Library Manager, a web application I built using Python specifically the Flask framework and SQLite for the database. Basically, you can keep track of all your physical books and audiobooks.

I designed this project to show off some core full-stack development skills—getting secure login working, making sure the database keeps everyone's data separate, and building a solid CRUD system (Create, Read, Update, Delete). One of the things I’m proudest of is the dynamic catalog view—it lets you search and filter your collection all at once, which makes managing a big library super smooth!

✨ What It Can Do

The app is built around three main ideas: keeping your data safe, giving you control over your books reading journey, and making it easy to find books you already loaned ,still in your wishlist or loaned out.

Keeping Your Data Private & Secure
When you sign up, you can be sure your data is locked down.

Password Security: They're all hashed using werkzeug.security—that's standard practice to protect your credentials, even if someone somehow got into the database.

Data Isolation: Your library is just yours. Every item in the database is tagged with your unique user_id. This design choice means that even the code can't accidentally show or delete another user's items—it’s locked down at the database level.

Managing Your Collection
You have complete control over every item.

Item Types: You can clearly label things as either a Book or an Audiobook.

Tracking Status: It's more than a list! You can mark items as Owned, something on your Wishlist, or, importantly, if you’ve Loaned Out a copy .So don't forget who has your favorite novel

Handling Entries: The app has dedicated pages for quickly adding new items (/add), updating details (/edit/), or nuking an entry from the database if you don't need it anymore.

Finding What You Need
The main library page is where the magic of searching and filtering happens.

Combined Queries: You can mix and match filters and searches. Want to see all the Owned Audiobooks by a specific author? Go for it!

Smart Search: The search bar doesn't just look at the title; it searches both Title and Author/Creator fields, using the SQL LIKE operator to catch partial matches.

Easy Filters: Simple dropdown menus let you narrow your view by Item Type or Status in a click.

💻 The Files

The entire project is tidy and lives within just three files.

library_manager_app.py

This is the central brain of the entire application. It’s a single Python file that handles everything:

Database Setup: It takes care of connecting to SQLite, initializing the users and items tables when needed, and ensuring connections are safely closed after each request.

User Login/Out: All the logic for registration, logging in (checking that password hash!), and logging out is right here, tied into Flask's session management using the app.secret_key.

Routing: Every URL in the app, from the homepage to the edit pages, is defined by a route function in this file.

HTML Embedding: Because I needed the whole thing to work as one self-contained unit, the HTML, the responsive Tailwind CSS, and any small bits of JavaScript are all contained directly within multi-line Python strings and dynamically generated.Crucially, this application uses no separate .html template files. All front-end content HTML, responsive CSS, and JavaScript is defined directly within multi-line Python strings in helper functions and returned by the route handlers.

library.db

This is the database file created by the Python script. It's the simple SQLite file that holds all your permanent data—the user accounts and your library items.

💡 Design Choices: Why I Built It This Way

When designing this app, I had to make some conscious choices about security and performance.

The Database is prominent.
Question:Should I rely only on my Python code to check if a user is allowed to see an item, or should the database itself enforce it?

Choice : Database Enforcement was my choice.

My Rationale: Putting the security check right into the SQL query ,"WHERE user_id = ?", is the safest bet. Even if there's a bug in the application logic, the database simply won't return items belonging to anyone else. It's a structural guarantee of privacy.

Making Queries Flexible (But Safe!)
The Challenge: Combining a search term, a status filter, and a type filter into one robust query is tricky. Doing it wrong leads to SQL Injection vulnerabilities.

The Choice: Dynamic Query Construction with Placeholders.

My Rationale: I had to build the SQL query string piece by piece depending on which filters the user selected. To keep it secure, I strictly used SQL placeholders (?) for every user-provided value (like the search term). This prevents users from sneaking malicious code into the query while still allowing for super flexible filtering.

Making It Look Good
The Constraint: I couldn't use separate .css files.

The Choice: using CSS via a CDN.

My Rationale: I needed the UI to be responsive, modern, and professional. By loading the Tailwind library straight from a content delivery network, I could use its utility classes (like flex, p-4, and rounded-lg) directly within my embedded HTML strings. This allowed me to create a great-looking, mobile-friendly interface while sticking to the core project constraint of keeping the app in a single file.

I'm really happy with how this challenging project turned out.It's a great example of connecting all the pieces of a web application together, from secure login to dynamic data presentation.

💻 Requirements

To run this application, you need:

Python 3

Flask (for the web server)

SQLite 3 (for the database)
