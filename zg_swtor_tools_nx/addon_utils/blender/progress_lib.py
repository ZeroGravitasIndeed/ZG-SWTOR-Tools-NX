"""
progress_lib
============

Single-file, registration-free progress bar helper for Blender 4.5+ add-ons.

Any add-on can copy this file into its package and:

    1. Report progress from anywhere:   progress_lib.update("my_key", 0.5)
    2. Draw the bar in ANY UILayout:    progress_lib.draw(layout, "my_key")

State lives in a plain module-level dict keyed by a string, so the code that
does the work and the code that draws the bar are fully decoupled. Use a
unique key per task (prefix it with your add-on name to avoid collisions).

API summary
-----------
    start(key, text="")                      Mark a task active, factor = 0.
    update(key, factor, text=None, refresh=False)
                                             Set progress (0.0 - 1.0).
    finish(key)                              Mark the task inactive.
    is_active(key) -> bool                   Query running state.
    draw(layout, key, ...) -> bool           Draw the bar into a layout.
    task(key, total, text="", refresh=True)  Context manager for loops.
    clear()                                  Drop all tasks (call on unregister).

Threading note
--------------
Blender's UI and ``bpy`` data are not thread-safe. If work runs in a thread,
store progress in a thread-safe variable and call ``update()`` from a
``bpy.app.timers`` callback running on the main thread.
"""

from contextlib import contextmanager

import bpy

__all__ = ("start", "update", "finish", "is_active", "draw", "task", "clear")


# ---------------------------------------------------------------------------
# Internal state
# ---------------------------------------------------------------------------

class _State:
    """Per-task data: progress factor, label text, and active flag."""

    __slots__ = ("factor", "text", "active")

    def __init__(self):
        self.factor = 0.0
        self.text = ""
        self.active = False


# Registry of tasks: {key: _State}. Module-level, so it needs no registration.
# Note: each add-on that vendors its own copy of this file has its own registry.
_tasks = {}


def _get(key):
    """Return the _State for ``key``, creating it on first access."""
    state = _tasks.get(key)
    if state is None:
        state = _tasks[key] = _State()
    return state


def _redraw(force=False):
    """
    Request a UI redraw across all windows.

    :param force: If True, also run an immediate synchronous redraw. This is
        required when the caller is a blocking loop (e.g. an operator's
        ``execute``), because Blender otherwise does not repaint until the
        loop returns.
    """
    # bpy.data is used instead of bpy.context so this works from timers too.
    for wm in bpy.data.window_managers:
        for window in wm.windows:
            for area in window.screen.areas:
                area.tag_redraw()

    if force:
        try:
            # Documented-as-debug operator, widely used to force a repaint.
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        except RuntimeError:
            # No window available (e.g. background mode); safe to ignore.
            pass


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def start(key, text=""):
    """Mark task ``key`` as active with progress reset to 0."""
    state = _get(key)
    state.factor = 0.0
    state.text = text
    state.active = True
    _redraw()


def update(key, factor, text=None, refresh=False):
    """
    Set the progress of task ``key``.

    :param factor: Progress in [0.0, 1.0]; out-of-range values are clamped.
    :param text: Optional new label. ``None`` keeps the current label.
    :param refresh: Force an immediate repaint (needed in blocking loops).
    """
    state = _get(key)
    state.active = True
    state.factor = max(0.0, min(1.0, float(factor)))
    if text is not None:
        state.text = text
    _redraw(force=refresh)


def finish(key):
    """Mark task ``key`` as inactive; ``draw()`` will then hide the bar."""
    state = _get(key)
    state.factor = 1.0
    state.active = False
    _redraw()


def is_active(key):
    """Return True while task ``key`` is running."""
    state = _tasks.get(key)
    return bool(state and state.active)


def draw(layout, key, *, type='BAR', show_percent=True, hide_inactive=True):
    """
    Draw the progress indicator of task ``key`` into any ``UILayout``.

    Call it from any ``draw()`` method: panels, menus, popovers, preferences,
    or sub-layouts such as ``layout.box()`` / ``layout.row()``.

    :param layout: Target ``bpy.types.UILayout``.
    :param key: Task identifier.
    :param type: ``'BAR'`` or ``'RING'``.
    :param show_percent: Append the percentage to the label text.
    :param hide_inactive: Draw nothing when the task is not active.
    :return: True if something was drawn, so callers can fall back to other
        UI (e.g. a "Start" button) when it returns False.
    """
    state = _tasks.get(key)
    if state is None or (hide_inactive and not state.active):
        return False

    label = state.text
    if show_percent:
        label = f"{label} {state.factor:.0%}".strip()

    layout.progress(factor=state.factor, type=type, text=label)
    return True


class _Tracker:
    """Helper yielded by ``task()``; converts step counts to a factor."""

    def __init__(self, key, total, refresh):
        self._key = key
        self._total = max(1, int(total))  # Avoid division by zero.
        self._done = 0
        self._refresh = refresh

    def step(self, amount=1, text=None):
        """Advance by ``amount`` units out of ``total`` and update the bar."""
        self._done += amount
        update(self._key, self._done / self._total, text, self._refresh)


@contextmanager
def task(key, total, text="", refresh=True):
    """
    Context manager that wraps a loop of ``total`` steps.

    Usage::

        with progress_lib.task("myaddon.bake", len(items), "Baking") as t:
            for item in items:
                process(item)
                t.step()

    The task is always finished on exit, even if an exception is raised.

    :param refresh: Force a repaint on every step. Keep True for blocking
        code; set False if you already return to Blender's event loop.
    """
    start(key, text)
    try:
        yield _Tracker(key, total, refresh)
    finally:
        finish(key)


def clear():
    """Forget all tasks. Call from your add-on's ``unregister()``."""
    _tasks.clear()
