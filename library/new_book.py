from flask import request
from library.database import get_connection




def new_book():
    bg_title: str = request.form["bg_title"]
    eng_title: str = request.form["eng_title"]
    format: str = request.form["format"]
    location: str = request.form["location"]
    author_of_list: str = request.form["author_of_list"]
    new_author: str = request.form["new_author"]
    related_series_list: str = request.form["related_series"]
    new_series_name: str = request.form["name_new_related_series"]
    new_series_description: str = request.form["description_new_related_series"]
    type_series: str = request.form["series_type"]
    info: str = request.form["info"]

    if author_of_list == "":
        with get_connection() as connection:
            author_id = connection.execute("""
            INSERT INTO "Authors"("Name")
            VALUES (?)
            """, new_author).lastrowid
    else:
        author_id = author_of_list

    if related_series_list == "single_book":
        related_series_id = None
    elif related_series_list == "":
        with get_connection() as connection:
            related_series_id = connection.execute("""
            INSERT INTO "Related"("Name", "RelationTypeID", "Description")
            VALUES (?, ?, ?)
            """, new_series_name, type_series, new_series_description).lastrowid
    else:
        related_series_id = related_series_list

    if "read_status" in request.form:
        read_status = 1
    else:
        read_status = 0

    with get_connection() as connection:
        new_book_id = connection.execute("""
            INSERT INTO Books (NameBG, NameENG, AuthorID, FormatID, RelatedID, LocationID, Read, Info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, bg_title, eng_title, author_id, format, related_series_id, location, read_status, info).lastrowid

    return new_book_id
