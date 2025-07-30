# create_chesstab_database.py
# Copyright 2020 Roger Marsh
# Licence: See LICENSE.txt (BSD licence)

"""Create ChessTab database with chosen database engine and segment size."""

from solentware_base.tools import create_database

try:
    from ..unqlite import database as chessunqlite
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessunqlite = None
try:
    from ..vedis import database as chessvedis
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessvedis = None
if create_database._deny_sqlite3:
    chesssqlite3 = None
else:
    try:
        from ..sqlite import database as chesssqlite3
    except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
        chesssqlite3 = None
try:
    from ..apsw import database as chessapsw
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessapsw = None
try:
    from ..berkeleydb import database as chessberkeleydb
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessberkeleydb = None
try:
    from ..db import database as chessdb
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessdb = None
try:
    from ..db_tkinter import database as chessdbtkinter
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessdbtkinter = None
try:
    from ..dpt import database as chessdpt
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessdpt = None
try:
    from ..lmdb import database as chesslmdb
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chesslmdb = None
try:
    from ..ndbm import database as chessndbm
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessndbm = None
try:
    from ..gnu import database as chessgnu
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    chessgnu = None


class CreateChessTabDatabase(create_database.CreateDatabase):
    """Create a ChessTab database."""

    _START_TEXT = "".join(
        (
            "ChessTab would create a new database with the top-left engine, ",
            "and segment size 4000.",
        )
    )

    def __init__(self):
        """Build the user interface."""
        engines = {}
        if chessunqlite:
            engines[
                chessunqlite.unqlite_database.unqlite
            ] = chessunqlite.Database
        if chessvedis:
            engines[chessvedis.vedis_database.vedis] = chessvedis.Database
        if chesssqlite3:
            engines[
                chesssqlite3.sqlite3_database.sqlite3
            ] = chesssqlite3.Database
        if chessapsw:
            engines[chessapsw.apsw_database.apsw] = chessapsw.Database
        if chessdb:
            engines[chessdb.bsddb3_database.bsddb3] = chessdb.Database
        if chesslmdb:
            engines[chesslmdb.lmdb_database.lmdb] = chesslmdb.Database
        if chessberkeleydb:
            engines[
                chessberkeleydb.berkeleydb_database.berkeleydb
            ] = chessberkeleydb.Database
        if chessdbtkinter:
            engines[
                chessdbtkinter.db_tkinter_database.db_tcl
            ] = chessdbtkinter.Database
        if chessdpt:
            engines[
                chessdpt.dptnofistat.dpt_database._dpt.dptapi
            ] = chessdpt.Database
        if chessndbm:
            engines[
                chessndbm.ndbm_database.ndbm_module.dbm.ndbm
            ] = chessndbm.Database
        if chessgnu:
            engines[
                chessgnu.gnu_database.gnu_module.dbm.gnu
            ] = chessgnu.Database
        super().__init__(title="Create ChessTab Database", engines=engines)


if __name__ == "__main__":
    CreateChessTabDatabase().root.mainloop()
