import bpy
import addon_utils
from pathlib import Path
import os



ADDON_ROOT = Path(__file__).resolve().parent



def requirements_checks():
    '''
    Returns a dict with both boolean and string reports on the existence
    and validity of some resources necessary for certain tools to work
    '''
    
    checks = {}



    # -----------------------------
    # Blender version checks

    blender_version_major_number, blender_version_minor_number , _ = bpy.app.version
    checks["blender_version"] = float(str(blender_version_major_number) + "." + str(blender_version_minor_number))
    checks["blender_version_status"] = bpy.app.version
    checks["blender_version_status_verbose"] = bpy.app.version




    # -----------------------------
    # SWTOR IO Tools Add-on checks
    is_installed = any( mod.__name__ == "swtor_io_tools" for mod in addon_utils.modules(refresh=True) )
    
    if not is_installed:
        checks["swtor_io_tools"] = False
        checks["swtor_io_tools_status"] = "NOT INSTALLED"
        checks["swtor_io_tools_status_verbose"] = "NOT INSTALLED. SWTOR IO Tools Add-on isn't installed."
    else:
        # addon_utils.check() returns a tuple of bools:
        # (add-on is enabled by default, add-on is enabled right now).
        # It doesn't check for its existence, hence the previous conditional above.
        if addon_utils.check("swtor_io_tools")[1]:
            checks["swtor_io_tools"] = True
            checks["swtor_io_tools_status"] = "ENABLED"
            checks["swtor_io_tools_status_verbose"] = "ENABLED. SWTOR IO Tools Add-on is installed and enabled."
        else:
            checks["swtor_io_tools"] = False
            checks["swtor_io_tools_status"] = "DISABLED"
            checks["swtor_io_tools_status_verbose"] = "DISABLED. SWTOR IO Tools Add-on is installed, but still needs to be enabled."



    # -----------------------------
    # 'resources' folder checks

    if checks["swtor_io_tools"] == False:

        checks["resources"] = False
        checks["resources_status"] = "NOT SET"
        checks["resources_status_verbose"] = "NOT SET. No SWTOR IO Tools is enabled to set it."

        checks["legacy_resources"] = False
        checks["legacy_resources_status"] = "NOT SET"
        checks["legacy_resources_status_verbose"] = "NOT SET. No SWTOR IO Tools is enabled to set it."

    else:
        swtor_resources_dir = getattr(bpy.context.preferences.addons["swtor_io_tools"].preferences, "swtor_resources_dir", "")
        is_badly_written = os.sep not in swtor_resources_dir
        is_unfilled = swtor_resources_dir == ""
        is_a_folder = Path(swtor_resources_dir).exists()
        is_a_resources_folder = ( Path(swtor_resources_dir) / "art/shaders/materials").exists()

        checks["resources"] = is_a_resources_folder
        
        if is_unfilled:
            checks["resources"] = False
            checks["resources_status"] = "NOT SET"
            checks["resources_status_verbose"] = "NOT SET."
        else:
            if is_badly_written:
                checks["resources"] = False
                checks["resources_status"] = "NOT VALID"
                checks["resources_status_verbose"] = "NOT VALID. This is not a folder path."
            else:
                if is_a_resources_folder:
                    checks["resources"] = True
                    checks["resources_status"] = "SET"
                    checks["resources_status_verbose"] = "SET. This is a valid 'resources' folder."
                else:
                    if is_a_folder:
                        checks["resources"] = False
                        checks["resources_status"] = "NOT VALID"
                        checks["resources_status_verbose"] = "NOT VALID. This folder isn't a valid 'resources' directory root."
                    else:
                        checks["resources"] = False
                        checks["resources_status"] = "NOT FOUND"
                        checks["resources_status_verbose"] = "NOT FOUND. No folder can't be found at the specified path."




        swtor_legacy_resources_dir = getattr(bpy.context.preferences.addons["swtor_io_tools"].preferences, "swtor_legacy_resources_dir", "")
        is_badly_written = os.sep not in swtor_legacy_resources_dir
        is_unfilled = swtor_legacy_resources_dir == ""
        is_a_folder = Path(swtor_legacy_resources_dir).exists()
        is_a_resources_folder = ( Path(swtor_legacy_resources_dir) / "art/shaders/materials").exists()
        is_a_legacy_resources_folder = not ( Path(swtor_legacy_resources_dir) / "art/dynamic/player_character/head/texture/___psd/modernization").exists()

        checks["legacy_resources"] = is_a_legacy_resources_folder
        
        if is_unfilled:
            checks["legacy_resources"] = False
            checks["legacy_resources_status"] = "NOT SET"
            checks["legacy_resources_status_verbose"] = "NOT SET."
        else:
            if is_badly_written:
                checks["legacy_resources"] = False
                checks["legacy_resources_status"] = "NOT VALID"
                checks["legacy_resources_status_verbose"] = "NOT VALID. This is not a folder path."
            else:
                if is_a_resources_folder:
                    checks["legacy_resources"] = True
                    checks["legacy_resources_status"] = "SET"
                    checks["legacy_resources_status_verbose"] = "SET. This is a valid 'resources' folder."
                    if is_a_legacy_resources_folder:
                        checks["legacy_resources"] = True
                        checks["legacy_resources_status"] = "SET"
                        checks["legacy_resources_status_verbose"] = "SET. This is a valid Legacy 'resources' folder."
                    else:
                        checks["legacy_resources"] = False
                        checks["legacy_resources_status"] = "NOT LEGACY"
                        checks["legacy_resources_status_verbose"] = "NOT LEGACY. This 'resources' folder lacks Legacy assets."
                else:
                    if is_a_folder:
                        checks["legacy_resources"] = False
                        checks["legacy_resources_status"] = "NOT VALID"
                        checks["legacy_resources_status_verbose"] = "NOT VALID. This folder isn't a valid 'resources' directory root."
                    else:
                        checks["legacy_resources"] = False
                        checks["legacy_resources_status"] = "NOT FOUND"
                        checks["legacy_resources_status_verbose"] = "NOT FOUND. No folder can't be found at the specified path."

    # -----------------------------
    # custom shaders checks
    # THIS BLOCK WILL NEED RETHINKING depending on whether 3rd party custom shaders will be allowed
    # (will require restoring the option in addon_pref's UI). See conditional in line 98 for current
    # temporary solution.

    # Default one
    default_custom_shaders_blend_filepath = os.path.join(ADDON_ROOT, "addon_resources", "Custom SWTOR Shaders.blend")

    # Current one
    if "zg_swtor_tools_nx" in bpy.context.preferences.addons:
        custom_shaders_blend_filepath = getattr(bpy.context.preferences.addons["zg_swtor_tools_nx"].preferences, "swtor_custom_shaders_blendfile_path", "")
    else:
        custom_shaders_blend_filepath = default_custom_shaders_blend_filepath
        
    blend_file_badly_written = (".blend" not in custom_shaders_blend_filepath or os.sep not in custom_shaders_blend_filepath)
    blend_file_exists = Path(custom_shaders_blend_filepath).is_file()
    blend_file_is_internal = (custom_shaders_blend_filepath == default_custom_shaders_blend_filepath)

    # Check .blend file's insides for a custom Garment shader to validate it:
    # (see https://devtalk.blender.org/t/traverse-blend-file-to-get-list-of-collections/10348/14 
    # the '_' avoids actually loading anything )
    if blend_file_exists:
        blend_file_is_valid = True
        # blend_file_is_valid = False
        # node_groups_names = None
        # with bpy.data.libraries.load(custom_shaders_blend_filepath) as (data_from, _):
        #     return node_groups_names in data_from.node_groups
        
        # blend_file_is_valid = "SWTOR - Garment Shader" in node_groups_names
    else:
        blend_file_is_valid = False

    checks["custom_shaders"] = blend_file_exists

    if blend_file_exists:
        if blend_file_is_valid:
            checks["custom_shaders"] = True
            if blend_file_is_internal:
                checks["custom_shaders_status"] = "INTERNAL"
                checks["custom_shaders_status_verbose"] = "INTERNAL. Uses the Custom SWTOR Shaders .blend file inside the Add-on."
            else:
                checks["custom_shaders_status"] = "EXTERNAL"
                checks["custom_shaders_status_verbose"] = "EXTERNAL. Uses a Custom SWTOR Shaders .blend file outside the Add-on."
        else:
            checks["custom_shaders"] = False
            checks["custom_shaders_status"] = "NOT VALID"
            checks["custom_shaders_status_verbose"] = "NOT VALID. This .blend file doesn't contain valid Custom SWTOR Shaders."
    else:
        if blend_file_badly_written:
            checks["custom_shaders"] = False
            checks["custom_shaders_status"] = "NOT VALID"
            checks["custom_shaders_status_verbose"] = "NOT VALID. This is not a .blend file path."
        else:
            checks["custom_shaders"] = False
            checks["custom_shaders_status"] = "NOT FOUND"
            checks["custom_shaders_status_verbose"] = "NOT FOUND. No .blend file can't be found at the specified path."


    return checks