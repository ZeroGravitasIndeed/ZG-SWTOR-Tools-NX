"""Searchable single-item selectors for a large, static list of items.

Target: Blender 4.5 (uses ``UILayout.panel()``, available since 4.1).

Data source
-----------
``items.json`` bundled next to this module. Flat JSON object mapping a
human-readable name (the searched text) to a fully qualified name (FQN)::

    {
        "Wooden Chair": "assets.furniture.chairs.wooden_chair",
        "Steel Table":  "assets.furniture.tables.steel_table"
    }

The data is loaded once per session and cached at module level.

Three selector variants are provided, each in its own collapsible section:

1. Search popup  -- ``invoke_search_popup`` over a static EnumProperty.
                    Fuzzy-ranked: matches are listed first, non-matches
                    are NOT hidden. Needs no CollectionProperty.
2. Filtered list -- ``UIList`` with a custom ``filter_items``. Strict
                    substring filtering: non-matches are hidden.
3. Inline search -- ``prop_search`` bound to a string property. Fuzzy-ranked
                    like the popup; the field turns red if the text is not
                    an existing entry.

Each variant stores the chosen item's *name* (not an index) in a Scene
string property, so the selection survives reordering of the JSON file and
is saved in the .blend file. Use ``resolve_fqn(name)`` to get the FQN.

Packaging
---------
As a Blender 4.5 extension, ship this file as ``__init__.py`` together with
``items.json`` and a ``blender_manifest.toml``.
"""

import json
from pathlib import Path

import bpy
from bpy.app.handlers import persistent
from bpy.props import (
    CollectionProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import Operator, Panel, PropertyGroup, UIList

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# JSON file shipped next to this module. Path(__file__) resolves correctly
# for extensions; never write to this location at runtime.
_JSON_PATH = Path(__file__).parent / "addon_resources" / "processed_game_data" / "armor_names_to_fqn.json"

# When True, the UIList filter also matches against the FQN, not only the name.
MATCH_FQN = False

# ---------------------------------------------------------------------------
# Static data cache
# ---------------------------------------------------------------------------
# These module-level objects live for the whole session. Blender does not
# keep its own reference to the strings returned by an EnumProperty items
# callback, so the list returned to it MUST stay referenced somewhere.

_items = {}         # human-readable name -> FQN, in file order
_enum_items = []    # (identifier, label, description) tuples for the enum
_search_keys = {}   # name -> lowercase search text, used by the UIList filter


def get_items():
    """Return the name -> FQN mapping, reading the JSON file on first use.

    Also builds the enum item list and the lowercase search keys, so that
    neither has to be recomputed on redraw.

    Returns:
        dict[str, str]: Human-readable name -> FQN, in file order.
            Empty if the file is missing or malformed (an error is printed
            to the console; the UI then shows a warning label).
    """
    global _items, _enum_items, _search_keys

    # Already loaded: return the cache.
    if _items:
        return _items

    # Read and parse. utf-8-sig tolerates an optional BOM from some editors.
    try:
        with open(_JSON_PATH, "r", encoding="utf-8-sig") as file:
            data = json.load(file)
    except (OSError, ValueError) as err:
        # json.JSONDecodeError is a subclass of ValueError.
        print(f"[item_selector] Cannot read {_JSON_PATH}: {err}")
        return _items

    # Validate the structure: flat object with string values.
    # (JSON object keys are always strings.)
    if not isinstance(data, dict) or not all(
        isinstance(value, str) for value in data.values()
    ):
        print(f"[item_selector] {_JSON_PATH} must be a flat name -> FQN object.")
        return _items

    _items = data

    # Enum items: identifier and label are the name; the FQN is the tooltip.
    _enum_items = [(name, name, fqn) for name, fqn in data.items()]

    # Lowercase search text, computed once instead of on every redraw.
    if MATCH_FQN:
        _search_keys = {n: f"{n} {f}".lower() for n, f in data.items()}
    else:
        _search_keys = {n: n.lower() for n in data}

    return _items


def resolve_fqn(name):
    """Return the FQN for a stored selection name.

    Args:
        name (str): Value of one of the scene selection properties.

    Returns:
        str | None: The FQN, or None if the name is empty or unknown
            (e.g. it was removed from the JSON in a newer add-on version).
    """
    return get_items().get(name)


# ---------------------------------------------------------------------------
# Collection for UIList / prop_search
# ---------------------------------------------------------------------------

class ItemEntry(PropertyGroup):
    """One entry of the item collection.

    The inherited ``name`` property holds the human-readable key. It is the
    text that ``prop_search`` matches and the text the list displays.
    """

    # Fully qualified name associated with the name.
    fqn: StringProperty(name="FQN")


def _on_list_index_update(self, context):
    """Update callback of ``WindowManager.item_index``.

    Mirrors the active list row into a Scene string property, because the
    WindowManager is not saved with the .blend file but the Scene is.

    Args:
        self (bpy.types.WindowManager): Owner of the changed property.
        context (bpy.types.Context): Current context.
    """
    entries = self.item_collection
    idx = self.item_index
    # The index may be -1 (nothing selected) or stale; guard the range.
    context.scene.selected_list_item = (
        entries[idx].name if 0 <= idx < len(entries) else ""
    )


def populate_collections():
    """Fill the item collection of every WindowManager from the cache.

    ID properties cannot be written while the add-on registers (restricted
    context) or inside ``draw()``. Therefore this is called from a one-shot
    timer (initial load) and from a ``load_post`` handler (file open).

    WindowManagers that already hold all entries are skipped.
    """
    mapping = get_items()
    if not mapping:
        return

    # The active scene (if any) provides the saved list selection to restore.
    scene = getattr(bpy.context, "scene", None)
    saved_name = scene.selected_list_item if scene else ""

    for wm in bpy.data.window_managers:
        if len(wm.item_collection) == len(mapping):
            continue

        wm.item_collection.clear()
        for name, fqn in mapping.items():
            entry = wm.item_collection.add()
            entry.name = name
            entry.fqn = fqn

        # Re-highlight the saved selection in the list. The index is only
        # set when the name exists; otherwise it stays at -1 (no highlight).
        if saved_name in mapping:
            wm.item_index = list(mapping).index(saved_name)


@persistent
def _on_load_post(_dummy):
    """Repopulate after a .blend file is opened (File > Open / New).

    ``@persistent`` keeps the handler alive across file loads.
    """
    populate_collections()


def _populate_once():
    """One-shot timer callback for the initial population after register().

    Returns:
        None: Tells Blender not to reschedule the timer.
    """
    populate_collections()
    return None


# ---------------------------------------------------------------------------
# Variant 1: search popup
# ---------------------------------------------------------------------------

def enum_items_callback(self, context):
    """Items callback of the popup operator's EnumProperty.

    Args:
        self (bpy.types.Operator): Operator owning the property.
        context (bpy.types.Context): Current context.

    Returns:
        list[tuple[str, str, str]]: The module-level cache. Returning a
            persistent object avoids Blender reading freed string memory.
    """
    get_items()  # Ensure the cache is populated.
    return _enum_items


def _tag_redraw_all(context):
    """Request a redraw of every 3D Viewport area in all windows.

    Property changes made by widgets redraw their region automatically.
    Changes made from ``Operator.execute`` after a search popup closes do
    not, so the sidebar would show stale data until the cursor hovers it.
    ``context.area`` is unreliable at that point (it can be None), hence
    the walk over all windows.

    Args:
        context (bpy.types.Context): Current context.
    """
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


class SELECTOR_OT_pick_item(Operator):
    """Pick an item through a searchable popup."""

    bl_idname = "selector.pick_item"
    bl_label = "Pick Item"
    # The property shown in the search popup.
    bl_property = "item"

    item: EnumProperty(name="Item", items=enum_items_callback)

    def invoke(self, context, event):
        """Open the search popup instead of a standard dialog.

        ``invoke_search_popup`` calls ``execute`` once the user confirms an
        entry, so the operator itself finishes immediately.
        """
        context.window_manager.invoke_search_popup(self)
        return {'FINISHED'}

    def execute(self, context):
        """Store the chosen name in the Scene."""
        context.scene.selected_popup_item = self.item
        # Refresh the sidebar immediately (see _tag_redraw_all).
        _tag_redraw_all(context)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Variant 2: strictly filtered UIList
# ---------------------------------------------------------------------------

class SELECTOR_UL_items(UIList):
    """List that shows only entries matching every word of the filter text."""

    # Show the filter field by default instead of behind the small arrow.
    use_filter_show = True

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):
        """Draw one row.

        Args:
            layout (bpy.types.UILayout): Row layout.
            item (ItemEntry): The entry being drawn.
        """
        # A plain label (not an editable prop), so names cannot be renamed
        # in the UI and desynchronise from the JSON data.
        layout.label(text=item.name, icon='DOT')

    def filter_items(self, context, data, propname):
        """Return flags marking which items are visible.

        Called on every redraw of an expanded list. Items whose flag is 0
        are omitted; no reordering is performed.

        Args:
            data: Owner of the collection (here, the WindowManager).
            propname (str): Name of the collection property on ``data``.

        Returns:
            tuple[list[int], list[int]]: (visibility flags, new order).
                An empty order list preserves the original order.
        """
        entries = getattr(data, propname)

        # self.filter_name is the text typed into the list's filter field.
        # Splitting on whitespace requires ALL words to match, in any order.
        words = self.filter_name.lower().split()

        # An empty filter yields no words, and all([]) is True, so every
        # item stays visible. Keys come from the precomputed cache.
        flags = [
            self.bitflag_filter_item
            if all(word in _search_keys.get(entry.name, "") for word in words)
            else 0
            for entry in entries
        ]
        return flags, []


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def _draw_selection(layout, name):
    """Draw the selected name and its FQN as read-only labels.

    Args:
        layout (bpy.types.UILayout): Layout to draw into.
        name (str): Stored selection name (may be empty or unknown).
    """
    fqn = resolve_fqn(name)
    if fqn is None:
        return
    col = layout.column(align=True)
    col.label(text=f"Selected: {name}")
    col.label(text=f"FQN: {fqn}")


class VIEW3D_PT_item_selector(Panel):
    """Sidebar panel with one collapsible section per selector variant."""

    bl_label = "Item Selector"
    bl_idname = "VIEW3D_PT_item_selector"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Selector"

    def draw(self, context):
        """Draw the three selector variants.

        ``layout.panel(idname, default_closed)`` returns ``(header, body)``.
        ``body`` is None while the section is collapsed, so collapsed
        sections draw nothing and ``filter_items`` does not run for them.
        ``idname`` must be unique within this panel; Blender stores the
        open/closed state under it.
        """
        layout = self.layout
        scene = context.scene
        wm = context.window_manager

        # The collection is filled by a timer / load handler. Until then
        # (or if the JSON failed to load) there is nothing to show.
        if not wm.item_collection:
            layout.label(text="Items not loaded.", icon='ERROR')
            return

        # --- Variant 1: search popup ---------------------------------------
        # tool_section = layout.box()
        
        # tool_section.label(text="Search popup")
        # tool_section.operator(
        #     SELECTOR_OT_pick_item.bl_idname,
        #     text=scene.selected_popup_item or "Select...",
        #     icon='VIEWZOOM',
        # )
        # _draw_selection(tool_section, scene.selected_popup_item)

        # --- Variant 2: strictly filtered list -----------------------------
        tool_section = layout.box()

        tool_section.label(text="Add Armor Part")
        tool_section.template_list(
            "SELECTOR_UL_items", "selector_list",  # class, unique list id
            wm, "item_collection",                 # data source
            wm, "item_index",                      # active index
            rows=8,
            layout='COMPACT',
        )
        _draw_selection(tool_section, scene.selected_list_item)

        # # --- Variant 3: inline search field --------------------------------
        # header, body = layout.panel("selector_inline", default_closed=True)
        # header.label(text="Inline search")
        # if body:
        #     # Edits the Scene string; suggestions come from the collection.
        #     # The field is red when the text matches no entry.
        #     body.prop_search(
        #         scene, "selected_search_item",
        #         wm, "item_collection",
        #         text="", icon='VIEWZOOM',
        #     )
        #     _draw_selection(body, scene.selected_search_item)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

classes = (
    ItemEntry,
    SELECTOR_OT_pick_item,
    SELECTOR_UL_items,
    VIEW3D_PT_item_selector,
)


def register():
    """Register classes, properties, and population hooks."""
    for cls in classes:
        bpy.utils.register_class(cls)

    # Session-only data (not saved in the .blend): the entries and the
    # list's active index.
    bpy.types.WindowManager.item_collection = CollectionProperty(type=ItemEntry)
    bpy.types.WindowManager.item_index = IntProperty(
        name="Active Item",
        default=-1,  # -1: nothing highlighted
        update=_on_list_index_update,
    )

    # Saved selections: item names, one per variant.
    bpy.types.Scene.selected_popup_item = StringProperty(name="Popup Selection")
    bpy.types.Scene.selected_list_item = StringProperty(name="List Selection")
    bpy.types.Scene.selected_search_item = StringProperty(name="Search Selection")

    # Fill the collection after file loads, and once now. Context is
    # restricted inside register(), so the first fill is deferred to a timer.
    bpy.app.handlers.load_post.append(_on_load_post)
    bpy.app.timers.register(_populate_once, first_interval=0.0)


def unregister():
    """Undo everything done in register(), in reverse order."""
    # Cancel the initial fill if it has not run yet.
    if bpy.app.timers.is_registered(_populate_once):
        bpy.app.timers.unregister(_populate_once)
    if _on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load_post)

    del bpy.types.Scene.selected_search_item
    del bpy.types.Scene.selected_list_item
    del bpy.types.Scene.selected_popup_item
    del bpy.types.WindowManager.item_index
    del bpy.types.WindowManager.item_collection

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    # Allows running the file from Blender's text editor for testing.
    # items.json must then sit next to the saved .blend file's script path.
    register()