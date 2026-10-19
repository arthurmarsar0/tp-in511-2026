"""
Demo database hydration.
"""

import sqlite3
from pathlib import Path

DB_PATH = "library.db"


def init_demo_db(path: str = DB_PATH):
    """Create a demo database with library data (authors, publishers, books)."""
    Path(path).unlink(missing_ok=True)

    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE authors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            birth_year INTEGER,
            nationality TEXT
        );

        CREATE TABLE publishers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            founded_year INTEGER,
            country TEXT
        );

        CREATE TABLE books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author_id INTEGER,
            publisher_id INTEGER,
            year INTEGER,
            genre TEXT,
            pages INTEGER,
            rating REAL,
            FOREIGN KEY (author_id) REFERENCES authors(id),
            FOREIGN KEY (publisher_id) REFERENCES publishers(id)
        );

        INSERT INTO authors (name, birth_year, nationality) VALUES
            ('Isaac Asimov', 1920, 'American'),
            ('Ursula K. Le Guin', 1929, 'American'),
            ('Frank Herbert', 1920, 'American'),
            ('Octavia Butler', 1947, 'American'),
            ('J.R.R. Tolkien', 1892, 'British'),
            ('George Orwell', 1903, 'British'),
            ('Aldous Huxley', 1894, 'British'),
            ('Ray Bradbury', 1920, 'American'),
            ('Philip K. Dick', 1928, 'American'),
            ('William Gibson', 1948, 'American'),
            ('Neal Stephenson', 1959, 'American'),
            ('Liu Cixin', 1963, 'Chinese');

        INSERT INTO publishers (name, founded_year, country) VALUES
            ('Ace Books', 1952, 'USA'),
            ('Gollancz', 1935, 'UK'),
            ('Penguin Books', 1935, 'UK'),
            ('HarperCollins', 1989, 'USA'),
            ('Tor Books', 1976, 'USA'),
            ('Vintage Books', 1954, 'USA'),
            ('Chilton Books', 1914, 'USA');

        INSERT INTO books (title, author_id, publisher_id, year, genre, pages, rating) VALUES
            ('Foundation', 1, 1, 1951, 'Science Fiction', 255, 4.3),
            ('I, Robot', 1, 2, 1950, 'Science Fiction', 224, 4.2),
            ('The Caves of Steel', 1, 3, 1954, 'Science Fiction', 206, 4.0),
            ('The Left Hand of Darkness', 2, 2, 1969, 'Science Fiction', 304, 4.3),
            ('The Dispossessed', 2, 4, 1974, 'Science Fiction', 387, 4.2),
            ('A Wizard of Earthsea', 2, 5, 1968, 'Fantasy', 205, 4.1),
            ('Dune', 3, 1, 1965, 'Science Fiction', 412, 4.5),
            ('Dune Messiah', 3, 1, 1969, 'Science Fiction', 331, 4.0),
            ('Children of Dune', 3, 1, 1976, 'Science Fiction', 408, 4.1),
            ('Kindred', 4, 2, 1979, 'Science Fiction', 264, 4.3),
            ('Parable of the Sower', 4, 2, 1993, 'Dystopian', 318, 4.4),
            ('The Fellowship of the Ring', 5, 2, 1954, 'Fantasy', 423, 4.5),
            ('The Two Towers', 5, 2, 1954, 'Fantasy', 352, 4.4),
            ('The Return of the King', 5, 2, 1955, 'Fantasy', 416, 4.5),
            ('1984', 6, 3, 1949, 'Dystopian', 328, 4.5),
            ('Animal Farm', 6, 3, 1945, 'Satire', 112, 4.3),
            ('Brave New World', 7, 3, 1932, 'Dystopian', 288, 4.2),
            ('Fahrenheit 451', 8, 4, 1953, 'Dystopian', 194, 4.3),
            ('The Martian Chronicles', 8, 4, 1950, 'Science Fiction', 222, 4.2),
            ('Do Androids Dream of Electric Sheep?', 9, 4, 1968, 'Science Fiction', 210, 4.3),
            ('Ubik', 9, 1, 1969, 'Science Fiction', 215, 4.2),
            ('Neuromancer', 10, 2, 1984, 'Cyberpunk', 271, 4.3),
            ('Snow Crash', 11, 4, 1992, 'Cyberpunk', 470, 4.1),
            ('The Three-Body Problem', 12, 5, 2008, 'Science Fiction', 302, 4.2);
    """)
    conn.commit()
    conn.close()
    print(f"Demo database created: {path} (12 authors, 7 publishers, 24 books)")
