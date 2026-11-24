"""
progress_lib_example
====================

Example consumer of ``progress_lib``. Place both files in the same folder
(or in the same add-on package and switch to ``from . import progress_lib``).

Shows the same task's bar drawn in two different layouts at once.
"""

bl_info = {
    "name": "Progress Lib Example",
    "author": "Example",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "3D Viewport > Sidebar > Progress Lib",
    "description": "Demonstrates progress_lib usage",
    "category": "Interface",
}

import time

import bpy
from bpy.types import Operator, Panel

# In a package this would be: from . import progress_lib
import zg_swtor_tools_nx.addon_utils.blender.progress_lib as progress_lib

# Unique task key; prefix with the add-on name to avoid collisions.
TASK_KEY = "progress_lib_example.demo"


class PLEXAMPLE_OT_run(Operator):
    """Run a blocking loop that reports progress through progress_lib"""

    bl_idname = "plexample.run"
    bl_label = "Start Task"

    def execute(self, context):
        """Process 50 dummy items, advancing the bar once per item."""
        items = range(50)

        # The context manager starts the task, finishes it on exit, and
        # forces a repaint at each step since this loop blocks the UI.
        with progress_lib.task(TASK_KEY, len(items), "Processing") as t:
            for _item in items:
                time.sleep(0.05)  # Placeholder for real work.
                t.step()

        return {'FINISHED'}


class PLEXAMPLE_PT_panel(Panel):
    """Sidebar panel drawing the bar in two different sub-layouts"""

    bl_label = "Progress Lib"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Progress Lib"

    def draw(self, context):
        """Draw the bar in a box and in a row; fall back to a button."""
        layout = self.layout

        # draw() returns False when the task is inactive -> show the button.
        if not progress_lib.draw(layout.box(), TASK_KEY):
            layout.operator(PLEXAMPLE_OT_run.bl_idname, icon='PLAY')
        else:
            # Same task, different layout and style: a ring inside a row.
            row = layout.row()
            progress_lib.draw(row, TASK_KEY, type='RING', show_percent=False)


_classes = (PLEXAMPLE_OT_run, PLEXAMPLE_PT_panel)


def register():
    """Register UI classes. progress_lib itself needs no registration."""
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister UI classes and release progress_lib state."""
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
    progress_lib.clear()


if __name__ == "__main__":
    register()
