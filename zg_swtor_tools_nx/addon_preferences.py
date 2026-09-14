import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty

import os
from pathlib import Path



from .addon_checks import requirements_checks



ADDON_ROOT = __file__.rsplit(__name__.rsplit(".")[0])[0] + __name__.rsplit(".")[0]

Y_SCALING_GRAL = 0.9
Y_SCALING_INFO = 0.65
Y_SCALING_SPACER = 0.3



# PREFERENCES ----------------------------------------

class addonPreferences(bpy.types.AddonPreferences):
    bl_idname = "zg_swtor_tools_nx"

    # Preferences properties --------------------
    
    # Custom SWTOR shaders blendfile folderpath
    swtor_custom_shaders_blendfile_path: bpy.props.StringProperty(
        name = "Custom Shaders File",
        description = "Path to a Blend file holding custom replacement SWTOR shaders\nfor the current modern ones.\n\n• It defaults to the one stored inside the addon",
        subtype = "FILE_PATH",
        default = os.path.join(ADDON_ROOT, "rsrc", "Custom SWTOR Shaders.blend"),
        maxlen = 1024
    )
    
    # Behavior of some tools when processing SWTOR objects with custom mesh scaling
    # (the new scale settings in the .gr2 importer Add-on, which are recorded in the
    # imported objects' as a 'gr2_scale' custom property)
    use_gr2_scale_custom_prop: bpy.props.BoolProperty(
        name = "Use SWTOR Objects' Mesh Scale Data If Available",
        description = "If a SWTOR object has a 'gr2_scale' custom property, added by a .gr2 Importer Add-on,\nmesh size-sensitive tools will consider that data over any other assumed or set scalings\n(such as the default 1.0 or a .gr2 Add-on's importing prefs settings)",
        default = True,
    )

    # PREFERENCES UI ---------------------------------
    
    def draw(self, context):
        
        checks = requirements_checks()
        
        
        layout = self.layout


        # resources folderpath preferences UI
        pref_box = layout.box()
        
        col=pref_box.column(align=True)
        col.scale_y = Y_SCALING_INFO
        col.label(text="Path to the 'resources' folder in a SWTOR assets extraction")
        col.label(text="produced by the Slicers GUI app, EasyMYP, or any similar tool.")

        col=pref_box.column()
        col.prop(self, 'swtor_resources_dir', expand=True, )
        
        col.alert = not checks["resources"]
        col.label(text="Status: " + checks["resources_status_verbose"])



        # Custom SWTOR shaders blendfile folderpath UI
        pref_box = layout.box()
        
        col=pref_box.column(align=True)
        col.scale_y = Y_SCALING_INFO
        col.label(text="Path to a .blend file holding customizable replacement SWTOR shaders. By default,")
        col.label(text="it uses the one stored inside this Add-on. A path to a different one can be set here.")
        
        col=pref_box.column()
        col.prop(self, 'swtor_custom_shaders_blendfile_path', expand=True, )
        
        col.alert = not checks["custom_shaders"]
        col.label(text="Status: " + checks["custom_shaders_status_verbose"])

        col.operator("zgswtor.reset_custom_shaders_prefs_to_internal", text="Reset to internal Custom Shaders file")



        # SWTOR objects' scaling data usage UI
        pref_box = layout.box()

        col=pref_box.column()
        col.prop(self, 'use_gr2_scale_custom_prop', text="Use SWTOR objects' mesh scale data if available and relevant to any ZG Tool.")


# reset_custom_shaders_prefs_to_internal Operator ----
class ZGSWTOR_OT_reset_custom_shaders_prefs_to_internal(bpy.types.Operator):
    bl_idname = "zgswtor.reset_custom_shaders_prefs_to_internal"
    bl_label = "ZG Custom Shaders Reset To Internal"
    bl_options = {'REGISTER', "UNDO"}
    bl_description = "Resets the Custom Shaders .blend file Preference\nto use the file inside this Add-on's folder"

    @classmethod
    def poll(cls,context):
        checks = requirements_checks()
        if not checks["custom_shaders"]:
            return True
        else:
            return False


    def execute(self, context):
        
        # Default Custom shaders .blend file's filepath
        default_custom_shaders_blend_filepath = os.path.join(os.path.dirname(__file__), "rsrc" + os.sep + "Custom SWTOR Shaders.blend")

        context.preferences.addons["zg_swtor_tools_nx"].preferences["swtor_custom_shaders_blendfile_path"] = default_custom_shaders_blend_filepath
        
        return {"FINISHED"}
    
# ----------------------------------------------------




# Open new Preferences window aux function
def blender_prefs_with_custom_size(pref_window_width,  pref_window_height):
    # based on code by "Rombout Versluijs, Pan Beep (Beep) https://github.com/schroef.
    # See:
    # https://github.com/schroef/Custom-Preferences-Size
    # and:
    # https://projects.blender.org/blender/blender/issues/71935#818493
    
    # This sets the prefs window's dimensions and opens it,
    # but once open it sets its values back to their original settings
    # for future manual openings, as a precaution.
    
    # Modify scene settings
    render = bpy.context.scene.render
    prefs = bpy.context.preferences
    view = prefs.view
    orgResX = render.resolution_x
    orgResY = render.resolution_y
    render.resolution_x = int(pref_window_width)
    render.resolution_y = int(pref_window_height)
    orgDispMode = view.render_display_type
    view.render_display_type = "WINDOW"

    # Call image editor window
    bpy.ops.render.view_show("INVOKE_DEFAULT")

    # Change area type
    area = bpy.context.window_manager.windows[-1].screen.areas[0]
    area.type = "PREFERENCES"

    # Restore old values
    view.render_display_type = orgDispMode
    render.resolution_x = orgResX
    render.resolution_y = orgResY

# Operator to open the ZG SWTOR Tools' preferences window,
# called by addon_ui's status panel.
class ZGSWTOR_OT_open_zg_preferences(Operator):
    bl_idname = "zgswtor.open_zg_addon_preferences"
    bl_label = "ZG Open ZG SWTOR Tools Add-on's Preferences"
    bl_description = "Open ZG SWTOR Tools Add-on's Preferences"

    def execute(self, context):
        # bpy.ops.screen.userpref_show(section="ADDONS")
        
        blender_prefs_with_custom_size(640, 512)
        bpy.ops.preferences.addon_show(module="zg_swtor_tools_nx")
        return {'FINISHED'}


# Operator to open the .gr2 importer add-on's preferences window
# called by addon_ui's status panel.
class ZGSWTOR_OT_open_gr2_preferences(Operator):
    bl_idname = "zgswtor.open_gr2_addon_preferences"
    bl_label = "ZG Open .gr2 Importer Add-on's Preferences"


    def execute(self, context):
        # bpy.ops.screen.userpref_show(section="ADDONS")
        
        blender_prefs_with_custom_size(640, 512)
        bpy.ops.preferences.addon_show(module="swtor_io_tools")
        return {'FINISHED'}


    

# Registrations

def register():
    bpy.utils.register_class(addonPreferences)
    bpy.utils.register_class(ZGSWTOR_OT_reset_custom_shaders_prefs_to_internal)
    
    bpy.utils.register_class(ZGSWTOR_OT_open_zg_preferences)
    bpy.utils.register_class(ZGSWTOR_OT_open_gr2_preferences)


def unregister():
    bpy.utils.unregister_class(ZGSWTOR_OT_open_gr2_preferences)
    bpy.utils.unregister_class(ZGSWTOR_OT_open_zg_preferences)

    bpy.utils.unregister_class(ZGSWTOR_OT_reset_custom_shaders_prefs_to_internal)
    bpy.utils.unregister_class(addonPreferences)

if __name__ == "__main__":
    register()
    
