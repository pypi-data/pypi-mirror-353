# gnudu_file.py
# Copyright 2015 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Import PGN file with gnu.database_du to database."""


if __name__ == "__main__":
    from .file_widget import FileWidget
    from ..gnu.database_du import Database

    FileWidget(Database, "dbm.gnu")
