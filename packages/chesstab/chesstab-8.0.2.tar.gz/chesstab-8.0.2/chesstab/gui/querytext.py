# querytext.py
# Copyright 2015 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Widget to display a game selection rule."""

import tkinter
import tkinter.messagebox

from ..core.querystatement import QueryStatement
from .gamerow import chess_db_row_game
from ..core.chessrecord import ChessDBrecordGameTags
from .blanktext import NonTagBind, BlankText
from .sharedtext import SharedText, SharedTextEngineText, SharedTextScore


class QueryText(SharedText, SharedTextEngineText, SharedTextScore, BlankText):
    """Game selection rule widget.

    panel is used as the panel argument for the super().__init__ call.

    ui is the user interface manager for an instance of QueryText, usually an
    instance of ChessUI.

    items_manager is used as the items_manager argument for the
    super().__init__ call.

    itemgrid is the ui reference to the DataGrid from which the record was
    selected.

    Subclasses are responsible for providing a geometry manager.

    Attribute _most_recent_bindings is set to indicate the initial set of
    event bindings.  Instances will override this as required.

    """

    def __init__(
        self, panel, ui=None, items_manager=None, itemgrid=None, **ka
    ):
        """Create widgets to display game selection rule."""
        super().__init__(panel, items_manager=items_manager, **ka)
        self.ui = ui
        self.itemgrid = itemgrid

        # Selection rule parser instance to process text.
        self.query_statement = QueryStatement()
        if ui.base_games.datasource:
            self.query_statement.dbset = ui.base_games.datasource.dbset

    def set_and_tag_item_text(self, reset_undo=False):
        """Display the game selection rule as text.

        reset_undo causes the undo redo stack to be cleared if True.  Set True
        on first display of a selection rule for editing so that repeated
        Ctrl-Z in text editing mode recovers the original selection rule.

        """
        if not self._is_text_editable:
            self.score.configure(state=tkinter.NORMAL)
        self.score.delete("1.0", tkinter.END)
        self._map_initial_query_statement()
        if self._most_recent_bindings != NonTagBind.NO_EDITABLE_TAGS:
            self._bind_for_primary_activity()
        if not self._is_text_editable:
            self.score.configure(state=tkinter.DISABLED)
        if reset_undo:
            self.score.edit_reset()

    def set_statusbar_text(self):
        """Set status bar to display game selection rule name."""
        self.ui.statusbar.set_status_text(self.query_statement.get_name_text())

    def get_name_query_statement_text(self):
        """Return text from query statement Text widget."""
        text = self.score.get("1.0", tkinter.END).strip()
        return text

    def _map_initial_query_statement(self):
        """Convert tokens to text and show in query statement Text widget."""
        # No mapping of tokens to text in widget (yet).
        self.score.insert(
            tkinter.INSERT,
            self.query_statement.get_name_query_statement_text(),
        )

    def refresh_game_list(self):
        """Display games matching game selection rule, empty on errors."""
        grid = self.itemgrid
        if grid is None:
            return
        if grid.get_database() is None:
            return
        self.ui.base_games.set_data_source(
            self.ui.selectionds(
                grid.datasource.dbhome,
                self.ui.base_games.datasource.dbset,
                self.ui.base_games.datasource.dbset,
                chess_db_row_game(self.ui),
            ),
            self.ui.base_games.on_data_change,
        )
        statement = self.query_statement
        if statement.where_error:
            self.ui.base_games.datasource.get_selection_rule_games(None)
            self.ui.base_games.load_new_index()
            tkinter.messagebox.showerror(
                parent=self.ui.get_toplevel(),
                title="Display Game Selection Rule",
                message=statement.where_error.get_error_report(
                    grid.datasource
                ),
            )
        elif statement.where:
            grid.datasource.dbhome.start_read_only_transaction()
            try:
                statement.where.evaluate(
                    grid.datasource.dbhome.record_finder(
                        grid.datasource.dbset, ChessDBrecordGameTags
                    )
                )
            finally:
                grid.datasource.dbhome.end_read_only_transaction()

            # Workaround problem with query ''.  See Where.evaluate() also.
            result = statement.where.node.get_root().result
            if result is None:
                self.ui.base_games.datasource.get_selection_rule_games(None)
            else:
                self.ui.base_games.datasource.get_selection_rule_games(
                    result.answer
                )
            self.ui.base_games.load_new_index()

        elif statement.get_query_statement_text():
            self.ui.base_games.load_new_index()
        # else:
        #    tkinter.messagebox.showinfo(
        #        parent = self.ui.get_toplevel(),
        #        title='Display Game Selection Rule',
        #        message=''.join(
        #            ('Game list not changed because active query ',
        #             'has not yet been evaluated.',
        #             )))

        # Get rid of the 'Please wait ...' status text.
        self.ui.statusbar.set_status_text()
