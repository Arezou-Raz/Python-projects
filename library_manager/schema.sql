-- Delete existing tables to ensure a clean start
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS items;

-- Create the users table for authentication
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL
);

-- Create the items table to store the library catalog (Books and Audiobooks)
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    item_type TEXT NOT NULL, -- Stores 'Book' or 'Audiobook'
    status TEXT NOT NULL,    -- Stores 'Owned', 'Wishlist', or 'Loaned Out'
    FOREIGN KEY (user_id) REFERENCES users (id)
);
