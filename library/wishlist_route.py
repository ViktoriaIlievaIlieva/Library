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
        with get_connection() as connection:
            connection.execute("""
            INSERT INTO "Wishlists"(Name, Author)
            VALUES (?,?)
            """, book, author)

    return redirect("/wishlist")


@blueprint_wishlist.route("/wishlist")
def wishlist():
    with get_connection() as connection:
        wishlist_cursor: CursorResult = connection.execute("""
        SELECT * 
        FROM Wishlists
        """)
        all_wished_books: list[dict] = wishlist_cursor.mappings().all()

    return render_template("wishlist/wishlist.html", list_with_dict_book_info=all_wished_books)


@blueprint_wishlist.route("/delete_wishlist_book")
def delete_wishlist_book():
    id = request.args["id"]
    with get_connection() as connection:
        connection.execute("""
        DELETE FROM Wishlists
        WHERE ID=?
        """, id)

    return redirect("/wishlist")
