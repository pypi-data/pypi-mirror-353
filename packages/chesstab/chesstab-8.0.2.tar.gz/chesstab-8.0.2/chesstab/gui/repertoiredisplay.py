# repertoiredisplay.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Widgets to display and edit repertoires.

These four classes display PGN text for games in the main window: they are
used in the gamelistgrid module.

The _RepertoireDisplay class provides attributes and behaviour shared by the
RepertoireDisplay, RepertoireDisplayInsert, and RepertoireDisplayEdit,
classes.  It also provides properties to support implementation of behaviour
shared with the CQL*, Game*, and Query*, classes.

The RepertoireDisplay, RepertoireDisplayInsert, and RepertoireDisplayEdit,
classes are subclasses of the relevant ShowPGN, InsertPGN, EditPGN, and
DisplayPGN, classes from the displaypgn module; to implement behaviour shared
with all text widgets in the main display (that includes widgets displaying
text).

"""

import tkinter

from solentware_grid.core.dataclient import DataNotify

from solentware_bind.gui.bindings import Bindings

from ..core.constants import TAG_OPENING
from .repertoire import Repertoire
from .repertoireedit import RepertoireEdit
from ..core.chessrecord import ChessDBrecordRepertoireUpdate
from .eventspec import EventSpec
from .display import Display
from .displaypgn import ShowPGN, InsertPGN, EditPGN, DisplayPGN
from .game import Game


class _RepertoireDisplay(ShowPGN, Game, Bindings, DataNotify, Display):
    """Extend and link PGN repertoire text to database.

    sourceobject - link to database.

    Attribute binding_labels specifies the order navigation bindings appear
    in popup menus.

    Attribute pgn_score_name provides the name used in widget titles and
    message text.

    Attribute pgn_score_tags provides the PGN tag names used in widget titles
    and message text.  It is the opening PGN tag defined in ChessTab.

    Attribute pgn_score_source provides the error key value to index a
    PGN game score with errors.

    Attribute pgn_score_updater provides the class used to process PGN text
    into a database update.

    """

    binding_labels = (
        EventSpec.navigate_to_position_grid,
        EventSpec.navigate_to_active_game,
        EventSpec.navigate_to_game_grid,
        EventSpec.navigate_to_repertoire_grid,
        EventSpec.repertoiredisplay_to_previous_repertoire,
        EventSpec.analysis_to_scoresheet,
        EventSpec.repertoiredisplay_to_next_repertoire,
        EventSpec.navigate_to_repertoire_game_grid,
        EventSpec.scoresheet_to_analysis,
        EventSpec.navigate_to_partial_grid,
        EventSpec.navigate_to_active_partial,
        EventSpec.navigate_to_partial_game_grid,
        EventSpec.navigate_to_selection_rule_grid,
        EventSpec.navigate_to_active_selection_rule,
        EventSpec.tab_traverse_backward,
        EventSpec.tab_traverse_forward,
    )

    # These exist so the insert_game_database methods in _RepertoireDisplay and
    # gamedisplay._GameDisplay, and delete_game_database in RepertoireDisplay
    # and gameedisplay.GameDisplay, can be modified and replaced by single
    # copies in the displaypgn.ShowPGN class.
    # See mark_partial_positions_to_be_recalculated() method too.
    # The names need to be more generic to make sense in cql, engine, and
    # query, context.
    pgn_score_name = "repertoire"
    pgn_score_source = ""
    pgn_score_tags = (TAG_OPENING,)
    pgn_score_updater = ChessDBrecordRepertoireUpdate

    def __init__(self, sourceobject=None, **ka):
        """Extend and link repertoire to database."""
        super().__init__(**ka)
        self.blockchange = False
        if self.ui.base_repertoires.datasource:
            self.set_data_source(self.ui.base_repertoires.get_data_source())
        self.sourceobject = sourceobject

    # Could be put in game.Repertoire class to hide the game.Game version.
    # Here can be justified because purpose is allow some methods to be moved
    # to displaypgn.ShowPGN class.
    @property
    def ui_displayed_items(self):
        """Return manager of widgets displaying a repertoire record."""
        return self.ui.repertoire_items

    # Defined so _cycle_item and give_focus_to_widget methods can be shared by
    # gamedisplay._GameDisplay and repertoiredisplay._RepertoireDisplay
    # classes.
    @property
    def ui_configure_item_list_grid(self):
        """Return function to configure repertoire grid to fit text."""
        return self.ui.configure_repertoire_grid

    # ui_base_table and mark_partial_positions_to_be_recalculated defined
    # so insert_game_database method can be shared by gamedisplay._GameDisplay
    # and repertoiredisplay._RepertoireDisplay classes.
    # See class attributes pgn_score_name and pgn_score_source too.

    @property
    def ui_base_table(self):
        """Return the User Interface TagRosterGrid object."""
        return self.ui.base_repertoires

    @property
    def ui_items_in_toplevels(self):
        """Return the User Interface objects in Toplevels."""
        return self.ui.games_and_repertoires_in_toplevels

    def mark_partial_positions_to_be_recalculated(self, datasource=None):
        """Do nothing.  Exists for compatibility with game display."""

    def _get_navigation_events(self):
        """Return event description tuple for navigation from repertoire."""
        return (
            (
                EventSpec.navigate_to_repertoire_grid,
                self.set_focus_repertoire_grid,
            ),
            (
                EventSpec.navigate_to_repertoire_game_grid,
                self.set_focus_repertoire_game_grid,
            ),
            (EventSpec.navigate_to_partial_grid, self.set_focus_partial_grid),
            (
                EventSpec.navigate_to_active_partial,
                self.set_focus_partialpanel_item,
            ),
            (
                EventSpec.navigate_to_partial_game_grid,
                self.set_focus_partial_game_grid,
            ),
            (
                EventSpec.navigate_to_position_grid,
                self.set_focus_position_grid,
            ),
            (EventSpec.navigate_to_active_game, self.set_focus_gamepanel_item),
            (EventSpec.navigate_to_game_grid, self.set_focus_game_grid),
            (
                EventSpec.navigate_to_selection_rule_grid,
                self.set_focus_selection_rule_grid,
            ),
            (
                EventSpec.navigate_to_active_selection_rule,
                self.set_focus_selectionpanel_item,
            ),
            (
                EventSpec.repertoiredisplay_to_previous_repertoire,
                self._prior_item,
            ),
            (EventSpec.repertoiredisplay_to_next_repertoire, self._next_item),
            (EventSpec.tab_traverse_forward, self.traverse_forward),
            (EventSpec.tab_traverse_backward, self.traverse_backward),
            # No traverse_round because Alt-F8 toggles repertoire and analysis.
        )

    def delete_item_view(self, event=None):
        """Remove repertoire item from screen."""
        del event
        self.set_data_source()
        self.ui.delete_repertoire_view(self)

    def on_game_change(self, instance):
        """Prevent update from self if instance refers to same record."""
        if self.sourceobject is not None:
            self._patch_pgn_score_to_fit_record_change_and_refresh_grid(
                self.ui.repertoire_games, instance
            )

    def on_repertoire_change(self, instance):
        """Prevent update from self if instance refers to same record."""
        if self.sourceobject is not None:
            if (
                instance.key == self.sourceobject.key
                and self.datasource.dbname == self.sourceobject.dbname
                and self.datasource.dbset == self.sourceobject.dbset
            ):
                self.blockchange = True

    def generate_popup_navigation_maps(self):
        """Return genenal and current widget navigation binding maps."""
        navigation_map = dict(self._get_navigation_events())
        local_map = {
            EventSpec.scoresheet_to_analysis: self.analysis_current_item,
        }
        return navigation_map, local_map


class RepertoireDisplay(
    _RepertoireDisplay, DisplayPGN, ShowPGN, Repertoire, DataNotify
):
    """Display a repertoire from a database allowing delete and insert."""

    # Allow for structure difference between RepertoireDisplay and GameDisplay
    # versions of delete_game_database.
    # Method comments suggest a problem exists which needs fixing.
    # Existence of this method prevents delete_game_database being used by
    # instances of superclasses of RepertoireDisplay, emulating the behaviour
    # before introduction of displaypgn module.
    @staticmethod
    def pgn_score_original_value(original_value):
        """Set source name for original_value object."""
        # currently attracts "AttributeError: 'ChessDBvalueGameTags' has
        # no attribute 'gamesource'.
        # original.value.gamesource = self.sourceobject.value.gamesource
        original_value.gamesource = ""

    def _create_primary_activity_popup(self):
        """Delegate then add close command to popup and return popup menu."""
        popup = super()._create_primary_activity_popup()
        self._add_close_item_entry_to_popup(popup)
        return popup

    def _create_select_move_popup(self):
        """Delegate then add close command to popup and return popup menu."""
        popup = super()._create_select_move_popup()
        self._add_close_item_entry_to_popup(popup)
        return popup


class RepertoireDisplayInsert(
    _RepertoireDisplay, InsertPGN, ShowPGN, RepertoireEdit, DataNotify
):
    """Display a repertoire from a database allowing insert.

    RepertoireEdit provides the widget and _RepertoireDisplay the database
    interface.
    """

    # This method forced by addition of second list element in Game record
    # value, which breaks the 'class <Repertoire>(<Game>)' relationship in
    # in classes in chessrecord module.
    def _construct_record_value(self):
        """Return record value for Repertoire record."""
        return repr(self.score.get("1.0", tkinter.END))


class RepertoireDisplayEdit(EditPGN, RepertoireDisplayInsert):
    """Display a repertoire from a database allowing edit and insert."""

    # Allow for structure difference between RepertoireDisplay and GameDisplay
    # versions of delete_game_database.
    # Method comments suggest a problem exists which needs fixing.
    # Existence of this method prevents delete_game_database being used by
    # instances of superclasses of RepertoireDisplay, emulating the behaviour
    # before introduction of displaypgn module.
    @staticmethod
    def pgn_score_original_value(original_value):
        """Set source name for original_value object."""
        # currently attracts "AttributeError: 'ChessDBvalueGameTags' has
        # no attribute 'gamesource'.
        # original.value.gamesource = self.sourceobject.value.gamesource
        original_value.gamesource = ""

    # _set_properties_on_grids defined so update_game_database method can be
    # shared by repertoiredisplay.RepertoireDisplayEdit and
    # gamedisplay.GameDisplayEdit classes.
    # See class attributes pgn_score_name and pgn_score_source too.
    # The property which returns self.ui.base_repertoires is ignored because
    # the GameDisplayEdit version of the method sets properties on all grids.
    def set_properties_on_game_grids(self, newkey):
        """Set grid row properties of row for newkey record."""
        self.ui.base_repertoires.set_properties(newkey)

    # This method forced by addition of second list element in Game record
    # value, which breaks the 'class <Repertoire>(<Game>)' relationship in
    # in classes in chessrecord module.
    def _construct_record_value(self):
        """Return record value for Repertoire record."""
        return repr(self.get_score_error_escapes_removed())
