# chess.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Define top level user interface to a ChessTab database.

Provide menu options to import chess games and related data.

Provide menu options to export chess games and related data.

Provide menu options to access the information in a ChessTab database.

Provide menu options to manipulate the information shown from a ChessTab
database.

The database engine used by a run of ChessTab is chosen when a database is
first opened or created.

An existing database can be opened only if the database engine with which it
was created is available.

A new database is created using the first database engine interface available
from the list in order:

dptdb    DPT (an emulation of Model 204 on MS Windows) via SWIG interface
bsddb3   Berkeley DB
apsw     Sqlite3
sqlite3  Sqlite3

"""

import os
import tkinter
import tkinter.ttk
import tkinter.messagebox
import tkinter.filedialog
import gc
import queue
import multiprocessing

from solentware_base import modulequery
from solentware_base.core.filespec import FileSpecError

from solentware_grid.core.dataclient import DataSource

from solentware_misc.core import callthreadqueue

from solentware_bind.gui.bindings import Bindings
from solentware_bind.gui.exceptionhandler import ExceptionHandler

from pgn_read.core.parser import PGN

from ..core import export_game
from ..core import export_repertoire
from ..core import export_chessql
from .. import (
    APPLICATION_DATABASE_MODULE,
    APPLICATION_NAME,
    PARTIAL_POSITION_MODULE,
    FULL_POSITION_MODULE,
    ANALYSIS_MODULE,
    SELECTION_MODULE,
    ERROR_LOG,
)
from ..core.filespec import (
    FileSpec,
    GAMES_FILE_DEF,
    PGN_ERROR_FIELD_DEF,
    EVENT_FIELD_DEF,
    SITE_FIELD_DEF,
    DATE_FIELD_DEF,
    ROUND_FIELD_DEF,
    WHITE_FIELD_DEF,
    BLACK_FIELD_DEF,
    RESULT_FIELD_DEF,
)
from ..core.constants import UNKNOWN_RESULT
from ..shared import rundu
from .gamedisplay import GameDisplayInsert
from .cqldisplay import CQLDisplayInsert
from .repertoiredisplay import RepertoireDisplayInsert
from . import constants
from .gamerow import chess_db_row_game
from .querydisplay import QueryDisplayInsert
from . import options
from . import colourscheme
from . import help_
from .uci import UCI
from .chess_ui import ChessUI
from .eventspec import EventSpec

STARTUP_MINIMUM_WIDTH = 340
STARTUP_MINIMUM_HEIGHT = 400

ExceptionHandler.set_application_name(APPLICATION_NAME)


class ChessError(Exception):
    """Exception class fo chess module."""


# Convert module constants _FullPositionDS and others to class attribute
# names because the default class-attribute-naming-style is 'any'.
class _Import:
    """Names of classes imported by import_module from alternative modules.

    For runtime "from <db|dpt>results import Database" and similar.
    """

    Database = "Database"
    FullPositionDS = "FullPositionDS"
    ChessQueryLanguageDS = "ChessQueryLanguageDS"
    AnalysisDS = "AnalysisDS"
    SelectionDS = "SelectionDS"


class Chess(Bindings):
    """Connect a chess database with User Interface."""

    _index = GAMES_FILE_DEF
    _open_msg = "Open a chess database with Database | Open"

    def __init__(self, dptmultistepdu=False, dptchunksize=None, **kargs):
        """Create the database and ChessUI objects.

        dptmultistepdu is True: use multi-step deferred update in dpt
        otherwise use single-step deferred update in dpt.
        dptchunksize is None: obey dptmultistepdu rules for deferred update.
        dptchunksize is integer >= 5000: divide pgn file into dptchunksize game
        chunks and do a single-step deferred update for each chunk.
        otherwise behave as if dptchunksize == 5000.
        This parameter is provided to cope with running deferred updates under
        versions of Wine which do not report memory usage correctly causing
        dpt single-step deferred update to fail after processing a few
        thousand games.

        **kargs - passed through to database object

        """
        super().__init__()
        self.root = tkinter.Tk()
        try:
            self.root.wm_title(APPLICATION_NAME)
            self.root.wm_minsize(
                width=STARTUP_MINIMUM_WIDTH, height=STARTUP_MINIMUM_HEIGHT
            )

            if dptchunksize is not None:
                if not isinstance(dptchunksize, int):
                    dptchunksize = 5000
                self._dptchunksize = max(dptchunksize, 5000)
                self._dptmultistepdu = False
            else:
                self._dptchunksize = dptchunksize
                self._dptmultistepdu = dptmultistepdu is True
            self._database_class = None
            self._chessdbkargs = kargs
            self.opendatabase = None
            self._database_enginename = None
            self._database_modulename = None
            self._partialposition_class = None
            self._fullposition_class = None
            self._engineanalysis_class = None
            self._selection_class = None
            self._pgnfiles = None
            self.queue = None
            self.reportqueue = queue.Queue(maxsize=1)

            # For tooltip binding, if it ever works.
            # See create_menu_changed_callback() method.
            menus = []

            menubar = tkinter.Menu(self.root)
            menus.append(menubar)

            menu1 = tkinter.Menu(menubar, name="database", tearoff=False)
            menus.append(menu1)
            menubar.add_cascade(label="Database", menu=menu1, underline=0)
            for accelerator, function in (
                (EventSpec.menu_database_open, self._database_open),
                (EventSpec.menu_database_new, self._database_new),
                (EventSpec.menu_database_close, self._database_close),
                (EventSpec.menu_database_delete, self._database_delete),
                (EventSpec.menu_database_quit, self._database_quit),
            ):
                menu1.add_command(
                    label=accelerator[1],
                    command=self.try_command(function, menu1),
                    underline=accelerator[3],
                )
            menu1.add_separator()
            menu101 = tkinter.Menu(menu1, name="export", tearoff=False)
            menu1.insert_cascade(
                3,
                label=EventSpec.menu_database_export[1],
                menu=menu101,
                underline=EventSpec.menu_database_export[3],
            )
            menu102 = tkinter.Menu(menu1, name="import", tearoff=False)
            menu1.insert_cascade(
                3,
                label=EventSpec.menu_database_import[1],
                menu=menu102,
                underline=EventSpec.menu_database_import[3],
            )
            for index in (6, 5, 3, 0):
                menu1.insert_separator(index)
            for accelerator, function in (
                (EventSpec.menu_database_games, self._database_import),
                (
                    EventSpec.menu_database_repertoires,
                    self._import_repertoires,
                ),
                (EventSpec.menu_database_positions, self._import_positions),
            ):
                menu102.add_command(
                    label=accelerator[1],
                    command=self.try_command(function, menu102),
                    underline=accelerator[3],
                )
            menu10101 = tkinter.Menu(menu101, name="games", tearoff=False)
            menu101.add_cascade(
                label=EventSpec.menu_database_games[1],
                menu=menu10101,
                underline=EventSpec.menu_database_games[3],
            )
            for accelerator, function in (
                (
                    EventSpec.pgn_reduced_export_format,
                    self.export_all_games_pgn_reduced_export_format,
                ),
                (
                    EventSpec.pgn_export_format_no_comments_no_ravs,
                    self.export_all_games_pgn_no_comments_no_ravs,
                ),
                (
                    EventSpec.pgn_export_format_no_comments,
                    self.export_all_games_pgn_no_comments,
                ),
                (EventSpec.pgn_export_format, self.export_all_games_pgn),
                (
                    EventSpec.pgn_import_format,
                    self.export_all_games_pgn_import_format,
                ),
                (EventSpec.text_internal_format, self.export_all_games_text),
            ):
                menu10101.add_command(
                    label=accelerator[1],
                    command=self.try_command(function, menu10101),
                    underline=accelerator[3],
                )
            menu10102 = tkinter.Menu(
                menu101, name="repertoires", tearoff=False
            )
            menu101.add_cascade(
                label=EventSpec.menu_database_repertoires[1],
                menu=menu10102,
                underline=EventSpec.menu_database_repertoires[3],
            )
            for accelerator, function in (
                (
                    EventSpec.pgn_export_format_no_comments,
                    self.export_all_repertoires_pgn_no_comments,
                ),
                (EventSpec.pgn_export_format, self.export_all_repertoires_pgn),
                (
                    EventSpec.pgn_import_format,
                    self.export_all_repertoires_pgn_import_format,
                ),
                (
                    EventSpec.text_internal_format,
                    self.export_all_repertoires_text,
                ),
            ):
                menu10102.add_command(
                    label=accelerator[1],
                    command=self.try_command(function, menu10102),
                    underline=accelerator[3],
                )
            for accelerator, function in (
                (EventSpec.menu_database_positions, self._export_positions),
                (
                    EventSpec.menu_database_export_all_text,
                    self.export_all_games_text,
                ),
            ):
                menu101.add_command(
                    label=accelerator[1],
                    command=self.try_command(function, menu101),
                    underline=accelerator[3],
                )

            menu2 = tkinter.Menu(menubar, name="select", tearoff=False)
            menus.append(menu2)
            menubar.add_cascade(label="Select", menu=menu2, underline=0)
            for accelerator, function in (
                (EventSpec.menu_select_rule, self._index_select),
                (EventSpec.menu_show, self._index_show),
                (EventSpec.menu_hide, self._index_hide),
                (
                    EventSpec.menu_select_game,
                    self._create_options_index_callback(GAMES_FILE_DEF),
                ),
                (
                    EventSpec.menu_select_error,
                    self._create_options_index_callback(PGN_ERROR_FIELD_DEF),
                ),
            ):
                menu2.add_command(
                    label=accelerator[1],
                    command=self.try_command(function, menu2),
                    underline=accelerator[3],
                )
            menu2.add_separator()
            menu201 = tkinter.Menu(menu2, name="index", tearoff=False)
            menus.append(menu201)
            menu2.insert_cascade(
                4,
                label=EventSpec.menu_select_index[1],
                menu=menu201,
                underline=EventSpec.menu_select_index[3],
            )
            for index in (5, 4, 3, 1, 0):
                menu2.insert_separator(index)
            for accelerator, field in (
                (EventSpec.menu_select_index_black, BLACK_FIELD_DEF),
                (EventSpec.menu_select_index_white, WHITE_FIELD_DEF),
                (EventSpec.menu_select_index_event, EVENT_FIELD_DEF),
                (EventSpec.menu_select_index_date, DATE_FIELD_DEF),
                (EventSpec.menu_select_index_result, RESULT_FIELD_DEF),
                (EventSpec.menu_select_index_site, SITE_FIELD_DEF),
                (EventSpec.menu_select_index_round, ROUND_FIELD_DEF),
            ):
                menu201.add_command(
                    label=accelerator[1],
                    command=self.try_command(
                        self._create_options_index_callback(field), menu201
                    ),
                    underline=accelerator[3],
                )

            menu3 = tkinter.Menu(menubar, name="game", tearoff=False)
            menus.append(menu3)
            menubar.add_cascade(label="Game", menu=menu3, underline=0)
            menu3.add_separator()
            for accelerator, function in (
                (EventSpec.menu_game_new_game, self._game_new_game),
            ):
                menu3.add_command(
                    label=accelerator[1],
                    command=self.try_command(function, menu3),
                    underline=accelerator[3],
                )
            menu3.add_separator()

            menu4 = tkinter.Menu(menubar, name="position", tearoff=False)
            menus.append(menu4)
            menubar.add_cascade(label="Position", menu=menu4, underline=0)
            for accelerator, function in (
                (EventSpec.menu_position_partial, self._position_partial),
                (EventSpec.menu_show, self._position_show),
                (EventSpec.menu_hide, self._position_hide),
            ):
                menu4.add_command(
                    label=accelerator[1],
                    command=self.try_command(function, menu4),
                    underline=accelerator[3],
                )
            menu4.add_separator()
            for index in (1, 0):
                menu4.insert_separator(index)

            menu5 = tkinter.Menu(menubar, name="repertoire", tearoff=False)
            menus.append(menu5)
            menubar.add_cascade(label="Repertoire", menu=menu5, underline=0)
            for accelerator, function in (
                (EventSpec.menu_repertoire_opening, self._repertoire_game),
                (EventSpec.menu_show, self._repertoire_show),
                (EventSpec.menu_hide, self._repertoire_hide),
            ):
                menu5.add_command(
                    label=accelerator[1],
                    command=self.try_command(function, menu5),
                    underline=accelerator[3],
                )
            menu5.add_separator()
            for index in (1, 0):
                menu5.insert_separator(index)

            menu6 = tkinter.Menu(menubar, name="tools", tearoff=False)
            menus.append(menu6)
            menubar.add_cascade(label="Tools", menu=menu6, underline=0)
            for accelerator, function in (
                (EventSpec.menu_tools_board_style, self._select_board_style),
                (EventSpec.menu_tools_board_fonts, self._select_board_fonts),
                (
                    EventSpec.menu_tools_board_colours,
                    self._select_board_colours,
                ),
                (
                    EventSpec.menu_tools_hide_game_analysis,
                    self._hide_game_analysis,
                ),
                (
                    EventSpec.menu_tools_show_game_analysis,
                    self._show_game_analysis,
                ),
                (
                    EventSpec.menu_tools_hide_game_scrollbars,
                    self._hide_scrollbars,
                ),
                (
                    EventSpec.menu_tools_show_game_scrollbars,
                    self._show_scrollbars,
                ),
                (
                    EventSpec.menu_tools_toggle_game_move_numbers,
                    self._toggle_game_move_numbers,
                ),
                (
                    EventSpec.menu_tools_toggle__analysis_fen,
                    self._toggle_analysis_fen,
                ),
                (
                    EventSpec.menu_tools_toggle_single_view,
                    self._toggle_single_view,
                ),
            ):
                menu6.add_command(
                    label=accelerator[1],
                    command=self.try_command(function, menu6),
                    underline=accelerator[3],
                )
            menu6.add_separator()
            for index in (9, 8, 7, 5, 3, 0):
                menu6.insert_separator(index)

            menu7 = tkinter.Menu(menubar, name="engines", tearoff=False)
            menus.append(menu7)
            menubar.add_cascade(label="Engines", menu=menu7, underline=0)

            menu8 = tkinter.Menu(menubar, name="commands", tearoff=False)
            menus.append(menu7)
            menubar.add_cascade(label="Commands", menu=menu8, underline=0)

            menuhelp = tkinter.Menu(menubar, name="help", tearoff=False)
            menus.append(menuhelp)
            menubar.add_cascade(label="Help", menu=menuhelp, underline=0)
            menuhelp.add_separator()
            for accelerator, function in (
                (EventSpec.menu_help_guide, self._help_guide),
                (EventSpec.menu_help_selection_rules, self._help_selection),
                (EventSpec.menu_help_file_size, self._help_file_size),
                (EventSpec.menu_help_notes, self._help_notes),
                (EventSpec.menu_help_about, self._help_about),
            ):
                menuhelp.add_command(
                    label=accelerator[1],
                    command=self.try_command(function, menuhelp),
                    underline=accelerator[3],
                )
            menuhelp.add_separator()

            self.root.configure(menu=menubar)

            for menu in menus:
                self.bind(
                    menu,
                    "<<MenuSelect>>",
                    function=self.try_event(
                        self.create_menu_changed_callback(menu)
                    ),
                )

            toolbarframe = tkinter.ttk.Frame(master=self.root)
            toolbarframe.pack(side=tkinter.TOP, fill=tkinter.X)
            self.statusbar = Statusbar(
                toolbarframe, self.root.cget("background")
            )
            toppane = tkinter.ttk.PanedWindow(
                self.root,
                # background='cyan2',
                # opaqueresize=tkinter.FALSE,
                width=STARTUP_MINIMUM_WIDTH * 2,
                orient=tkinter.HORIZONTAL,
            )
            toppane.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)

            self.ui = ChessUI(
                toppane,
                statusbar=self.statusbar,
                uci=UCI(menu7, menu8),
                toolbarframe=toolbarframe,
            )
            self.queue = callthreadqueue.CallThreadQueue()

            # See comment near end of class definition DeferredUpdate in
            # sibling module chessdu for explanation of this change.
            self.__run_ui_task_from_queue(5000)

        except Exception as exc:
            self.root.destroy()
            del self.root
            # pylint message broad-except.
            # Can keep going for some exceptions.
            raise ChessError(
                " initialize ".join(("Unable to ", APPLICATION_NAME))
            ) from exc

    def __del__(self):
        """Ensure database Close method is called on destruction."""
        if self.opendatabase:
            self.opendatabase.close_database()
            self.opendatabase = None
        super().__del__()

    # The methods which do actions on an open database.

    def _database_quit(self):
        """Quit chess database."""
        if self._is_import_subprocess_active():
            quitmsg = "".join(
                (
                    "An import of PGN data is in progress.\n\n",
                    "The import will continue if you confirm quit but you ",
                    "will not be informed when the import finishes nor if ",
                    "it succeeded.  Try opening it later or examine the ",
                    "error log to find out.\n\n",
                    "You will not be able to open this database again until ",
                    "the import has finished.",
                )
            )
        else:
            quitmsg = "Confirm Quit"
        dlg = tkinter.messagebox.askquestion(
            parent=self._get_toplevel(), title="Quit", message=quitmsg
        )
        if dlg == tkinter.messagebox.YES:
            if self.ui.uci:
                self.ui.uci.remove_engines_and_menu_entries()
            if self.opendatabase:
                self._close_recordsets()
                self.opendatabase.close_database()
                self.opendatabase = None
                self._set_error_file_name(directory=None)
            self.root.destroy()

    def _is_import_subprocess_active(self):
        """Return the exception report file object."""
        return self.ui.is_import_subprocess_active()

    def _get_toplevel(self):
        """Return the toplevel widget."""
        return self.root

    @staticmethod
    def _set_error_file_name(directory=None):
        """Set the exception report file name to filename."""
        if directory is None:
            Chess.set_error_file_name(None)
        else:
            Chess.set_error_file_name(os.path.join(directory, ERROR_LOG))

    def _game_new_game(self):
        """Enter a new game (callback for Menu option)."""
        self._new_game()

    def _new_game(self):
        """Enter a new game."""
        game = GameDisplayInsert(
            master=self.ui.view_games_pw,
            ui=self.ui,
            items_manager=self.ui.game_items,
            itemgrid=self.ui.game_games,
        )
        game.set_position_analysis_data_source()
        game.collected_game = next(
            PGN(game_class=game.gameclass).read_games(
                "".join(
                    (
                        constants.EMPTY_SEVEN_TAG_ROSTER,
                        UNKNOWN_RESULT,
                    )
                )
            )
        )
        game.set_and_tag_item_text()
        self.ui.add_game_to_display(game)
        try:
            # Is new window only one available for user interaction?
            if self.root.focus_displayof() != self.root:
                return
        except KeyError:
            # Launch; Database Open; Database Close; Game New
            pass

        # Wrap to take account of self.ui.single_view
        self.ui.game_items.active_item.takefocus_widget.focus_set()

    def _position_partial(self):
        """Enter a new partial position (callback for Menu option)."""
        self._new_partial_position()

    def _new_partial_position(self):
        """Enter a new partial position."""
        position = CQLDisplayInsert(
            master=self.ui.view_partials_pw,
            ui=self.ui,
            items_manager=self.ui.partial_items,
            itemgrid=self.ui.partial_games,
        )
        position.cql_statement.process_statement("")
        position.set_and_tag_item_text(reset_undo=True)
        self.ui.add_partial_position_to_display(position)
        try:
            # Is new window only one available for user interaction?
            if self.root.focus_displayof() != self.root:
                return
        except KeyError:
            # Launch; Database Open; Database Close; Position Partial
            pass

        # Wrap to take account of self.ui.single_view
        self.ui.partial_items.active_item.takefocus_widget.focus_set()

    def _repertoire_game(self):
        """Enter a new opening variation (callback for Menu option)."""
        self._new_repertoire_game()

    def _new_repertoire_game(self):
        """Enter a new repertoire game (opening variation)."""
        game = RepertoireDisplayInsert(
            master=self.ui.view_repertoires_pw,
            ui=self.ui,
            items_manager=self.ui.repertoire_items,
            itemgrid=self.ui.repertoire_games,
        )
        game.set_position_analysis_data_source()
        game.collected_game = next(
            PGN(game_class=game.gameclass).read_games(
                "".join((constants.EMPTY_REPERTOIRE_GAME, UNKNOWN_RESULT))
            )
        )
        game.set_and_tag_item_text(reset_undo=True)
        self.ui.add_repertoire_to_display(game)
        try:
            # Is new window only one available for user interaction?
            if self.root.focus_displayof() != self.root:
                return
        except KeyError:
            # Launch; Database Open; Database Close; Game New
            pass

        # Wrap to take account of self.ui.single_view
        self.ui.repertoire_items.active_item.takefocus_widget.focus_set()

    def _select_board_style(self):
        """Choose and set colour scheme and font forchessboard."""
        decor = colourscheme.FontColourChooser(ui=self.ui)
        if decor.is_ok():
            if self.opendatabase:
                options.save_options(
                    self.opendatabase.home_directory, decor.get_options()
                )
            decor.apply_to_named_fonts()
            self.ui.set_board_fonts(decor)
            self.ui.set_board_colours(decor)

    def _select_board_fonts(self):
        """Choose and set font for board."""
        decor = colourscheme.FontChooser(ui=self.ui)
        if decor.is_ok():
            if self.opendatabase:
                options.save_options(
                    self.opendatabase.home_directory, decor.get_options()
                )
            decor.apply_to_named_fonts()
            self.ui.set_board_fonts(decor)

    def _select_board_colours(self):
        """Choose and set colour scheme for board."""
        decor = colourscheme.ColourChooser(ui=self.ui)
        if decor.is_ok():
            if self.opendatabase:
                options.save_options(
                    self.opendatabase.home_directory, decor.get_options()
                )
            self.ui.set_board_colours(decor)

    def _hide_game_analysis(self):
        """Hide the widgets which show analysis from chess engines."""
        self.ui.show_analysis = False
        exceptions = []
        for games in (
            self.ui.game_items.order,
            self.ui.repertoire_items.order,
            self.ui.games_and_repertoires_in_toplevels,
        ):
            for game in games:
                try:
                    game.hide_game_analysis()
                except tkinter.TclError:
                    exceptions.append((game, games))
        for game, games in exceptions:
            games.remove(game)

    def _show_game_analysis(self):
        """Show the widgets which show analysis from chess engines."""
        self.ui.show_analysis = True
        exceptions = []
        for games in (
            self.ui.game_items.order,
            self.ui.repertoire_items.order,
            self.ui.games_and_repertoires_in_toplevels,
        ):
            for game in games:
                try:
                    game.show_game_analysis()
                except tkinter.TclError:
                    exceptions.append((game, games))
        for game, games in exceptions:
            games.remove(game)

    def _hide_scrollbars(self):
        """Hide the scrollbars in the game display widgets."""
        self.ui.hide_scrollbars()
        self.ui.uci.hide_scrollbars()

    def _show_scrollbars(self):
        """Show the scrollbars in the game display widgets."""
        self.ui.show_scrollbars()
        self.ui.uci.show_scrollbars()

    def _toggle_game_move_numbers(self):
        """Toggle display of move numbers in game score widgets."""
        exceptions = []
        for games in (
            self.ui.game_items.order,
            self.ui.repertoire_items.order,
            self.ui.games_and_repertoires_in_toplevels,
        ):
            for game in games:
                try:
                    game.toggle_game_move_numbers()
                except tkinter.TclError:
                    exceptions.append((game, games))
        for game, games in exceptions:
            games.remove(game)

    def _toggle_analysis_fen(self):
        """Toggle display of PGN tags in analysis widgets."""
        exceptions = []
        for games in (
            self.ui.game_items.order,
            self.ui.repertoire_items.order,
            self.ui.games_and_repertoires_in_toplevels,
        ):
            for game in games:
                try:
                    game.toggle_analysis_fen()
                except tkinter.TclError:
                    exceptions.append((game, games))
        for game, games in exceptions:
            games.remove(game)

    def _toggle_single_view(self):
        """Toggle display single pane or all panes with non-zero weight."""
        if self.ui.single_view:
            self.ui.show_all_panedwindows()
        else:
            self.ui.show_just_panedwindow_with_focus(
                self.ui.top_pw.focus_displayof()
            )

    def _help_guide(self):
        """Display brief User Guide for Chess application."""
        help_.help_guide(self.root)

    def _help_selection(self):
        """Display description of selection rules for Chess application."""
        help_.help_selection(self.root)

    def _help_file_size(self):
        """Display brief instructions for file size dialogue."""
        help_.help_file_size(self.root)

    def _help_notes(self):
        """Display technical notes about Chess application."""
        help_.help_notes(self.root)

    def _help_about(self):
        """Display information about Chess application."""
        help_.help_about(self.root)

    @staticmethod
    def create_menu_changed_callback(menu):
        """Return callback to bind to <<MenuSelect>> event for menu."""
        del menu

        def menu_changed(event):
            """Display menu tip in status bar."""
            # entrycget('active', <property>) always returns None
            # <index> and 'end' forms work though
            # even tried repeating in an 'after_idle' call
            # similar on FreeBSD and W2000
            # PERL has same problem as found when looked at www
            # print 'menu changed', menu.entrycget('active', 'label')
            # print menu, event, 'changed', menu.entrycget('active', 'label')
            del event

        return menu_changed

    # See comment near end of class definition DeferredUpdate in sibling
    # module chessdu for explanation of this change: which is addition and use
    # of the __run_ui_task_from_queue and _try_command_after_idle methods.

    def __run_ui_task_from_queue(self, interval):
        """Do all queued tasks then wake-up after interval."""
        while True:
            try:
                method, args, kwargs = self.reportqueue.get_nowait()
                method(*args, **kwargs)
            except queue.Empty:
                self.root.after(
                    interval,
                    self.try_command(self.__run_ui_task_from_queue, self.root),
                    *(interval,),
                )
                break
            self.reportqueue.task_done()

    # The methods which open, close, and accesss data on, a database.

    def _database_open(self):
        """Open chess database."""
        if self.opendatabase is not None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                message="A chess database is already open",
                title="Open",
            )
            return

        chessfolder = tkinter.filedialog.askdirectory(
            parent=self._get_toplevel(),
            title="Select folder containing a chess database",
            initialdir="~",
            mustexist=tkinter.TRUE,
        )
        if not chessfolder:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                message="Open chess database cancelled",
                title="Open",
            )
            return

        # Set the error file in top folder of chess database
        self._set_error_file_name(directory=chessfolder)

        interface_modules = modulequery.modules_for_existing_databases(
            chessfolder, FileSpec()
        )
        # A database module is chosen when creating the database
        # so there should be either only one entry in edt or None
        if not interface_modules:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                message="".join(
                    (
                        "Chess database in ",
                        os.path.basename(chessfolder),
                        " cannot be opened, or there isn't one.\n\n",
                        "(Is correct database engine available?)",
                    )
                ),
                title="Open",
            )
            return
        if len(interface_modules) > 1:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                message="".join(
                    (
                        "There is more than one chess database in folder\n\n",
                        os.path.basename(chessfolder),
                        "\n\nMove the databases to separate folders and try ",
                        "again.  (Use the platform tools for moving files to ",
                        "relocate the database files.)",
                    )
                ),
                title="Open",
            )
            return

        idm = modulequery.installed_database_modules()
        _enginename = None
        for key, value in idm.items():
            if value in interface_modules[0]:
                if _enginename:
                    tkinter.messagebox.showinfo(
                        parent=self._get_toplevel(),
                        message="".join(
                            (
                                "Several modules able to open database in\n\n",
                                os.path.basename(chessfolder),
                                "\n\navailable.  Unable to choose.",
                            )
                        ),
                        title="Open",
                    )
                    return
                _enginename = key
        if _enginename is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                message="".join(
                    (
                        "No modules able to open database in\n\n",
                        os.path.basename(chessfolder),
                        "\n\navailable.",
                    )
                ),
                title="Open",
            )
            return
        _modulename = APPLICATION_DATABASE_MODULE[_enginename]
        if self._database_modulename != _modulename:
            if self._database_modulename is not None:
                tkinter.messagebox.showinfo(
                    parent=self._get_toplevel(),
                    message="".join(
                        (
                            "The database engine needed for this database ",
                            "is not the one already in use.\n\nYou will ",
                            "have to Quit and start the application again ",
                            "to open this database.",
                        )
                    ),
                    title="Open",
                )
                return
            self._database_enginename = _enginename
            self._database_modulename = _modulename

            def import_name(modulename, name):
                try:
                    module = __import__(
                        modulename, globals(), locals(), [name]
                    )
                except ImportError:
                    return None
                return getattr(module, name)

            self._database_class = import_name(_modulename, _Import.Database)
            self._fullposition_class = import_name(
                FULL_POSITION_MODULE[_enginename], _Import.FullPositionDS
            )
            self._partialposition_class = import_name(
                PARTIAL_POSITION_MODULE[_enginename],
                _Import.ChessQueryLanguageDS,
            )
            self._engineanalysis_class = import_name(
                ANALYSIS_MODULE[_enginename], _Import.AnalysisDS
            )
            self._selection_class = import_name(
                SELECTION_MODULE[_enginename], _Import.SelectionDS
            )

        try:
            self._open_database_directory(chessfolder)
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                message="".join(
                    (
                        "Unable to open database\n\n",
                        str(chessfolder),
                        "\n\nThe reported reason is:\n\n",
                        str(exc),
                    )
                ),
                title="Open",
            )
            self._close_database_and_hide_widgets()
            self.opendatabase = None
            if isinstance(exc, FileSpecError):
                return
            # pylint message broad-except.
            raise ChessError(
                " database in ".join(("Unable to open", APPLICATION_NAME))
            ) from exc

    def _database_new(self):
        """Create and open a new chess database."""
        if self.opendatabase is not None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                message="A chess database is already open",
                title="New",
            )
            return

        chessfolder = tkinter.filedialog.askdirectory(
            parent=self._get_toplevel(),
            title="Select folder for new chess database",
            initialdir="~",
        )
        if not chessfolder:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                message="Create new chess database cancelled",
                title="New",
            )
            return

        if os.path.exists(chessfolder):
            if modulequery.modules_for_existing_databases(
                chessfolder, FileSpec()
            ):
                tkinter.messagebox.showinfo(
                    parent=self._get_toplevel(),
                    message="".join(
                        (
                            "A chess database already exists in ",
                            os.path.basename(chessfolder),
                        )
                    ),
                    title="New",
                )
                return
        else:
            try:
                os.makedirs(chessfolder)
            except OSError:
                tkinter.messagebox.showinfo(
                    parent=self._get_toplevel(),
                    message="".join(
                        (
                            "Folder ",
                            os.path.basename(chessfolder),
                            " already exists",
                        )
                    ),
                    title="New",
                )
                return

        # Set the error file in top folder of chess database
        self._set_error_file_name(directory=chessfolder)

        # the default preference order is used rather than ask the user or
        # an order specific to this application.  An earlier version of this
        # module implements a dialogue to pick a database engine if there is
        # a choice.
        idm = modulequery.installed_database_modules()
        if len(idm) == 0:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                message="".join(
                    (
                        "No modules able to create database in\n\n",
                        os.path.basename(chessfolder),
                        "\n\navailable.",
                    )
                ),
                title="New",
            )
            return
        _modulename = None
        _enginename = None
        for ename in modulequery.DATABASE_MODULES_IN_DEFAULT_PREFERENCE_ORDER:
            if ename in idm:
                if ename in APPLICATION_DATABASE_MODULE:
                    _enginename = ename
                    _modulename = APPLICATION_DATABASE_MODULE[ename]
                    break
        if _modulename is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                message="".join(
                    (
                        "None of the available database engines can be ",
                        "used to create a database.",
                    )
                ),
                title="New",
            )
            return
        if self._database_modulename != _modulename:
            if self._database_modulename is not None:
                tkinter.messagebox.showinfo(
                    parent=self._get_toplevel(),
                    message="".join(
                        (
                            "The database engine needed for this database ",
                            "is not the one already in use.\n\nYou will ",
                            "have to Quit and start the application again ",
                            "to create this database.",
                        )
                    ),
                    title="New",
                )
                return
            self._database_enginename = _enginename
            self._database_modulename = _modulename

            def import_name(modulename, name):
                try:
                    module = __import__(
                        modulename, globals(), locals(), [name]
                    )
                except ImportError:
                    return None
                return getattr(module, name)

            self._database_class = import_name(_modulename, _Import.Database)
            self._fullposition_class = import_name(
                FULL_POSITION_MODULE[_enginename], _Import.FullPositionDS
            )
            self._partialposition_class = import_name(
                PARTIAL_POSITION_MODULE[_enginename],
                _Import.ChessQueryLanguageDS,
            )
            self._engineanalysis_class = import_name(
                ANALYSIS_MODULE[_enginename], _Import.AnalysisDS
            )
            self._selection_class = import_name(
                SELECTION_MODULE[_enginename], _Import.SelectionDS
            )

        try:
            self._open_database_directory(chessfolder)
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                message="".join(
                    (
                        "Unable to create database\n\n",
                        str(chessfolder),
                        "\n\nThe reported reason is:\n\n",
                        str(exc),
                    )
                ),
                title="New",
            )
            self._close_database_and_hide_widgets()
            # self.database = None  # Should be 'self.opendatabase = None'?
            # pylint message broad-except.
            # Can keep going for some exceptions.
            raise ChessError(
                " database in ".join(("Unable to create", APPLICATION_NAME))
            ) from exc

    def _database_close(self):
        """Close chess database."""
        if self.opendatabase is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Close",
                message="No chess database open",
            )
        elif self._database_class is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Close",
                message="Database interface not defined",
            )
        elif self._is_import_subprocess_active():
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Close",
                message="An import of PGN data is in progress",
            )
        else:
            dlg = tkinter.messagebox.askquestion(
                parent=self._get_toplevel(),
                title="Close",
                message="Close chess database",
            )
            if dlg == tkinter.messagebox.YES:
                if self.opendatabase:
                    self._close_database_and_hide_widgets()
                    self.opendatabase = None

    def _database_delete(self):
        """Delete chess database."""
        if self.opendatabase is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Delete",
                message="".join(
                    (
                        "Delete will not delete a database unless it can be ",
                        "opened.\n\nOpen the database and then Delete it.",
                    )
                ),
            )
            return
        dlg = tkinter.messagebox.askquestion(
            parent=self._get_toplevel(),
            title="Delete",
            message="".join(
                (
                    "Please confirm that the chess database in\n\n",
                    self.opendatabase.home_directory,
                    "\n\nis to be deleted.",
                )
            ),
        )
        if dlg == tkinter.messagebox.YES:
            # Replicate _close_database_and_hide_widgets replacing
            # close_database() call with
            # delete_database() call.  The close_database() call just before
            # setting opendatabase to None is removed.
            self._close_recordsets()
            message = self.opendatabase.delete_database()
            if message:
                tkinter.messagebox.showinfo(
                    parent=self._get_toplevel(),
                    title="Delete",
                    message=message,
                )
            self.root.wm_title(APPLICATION_NAME)
            self.ui.set_open_database_and_engine_classes()
            self.ui.hide_game_grid()
            self._set_error_file_name(directory=None)

            message = "".join(
                (
                    "The chess database in\n\n",
                    self.opendatabase.home_directory,
                    "\n\nhas been deleted.",
                )
            )
            self.opendatabase = None
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(), title="Delete", message=message
            )
        else:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Delete",
                message="The chess database has not been deleted",
            )

    def _index_select(self):
        """Enter a new index seletion (callback for Menu option)."""
        self._new_index_selection()

    def _new_index_selection(self):
        """Enter a new index selection."""
        selection = QueryDisplayInsert(
            master=self.ui.view_selection_rules_pw,
            ui=self.ui,
            items_manager=self.ui.selection_items,
            itemgrid=self.ui.base_games,
        )  # probably main list of games
        selection.query_statement.process_query_statement("")
        selection.set_and_tag_item_text(reset_undo=True)
        self.ui.add_selection_rule_to_display(selection)
        try:
            # Is new window only one available for user interaction?
            if self.root.focus_displayof() != self.root:
                return
        except KeyError:
            # Launch; Database Open; Database Close; Position Partial
            pass

        # Wrap to take account of self.ui.single_view
        self.ui.selection_items.active_item.takefocus_widget.focus_set()

    def _index_show(self):
        """Show list of stored stored selection rules."""
        if self.opendatabase is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Show",
                message="No chess database open",
            )
        elif self.ui.base_selections.is_visible():
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Show",
                message="Selection rules already shown",
            )
        else:
            self.ui.show_selection_rules_grid(self.opendatabase)

    def _index_hide(self):
        """Hide list of stored selection rules."""
        if self.opendatabase is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Hide",
                message="No chess database open",
            )
        elif not self.ui.base_selections.is_visible():
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Hide",
                message="Selection rules already hidden",
            )
        else:
            self.ui.hide_selection_rules_grid()

    def _create_options_index_callback(self, index):
        """Return callback to bind to index selection menu buttons."""

        def index_changed():
            """Set the index used to display list of games."""
            if self.opendatabase is None:
                tkinter.messagebox.showinfo(
                    parent=self._get_toplevel(),
                    title="Select Index for games database",
                    message="No chess database open",
                )
                return

            ui = self.ui
            self._index = index
            ui.base_games.set_data_source(
                DataSource(
                    self.opendatabase,
                    GAMES_FILE_DEF,
                    self._index,
                    chess_db_row_game(ui),
                ),
                ui.base_games.on_data_change,
            )
            if ui.base_games.datasource.recno:
                ui.base_games.set_partial_key()
            ui.base_games.load_new_index()
            if ui.base_games.datasource.dbname in ui.allow_filter:
                ui.set_toolbarframe_normal(ui.move_to_game, ui.filter_game)
            else:
                ui.set_toolbarframe_disabled()

        return index_changed

    def _position_show(self):
        """Show list of stored partial positions."""
        if self.opendatabase is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Show",
                message="No chess database open",
            )
        elif self.ui.base_partials.is_visible():
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Show",
                message="Partial positions already shown",
            )
        else:
            self.ui.show_partial_position_grid(self.opendatabase)

    def _position_hide(self):
        """Hide list of stored partial positions."""
        if self.opendatabase is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Hide",
                message="No chess database open",
            )
        elif not self.ui.base_partials.is_visible():
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Hide",
                message="Partial positions already hidden",
            )
        else:
            self.ui.hide_partial_position_grid()

    def _repertoire_show(self):
        """Show list of stored repertoire games (opening variations)."""
        if self.opendatabase is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Show",
                message="No chess database open",
            )
        elif self.ui.base_repertoires.is_visible():
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Show",
                message="Opening variations already shown",
            )
        else:
            self.ui.show_repertoire_grid(self.opendatabase)

    def _repertoire_hide(self):
        """Hide list of stored repertoire games (opening variations)."""
        if self.opendatabase is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Hide",
                message="No chess database open",
            )
        elif not self.ui.base_repertoires.is_visible():
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Hide",
                message="Opening variations already hidden",
            )
        else:
            self.ui.hide_repertoire_grid()

    def _open_database_directory(self, chessfolder):
        """Open chess database after creating it if necessary."""
        self.opendatabase = self._database_class(
            chessfolder, **self._chessdbkargs
        )
        self.opendatabase.open_database()
        self.ui.set_board_colours_from_options(
            options.get_saved_options(chessfolder)
        )
        # start code also used in _retry_import
        self.root.wm_title(
            " - ".join(
                (
                    APPLICATION_NAME,
                    os.path.join(
                        os.path.basename(os.path.dirname(chessfolder)),
                        os.path.basename(chessfolder),
                    ),
                )
            )
        )
        self.ui.set_open_database_and_engine_classes(
            database=self.opendatabase,
            fullpositionclass=self._fullposition_class,
            partialpositionclass=self._partialposition_class,
            engineanalysisclass=self._engineanalysis_class,
            selectionclass=self._selection_class,
        )
        self.ui.base_games.set_data_source(
            DataSource(
                self.opendatabase,
                GAMES_FILE_DEF,
                self._index,
                chess_db_row_game(self.ui),
            )
        )
        self.ui.show_game_grid(self.opendatabase)
        # end code also used in _retry_import

    def _close_database_and_hide_widgets(self):
        """Close database and hide database display widgets."""
        self._close_recordsets()
        self.opendatabase.close_database()
        self.root.wm_title(APPLICATION_NAME)

        # Order matters after changes to solentware-base first implemented as
        # solentware-bitbases in March 2019.
        # Conjecture is timing may still lead to exception in calls, driven by
        # timer, to _find_engine_analysis().  None seen yet.
        self.ui.set_open_database_and_engine_classes()
        self.ui.hide_game_grid()

        self._set_error_file_name(directory=None)

    # Close recordsets which do not have a defined lifetime.
    # Typically a recordset representing a scrollable list of records where
    # the records on the list vary with the state of a controlling widget.
    # Called just before opendatabase.close_database() to prevent the recordset
    # close() method being called on 'del recordset' after close_database() has
    # deleted the recordsets.
    # (The _dpt module needs this, but _db and _sqlite could get by without.)
    def _close_recordsets(self):
        ui = self.ui

        # If base_games is populated from a selection rule the datasource will
        # have a recordset which must be destroyed before the database is
        # closed.
        # This only affects DPT databases (_dpt module) but the _sqlite and _db
        # modules have 'do-nothing' methods to fit.
        data_source = ui.base_games.datasource
        if (
            data_source
            and hasattr(data_source, "recordset")
            and data_source.recordset is not None
        ):
            data_source.recordset.close()

        for grid in ui.game_games, ui.repertoire_games, ui.partial_games:
            data_source = grid.datasource
            if data_source:
                if data_source.recordset:
                    data_source.recordset.close()

        # This closes one of the five _DPTRecordSet instances which cause a
        # RuntimeError, because of an APIDatabaseContext.DestroyRecordSets()
        # call done earlier in close database sequence, in __del__ after doing
        # the sample CQL query 'cql() Pg7'.  Adding, say, pb3, to the query
        # raises the RuntimeError count to five, from four, while doing just
        # 'cql()' gets rid of all the RuntimeError exceptions.
        # Quit after close database otherwise finishes normally, but open drops
        # into MicroSoft Window's 'Not Responding' stuff sometimes.  Or perhaps
        # I have not seen it happen for quit yet.
        # The origin of the other four _DPTRecordSet instances has not been
        # traced yet.
        if ui.partial_games.datasource:
            ui.partial_games.datasource.cqlfinder = None

        # Not sure why these need an undefined lifetime.
        for item in ui.game_items, ui.repertoire_items:
            for widget in item.order:
                data_source = widget.analysis_data_source
                if data_source:
                    if data_source.recordset:
                        data_source.recordset.close()
        for widget in ui.selection_items.order:
            # widget.query_statement.where.node.result.answer is an example
            # instance that must be closed when query answer is displayed.
            # If query is typed in, not read from database, the DPT message
            # 'Bug: this context has no such record set object (any more?)'
            # is reported in a RuntimeError exception.  _DPTRecordList.__del__
            # raises this, and the problem is the DestroyAllRecordSets() call
            # done by close_database before the _DPTRecordList instance is
            # deleted.
            # Attribute widget.query_statement.where.node.result.answer is an
            # example. Closing the instance here clears the problem.
            # If query is read from database, a 'Python has stopped working'
            # dialogue is presented and Windows tries to find a solution!
            # I assume the cause is the lingering _DPTRecordList.
            # May need to add this to get rid of constraints in the Where tree.
            # if widget.datasource:
            #    widget.datasource.where = None
            pass

        for widget in ui.partial_items.order:
            # Same as selection_items, just above, for a typed CQL query but I
            # have not tracked down an example.
            # No problem for CQL query read from database.
            pass

        # Used print() to trace what was going on.
        # Gave each _DPTRecordList and _DPTFoundSet __init__ call a serial
        # number, defined as _DPTRecordSet.serial and held as self._serial,
        # which was printed for the instances which got a RuntimeError.
        # It was the same serials each time for the same query.
        # A traceback.print_stack() in __init__ showed the same profile for
        # each of these instances when created.
        # print() statements on entry to each method mentioned in the traceback
        # showed nothing unusual about these cases compared with all the others
        # which 'behaved properly' for deletion.
        # So tried forcing garbage collection, which seemed to work and does
        # not break the _db or _sqlite cases.
        gc.collect()

    # The methods which import data to a database.

    def _database_import(self):
        """Import games to open database."""
        if self.opendatabase is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Import",
                message="No chess database open to receive import",
            )
            return
        if self._database_class is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Import",
                message="Database interface not defined",
            )
            return
        if sum(
            len(i.stack)
            for i in (
                self.ui.game_items,
                self.ui.repertoire_items,
                self.ui.partial_items,
                self.ui.selection_items,
            )
        ):
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Import",
                message="".join(
                    (
                        "All game, repertoire, selection, and partial ",
                        "position, items must be closed before starting ",
                        "an import.",
                    )
                ),
            )
            return
        # Use askopenfilenames rather than askopenfilename with
        # multiple=Tkinter.TRUE because in freebsd port of Tkinter a tuple
        # is returned while at least some versions of the Microsoft Windows
        # port return a space separated string (which looks a lot like a
        # TCL list - curly brackets around path names containing spaces).
        # Then only the dialogues intercept of askopenfilenames needs
        # changing as askopenfilename with default multiple argument
        # returns a string containg one path name in all cases.
        #
        # Under Wine multiple=Tkinter.TRUE has no effect at Python 2.6.2 so
        # the dialogue supports selection of a single file only.
        gamefile = tkinter.filedialog.askopenfilenames(
            parent=self._get_toplevel(),
            title="Select files containing games to import",
            initialdir="~",
            filetypes=[("Portable Game Notation (chess)", ".pgn")],
        )
        if gamefile:
            self.statusbar.set_status_text(
                text="Please wait while importing PGN file"
            )
            # gives time for destruction of dialogue and widget refresh
            # does nothing for obscuring and revealing application later
            self.root.after_idle(
                self.try_command(self._import_pgnfiles, self.root), gamefile
            )

    def _import_repertoires(self):
        """Import repertoires from PGN-like file."""
        if self._is_import_subprocess_active():
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Import Repertoires",
                message="An import of PGN data is in progress",
            )
            return
        tkinter.messagebox.showinfo(
            parent=self._get_toplevel(),
            title="Import Repertoires",
            message="Not implemented",
        )

    def _import_positions(self):
        """Import positions from text file."""
        if self._is_import_subprocess_active():
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Import Positions",
                message="An import of PGN data is in progress",
            )
            return
        tkinter.messagebox.showinfo(
            parent=self._get_toplevel(),
            title="Import Positions",
            message="Not implemented",
        )

    def _import_pgnfiles(self, pgnfiles):
        """Import games to open database."""
        self.ui.set_import_subprocess()  # raises exception if already active
        self._pgnfiles = pgnfiles
        usedu = self.opendatabase.use_deferred_update_process()
        if usedu is None:
            tkinter.messagebox.showinfo(
                parent=self._get_toplevel(),
                title="Import",
                message="".join(
                    (
                        "Import\n\n",
                        "\n".join([os.path.basename(p) for p in pgnfiles]),
                        "\n\ncancelled",
                    )
                ),
            )
            self.statusbar.set_status_text(text="")
            return
        self.opendatabase.close_database_contexts()
        self.ui.set_import_subprocess(
            subprocess_id=multiprocessing.Process(
                target=rundu.rundu,
                args=(
                    self.opendatabase.home_directory,
                    pgnfiles,
                    usedu,
                ),
            )
        )
        self.ui.get_import_subprocess().start()
        self._wait_deferred_updates(pgnfiles)
        return

    def _wait_deferred_updates(self, pgnfiles):
        """Wait until subprocess doing deferred updates completes.

        pgnfiles - the PGN files being imported

        Wait for import subprocess to finish in a thread then do restart
        User Interface actions after idletasks.

        """
        del pgnfiles

        def completed():
            self.ui.get_import_subprocess().join()

            # See comment near end of class definition DeferredUpdate in
            # sibling module chessdu for explanation of this change.
            # self.root.after_idle(
            #     self.try_command(after_completion, self.root))
            self.reportqueue.put(
                (
                    self._try_command_after_idle,
                    (after_completion, self.root),
                    {},
                )
            )

        def after_completion():
            returncode = self.ui.get_import_subprocess().exitcode
            archives, guards = self.opendatabase.get_archive_names(
                file=GAMES_FILE_DEF
            )[1:]

            # Failed or cancelled while taking backups.
            if guards or archives:
                if returncode == 0:
                    msg = "was cancelled "
                else:
                    msg = "failed "
                tkinter.messagebox.showinfo(
                    parent=self._get_toplevel(),
                    title="Import",
                    message="".join(
                        (
                            "The import ",
                            msg,
                            "before completion of backups.",
                            "\n\nThe database has not been changed and will ",
                            "not be opened.",
                            "\n\nRestore the database from a backup, either ",
                            "from the one just taken or from the regular ",
                            "system backup sequence.",
                        )
                    ),
                )
                return

            # Failed with no backups.
            if returncode != 0:
                tkinter.messagebox.showinfo(
                    parent=self._get_toplevel(),
                    title="Import",
                    message="".join(
                        (
                            "The import failed.\n\nBackups were not ",
                            "taken so the database cannot be restored ",
                            "and may not be usable.",
                        )
                    ),
                )
                return

            try:
                action = self.opendatabase.open_after_import(
                    files=(GAMES_FILE_DEF,)
                )
            except self.opendatabase.__class__.SegmentSizeError:
                action = self.opendatabase.open_after_import(
                    files=(GAMES_FILE_DEF,)
                )

            # Database full (DPT only).
            if action is None:
                self.statusbar.set_status_text(text="Database full")
                return

            self.ui.set_import_subprocess()
            self._refresh_grids_after_import()
            self.statusbar.set_status_text(text="")
            return

        self.queue.put_method(self.try_thread(completed, self.root))

    def _refresh_grids_after_import(self):
        """Repopulate grid from database after import."""
        # See _wait_deferred_update comment at call to this method.
        # Gets stuck in on_data_change.
        self.ui.base_games.on_data_change(None)
        if self.ui.game_items.count_items_in_stack():
            self.ui.game_games.set_partial_key()
            self.ui.game_items.active_item.set_game_list()
        if self.ui.partial_items.count_items_in_stack():
            self.ui.partial_games.set_partial_key()
            self.ui.partial_items.active_item.refresh_game_list()

    def _try_command_after_idle(self, method, widget):
        """Run command in main thread after idle."""
        self.root.after_idle(self.try_command(method, widget))

    def _retry_import(self, files):
        """Open database and retry import with increased file sizes.

        DPT does not increase file sizes automatically as needed.
        The action still makes sense in Berkeley DB if other files had to be
        deleted to allow the automatic increase to occur.

        """
        self.opendatabase.open_database_contexts(files=files)
        self.opendatabase.adjust_database_for_retry_import(files)
        self.opendatabase.close_database_contexts()
        if self._pgnfiles:
            self.statusbar.set_status_text(
                text="Please wait while importing PGN file"
            )
            self.root.after_idle(
                self.try_command(self._import_pgnfiles, self.root),
                self._pgnfiles,
            )

    # The methods which export data from a database.

    def export_all_games_pgn_reduced_export_format(self):
        """Export all database games in PGN reduced export format."""
        self.ui.export_report(
            export_game.export_all_games_pgn_reduced_export_format(
                self.opendatabase,
                self.ui.get_export_filename(
                    "Games (reduced export format)", pgn=True
                ),
            ),
            "Games (reduced export format)",
        )

    def export_all_games_pgn_no_comments_no_ravs(self):
        """Export games in PGN export format excluding comments and RAVs."""
        self.ui.export_report(
            export_game.export_all_games_pgn_no_comments_no_ravs(
                self.opendatabase,
                self.ui.get_export_filename(
                    "Games (no comments no ravs)", pgn=True
                ),
            ),
            "Games (no comments no ravs)",
        )

    def export_all_games_pgn_no_comments(self):
        """Export all games in PGN export format excluding comments."""
        self.ui.export_report(
            export_game.export_all_games_pgn_no_comments(
                self.opendatabase,
                self.ui.get_export_filename("Games (no comments)", pgn=True),
            ),
            "Games (no comments)",
        )

    def export_all_games_pgn(self):
        """Export all database games in PGN export format."""
        self.ui.export_report(
            export_game.export_all_games_pgn(
                self.opendatabase,
                self.ui.get_export_filename("Games", pgn=True),
            ),
            "Games",
        )

    def export_all_games_pgn_import_format(self):
        """Export all database games in a PGN import format."""
        self.ui.export_report(
            export_game.export_all_games_pgn_import_format(
                self.opendatabase,
                self.ui.get_export_filename("Games (import format)", pgn=True),
            ),
            "Games (import format)",
        )

    def export_all_games_text(self):
        """Export all games as a text file."""
        export_game.export_all_games_text(
            self.opendatabase,
            self.ui.get_export_filename("Games (internal format)", pgn=False),
        )

    def export_all_repertoires_pgn_no_comments(self):
        """Export all repertoires in PGN export format without comments."""
        export_repertoire.export_all_repertoires_pgn_no_comments(
            self.opendatabase,
            self.ui.get_export_filename("Repertoires (no comments)", pgn=True),
        )

    def export_all_repertoires_pgn(self):
        """Export all repertoires in PGN export format."""
        export_repertoire.export_all_repertoires_pgn(
            self.opendatabase,
            self.ui.get_export_filename("Repertoires", pgn=True),
        )

    def export_all_repertoires_pgn_import_format(self):
        """Export all repertoires in a PGN import format."""
        export_repertoire.export_all_repertoires_pgn_import_format(
            self.opendatabase,
            self.ui.get_export_filename(
                "Repertoires (import format)", pgn=True
            ),
        )

    def export_all_repertoires_text(self):
        """Export all repertoires as a text file."""
        export_repertoire.export_all_repertoires_text(
            self.opendatabase,
            self.ui.get_export_filename(
                "Repertoires (internal format)", pgn=False
            ),
        )

    def _export_positions(self):
        """Export all positions as a text file."""
        export_chessql.export_all_positions(
            self.opendatabase,
            self.ui.get_export_filename("Partial Positions", pgn=False),
        )


class Statusbar:
    """Status bar for chess application."""

    def __init__(self, root, background):
        """Create status bar widget."""
        self.status = tkinter.Text(
            root,
            height=0,
            width=0,
            background=background,
            relief=tkinter.FLAT,
            state=tkinter.DISABLED,
            wrap=tkinter.NONE,
        )
        self.status.pack(
            side=tkinter.RIGHT, expand=tkinter.TRUE, fill=tkinter.X
        )

    def get_status_text(self):
        """Return text displayed in status bar."""
        return self.status.cget("text")

    def set_status_text(self, text=""):
        """Display text in status bar."""
        self.status.configure(state=tkinter.NORMAL)
        self.status.delete("1.0", tkinter.END)
        self.status.insert(tkinter.END, text)
        self.status.configure(state=tkinter.DISABLED)
