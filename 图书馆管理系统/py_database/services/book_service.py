from models.book import Book

def add_book(title, author, isbn):
    Book.add_book(title, author, isbn)