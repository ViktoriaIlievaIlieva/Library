from flask import Blueprint, render_template, request, redirect
from library.database import get_connection
from sqlalchemy.engine import CursorResult

blueprint_wishlist = Blueprint("Wishlist", __name__)


@blueprint_wishlist.route("/wishlist-add", methods=["GET", "POST"])
def wishlist_add():
    if request.method == "GET":
        return render_template("wishlist/new_book_for_wishlist.html")
    else:
        book = request.form["book"]
        author = request.form["author"]
        connection = get_connection()
        connection.execute("""
        INSERT INTO "Wishlists"(Name, Author)
        VALUES (?,?)
        """, book, author)

    connection.close()

    return redirect("/wishlist")

@blueprint_wishlist.route("/wishlist")
def wishlist():
    connection = get_connection()

    cursor_to_result: CursorResult = connection.execute("""
    SELECT * 
    FROM Wishlists
    """)
    all_wished_books: list[tuple] = cursor_to_result.fetchall()
    connection.close()

    list_with_dict_for_books_and_authors: list = []

    for book_info in all_wished_books:
        book = book_info[1]
        author = book_info[2]
        book_info: dict = {"book_title": book, "book_author": author}
        list_with_dict_for_books_and_authors.append(book_info)

    return render_template("wishlist/wishlist.html", list_with_dict_book_info=list_with_dict_for_books_and_authors)
