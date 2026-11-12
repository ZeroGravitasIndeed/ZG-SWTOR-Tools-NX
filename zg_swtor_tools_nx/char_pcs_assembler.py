'''
Assembler of SWTOR Player Characters in their underwear

Pending: see if https://b3d.interplanety.org/en/dynamically-setting-the-max-and-min-values-%E2%80%8B%E2%80%8Bfor-a-custorm-property-in-the-blender-python-api/
can be used for dynamic sliders limits setting.
'''

import bpy
from bpy.props import IntProperty, EnumProperty, PointerProperty, StringProperty, BoolProperty
from bpy.types import Operator, PropertyGroup

from bpy.path import ensure_ext
from bpy_extras.io_utils import ExportHelper

import zipfile

import xml.etree.ElementTree as ET
import json

import os
from pathlib import Path
import shutil



from .addon_checks import requirements_checks


# #############################################################################
# SOME GLOBAL CONSTANTS AND VARIABLES:
# region ######################################################################

# Add-on's folder for diverse auxilliary data (Jedipedia, PugTools, etc.).
ADDON_RESOURCES  = Path(__file__).resolve().parent / "addon_resources"
ADDON_TEMP_FILES = Path(__file__).resolve().parent / "addon_temp_files"

# Holder for loaded SWTOR data resources stored in this add-on's subfolders.
_SWTOR_DATA = {}

# Mapping from [gen][bodytype] to body type codes.
_BODYTYPE_CODES = {
    'm1':'bma',
    'm2':'bmn',
    'm3':'bms',
    'm4':'bmf',
    'f1':'bfa',
    'f2':'bfn',
    'f3':'bfs',
    'f4':'bfb',
    }

# Names of the Character Creator's sliders.
_SLIDERS_NAMES = (
    'appSlotHead',
    'appSlotAge',
    'appSlotComplexion',
    'appSlotEyeColor',
    'appSlotFaceHair',
    'appSlotFacePaint',
    'appSlotHair',
    'appSlotHairColor',
    'appSlotSkinColor',
)

# endregion ###################################################################






# #############################################################################
# MINOR UTILITY FUNCTIONS
# region ######################################################################

def open_xml_file(file_path):
    """
    Function to open and parse an XML file.
    Handles exceptions like FileNotFoundError, PermissionError, and ET.ParseError.

    Parameters:
        file_path (str): The path to the XML file to be opened.

    Returns:
        ElementTree.Element: The root element of the XML document if the file is successfully opened.
        None: If any exception occurs during the process.
        
    Requires: import xml.etree.ElementTree as ET
    """

    try:
        # Open the XML file
        tree = ET.parse(file_path)
        # Get the root element of the XML document
        root = tree.getroot()
        # print(f"XML file '{file_path}' opened successfully.")
        return root
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        return None
    except PermissionError:
        print(f"Error: Permission denied to read the file '{file_path}'.")
        return None
    except ET.ParseError:
        print(f"Error: The file '{file_path}' is not a valid XML file.")
        return None



def delete_collection_recursive(collection):
    """
    Delete a collection, all of its child collections, and all objects
    contained in them.

    Objects linked to multiple collections are fully removed from the
    file (not just unlinked from this hierarchy).
    """

    # Recurse into children first. Iterate over a copy of the list because
    # removing a child modifies collection.children during iteration.
    for child in list(collection.children):
        delete_collection_recursive(child)

    # Remove every object in this collection. Iterate over a copy because
    # removing an object modifies collection.objects during iteration.
    for obj in list(collection.objects):
        # do_unlink=True unlinks the object from all collections/scenes
        # before deleting its data-block.
        bpy.data.objects.remove(obj, do_unlink=True)

    # Finally remove the now-empty collection data-block.
    # This also unlinks it from any parent collection or scene.
    bpy.data.collections.remove(collection)

# endregion ###################################################################






# #############################################################################
# SWTOR-RELATED AUXILLIARY FUNCTIONS
# region ######################################################################

# -----------------------------------------------------------------------------
# Loader function of all SWTOR data resources needed (nodes, texts, etc.)
# that will fill _SWTOR_DATA
# -----------------------------------------------------------------------------

def load_swtor_bundled_data():
    '''
    Loads any needed SWTOR data in this add-on's addon_resources subfolder
    to the _SWTOR_DATA "constant".
    '''
    print('Start loading SWTOR JSON data')
    
    checks = requirements_checks()
    
    global _SWTOR_DATA

    if not _SWTOR_DATA:

        # Load pcs nodes exported by PugTools' Node Browser
        print('Loading pcs nodes')
        pcs_nodes = {}
        zip_path = ADDON_RESOURCES / "pcs_nodes.zip"
        with zipfile.ZipFile(zip_path, "r") as archive:
            for file_path in archive.namelist():
                with archive.open(file_path) as file:
                    data = json.load(file)
                if "name" in data:
                    key = data["name"]
                    pcs_nodes[key] = data["data"]
            _SWTOR_DATA['pcs_nodes'] = pcs_nodes

        # Load legacy pcs nodes exported by PugTools' Node Browser.
        # As it is not that costly, I'm loading them no matter if
        # there is no legacy folder selected. That avoids the issue
        # of having to call this function if a legacy folder is
        # assigned in IO Tools in the middle of a session.
        print('Loading legacy pcs nodes')
        pcs_nodes = {}
        zip_path = ADDON_RESOURCES / "legacy_pcs_nodes.zip"
        with zipfile.ZipFile(zip_path, "r") as archive:
            for file_path in archive.namelist():
                with archive.open(file_path) as file:
                    data = json.load(file)
                if "name" in data:
                    key = data["name"]
                    pcs_nodes[key] = data["data"]
            _SWTOR_DATA['legacy_pcs_nodes'] = pcs_nodes



        # Load dynamic nodes exported by PugTools' Node Browser
        print('Loading dynamic nodes')
        dynamic_nodes = {}
        zip_path = ADDON_RESOURCES / "dynamic_nodes.zip"
        with zipfile.ZipFile(zip_path, "r") as archive:
            for file_path in archive.namelist():
                with archive.open(file_path) as file:
                    data = json.load(file)
                if "name" in data:
                    key = data["name"]
                    dynamic_nodes[key] = data["data"]
            _SWTOR_DATA['dynamic_nodes'] = dynamic_nodes
        
        # Load legacy dynamic nodes exported by PugTools' Node Browser.
        # As it is not that costly, I'm loading them no matter if
        # there is no legacy folder selected. That avoids the issue
        # of having to call this function if a legacy folder is
        # assigned in IO Tools in the middle of a session.
        print('Loading legacy dynamic nodes')
        dynamic_nodes = {}
        zip_path = ADDON_RESOURCES / "legacy_dynamic_nodes.zip"
        with zipfile.ZipFile(zip_path, "r") as archive:
            for file_path in archive.namelist():
                with archive.open(file_path) as file:
                    data = json.load(file)
                if "name" in data:
                    key = data["name"]
                    dynamic_nodes[key] = data["data"]
            _SWTOR_DATA['legacy_dynamic_nodes'] = dynamic_nodes
            
            
            
        # Load pcs strings (for labelling the sliders.
        # We assume they haven't changed through versions,
        # only increased in number).
        print('Loading pcs labels')
        pcs_labels = {}
        zip_path = ADDON_RESOURCES / "pcs.zip"
        with zipfile.ZipFile(zip_path, "r") as archive:
            with archive.open("pcs.json") as file:
                pcs_labels = json.load(file)
            _SWTOR_DATA['pcs_labels'] = pcs_labels




    print('SWTOR data loaded')
    

def load_swtor_xml_data():
    # Preload index.xml files to avoid constantly re-opening and re-parsing them
    # The SWTOR IO Tools add-on is assumed to be installed and enabled, as this
    # tool isn't allowed to be run without it.

    print("Loading index.xml files data once")
    
    swtor_io_tools_prefs = bpy.context.preferences.addons["swtor_io_tools"].preferences
    swtor_resources_dir = getattr(swtor_io_tools_prefs, "swtor_resources_dir")

    _SWTOR_DATA['root_xml_skincolor']   = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/skincolor/index.xml')  )
    _SWTOR_DATA['root_xml_eyecolor']    = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/eyecolor/index.xml')   )
    _SWTOR_DATA['root_xml_haircolor']   = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/haircolor/index.xml')  )
    _SWTOR_DATA['root_xml_age']         = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/age/index.xml')        )
    _SWTOR_DATA['root_xml_complexion']  = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/complexion/index.xml') )
    _SWTOR_DATA['root_xml_facepaint']   = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/facepaint/index.xml')  )
    _SWTOR_DATA['root_xml_head']        = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/head/index.xml')       )
    _SWTOR_DATA['root_xml_hair']        = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/hair/index.xml')       )
    _SWTOR_DATA['root_xml_facehair']    = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/facehair/index.xml')   )







def get_matfile_data(mat_filepath):
    '''
    Open XML material .mat file and return all its material inputs.
    Includes also a few basic ones(Derived, AlphaMode, and AlphaTestValue).
    '''
    
    root = open_xml_file(mat_filepath)
    
    # We will store all data in the .mat file as a flat dict
    mat_inputs = {}
    
    mat_inputs['Derived']           = root.find("Derived").text
    mat_inputs['AlphaMode']         = root.find("AlphaMode").text
    mat_inputs['AlphaTestValue']    = root.find("AlphaTestValue").text


    for element in root.findall("./input"):
        elem_semantic =  element.find("semantic").text
        elem_type =      element.find("type").text
        elem_value =     element.find("value").text
        elem_variable =  element.find("variable").text
        
        if elem_type == "texture" and elem_value:
            elem_value = elem_value.replace("\\", "/")
            if elem_value[0:1] != "/":
                elem_value = f"/{elem_value}"
            if elem_variable:
                elem_variable = elem_variable.replace("\\", "/")
                if elem_variable[0:1] != "/":
                    elem_variable = f"/{elem_variable}"

                
        # This is a specific need for conversion to JSON
        # involving mixing dynamic node data values which
        # have vectors' components pre-separated and labelled. 
        if elem_type in ['rgb','rgba','vector4']:
            elem_value = elem_value.split(",")
            if elem_variable:
                elem_variable = elem_variable.split(",")

        # store element
        mat_inputs[elem_semantic] = {
            "type":     elem_type,
            "value":    elem_value,
            "variable": elem_variable,
        }

    # Set Neutral maps for these cases (just in case a parser complains).
    if not ('UsesFur' in mat_inputs and mat_inputs['UsesFur'] == "True"):
        mat_inputs['DirectionMap'] = {'value': "/art/defaultassets/black.dds"}
        
    if not ('UsesAnimatedWrinkles' in mat_inputs and mat_inputs['UsesAnimatedWrinkles'] == "True"):
        mat_inputs['animatedWrinkleMap']  = {'value': "/art/defaultassets/flat_w.dds"}
        mat_inputs['animatedWrinkleMask'] = {'value': "/art/defaultassets/flat_w.dds"}
    
    return mat_inputs
    

def merge_mat_dynamic_node_data(matfile_data, dynamic_node_data, skinmaterialindex=0):
    '''
    Merges dynamic nodes data with .mat data's "otherValues" section,
    based on passed SkinMaterialIndex data.
    
    WE ARE ASSUMING SINGLE PALETTE RE-HUEING HERE. DOUBLE PALETTE RE-HUEING
    (TYPICAL FOR GARMENTS, THAT WE AREN'T DOING) WILL REQUIRE RETHINKING IT.
    
    ABOUT SkinMaterialIndex:
    If it's set to -1, the model has no skin, aka no material should be replaced by the skin material. If it's set to 1, then the material at index #1 (second material) must be replaced. If the field is missing, then it's set to 0, aka the material at index #0 (first material) must be replaced.
    
    *  0 - Field is missing (default value 0) = replace material #0 (primary) with skin material.
    
    *  1 - Field is set to 1 = replace material #1 (secondary) with skin material.
    
    * -1 - Field is set to -1 = do not replace any materials with skin material.
    
    AN ISSUE IS THAT THE INPUT NAME IN TORC'S PATHS.JSON FILES IS MISTYPED: MATERIALSKININDEX.
    Given that, I'm keeping the wrong name in the JSON data this module emits. I'm also testing
    adding it to all body parts to see if the SWTOR IO Tools add-on can handle it (current
    Jedipedia JSON exports seem to omit the datum, but creature-type NPCs might require it).
    
    
    THERE IS ALSO SkinHueIndex:
    Determines which material index gets hued with dynamic skincolors
    * -1 - No skin (the most usual)
    *  1 - Seems to be the only other value happening.
    '''
    
    # DYNAMIC NODES ARE A MESS:
    # - They contain key:values ONLY for what changes in a material.
    # - appPalette data is decomposed into these key:values:
    #     appPaletteHue
    #     appPaletteSaturation
    #     appPaletteContrast
    #     appPaletteBrightness
    # - BUT the rest are a mishmash:
    #     appPaletteSpecular
    #     appPaletteMetallicSpecular
    #     appPaletteCarPaintColor
    #         have 'r','g','b','a' keys:values,
    #         but only the changing ones (say, 'r' and 'a').
        
    #     appPaletteEnvMapAdjust
    #     appPaletteMetallicAdjust
    #         have simple lists of RGBA components
    #         (probably because they were new element
    #         without previous .mat default inputs?).
    
    
    # Prepare a numbered "palette" string  
    if skinmaterialindex in [0, "0", "", None]:
        palette_prefix = "palette1"
    elif skinmaterialindex in [1, "1"]:
        palette_prefix = "palette2"
    elif skinmaterialindex in [-1, "-1"]:
        return matfile_data


    for key,value in dynamic_node_data.items():
        if not key.startswith('app'):
            continue
            
        elif key == 'appPaletteHue':
            matfile_data[palette_prefix]['value'][0] = str(value)
        elif key == 'appPaletteSaturation':
            matfile_data[palette_prefix]['value'][1] = str(value)
        elif key == 'appPaletteBrightness':
            matfile_data[palette_prefix]['value'][2] = str(value)
        elif key == 'appPaletteContrast':
            matfile_data[palette_prefix]['value'][3] = str(value)

        
        elif key == 'appPaletteSpecular':
            input_name = palette_prefix + "Specular"
            if 'r' in value:
                matfile_data[input_name]['value'][0] = str(value['r'])
            if 'g' in value:
                matfile_data[input_name]['value'][1] = str(value['g'])
            if 'b' in value:
                matfile_data[input_name]['value'][2] = str(value['b'])


        elif key == 'appPaletteMetallicSpecular':
            input_name = palette_prefix + "MetallicSpecular"
            if 'r' in value:
                matfile_data[input_name]['value'][0] = str(value['r'])
            if 'g' in value:
                matfile_data[input_name]['value'][1] = str(value['g'])
            if 'b' in value:
                matfile_data[input_name]['value'][2] = str(value['b'])
            
        # We aren't doing appPaletteCarPaintColor and related because
        # we don't know yet what they correlate to in .mat data.
            

    return matfile_data



def process_wildcards(string, bodytype_code):
    '''
    Replaces bodytype and gender wildcards
    with values derived from the bodytype code.
    '''
    string = string.replace('[bt]', bodytype_code)
    string = string.replace('[gen]', bodytype_code[1:2])
    
    return string
    
# endregion ###################################################################






# #############################################################################
# MAIN SWTOR NODE PROCESSING FUNCTIONS
# region ######################################################################

# -----------------------------------------------------------------------------
# Character data to ami IDs processor
# -----------------------------------------------------------------------------

def parse_pcs_node_and_sliders(self, context):
    '''
    Process set of Player Character's slider settings.
    '''
    # (It's not taking advantage of self right now. Investigate possibilities)

    # SWTOR DATA PROCESSING
    # region

    # How to obtain the appPcsCustomizationSlots IDs that provide ModelIDs, Attachment models, and MaterialIndex for each head attribute (model, complexion, etc):
    # - Compose a FQN out of class, gender, and species selection, and load the node with that FQN.
    # - In appPcsHeadSkeletonMap -> bodyType, select the ID whose position in the list matches the head slider's value.
    # - To get the head model and material iDs, use that ID in appPosCustomizationSlots.
    # - to get the rest of the head's attributes, use that ID in appPcsSliderMap to get lists for every pertinent attribute,
    #   and then get their IDs whose positions in their lists match their sliders' values. Use Those IDs in appPcsCustomizationSlots, too.

    print("processing sliders")

    # Fetch the sliders property group's values'.
    sliders         = context.scene.zgswtor_pcs_sliders
    sliders_labels  = context.scene.zgswtor_pcs_sliders_labels
    sliders_limits  = context.scene.zgswtor_pcs_sliders_limits

    # Are we using Legacy assets?
    legacy_mode = context.scene.zgswtor_pcs_legacy_mode
    if legacy_mode:
        legacy_prefix = "legacy_"
    else:
        legacy_prefix = ""



    # -------------------------------------------------------------------------
    # Adjust species in the case of Zabrak, as I've made the Empire/Republic versions
    # explicit in the menu instead of simple 'zabrak' vs. imp_legacy / rep_legacy suffixes
    # (the "_legacy" bit is solved after building the fqn during checking for the node's existence).
    species = sliders.pcs_species
    
    if "zabrak_" in species:
        if sliders.pcs_class in [
            "bounty_hunter",
            "imperial_agent",
            "sith_inquisitor",
            "sith_warrior",
        ]:
            # Empire faction
            if species == "zabrak_imp":
                species = "zabrak"
        else:
            # Republic faction
            if species == "zabrak_rep":
                species = "zabrak"


    # Build the FQN
    pcs_node_fqn = f'pcs.{sliders.pcs_class}.{sliders.pcs_gender}.{species}'
    
    # Many species can have a "_legacy" suffix depending on faction.
    # This check simplifies handling that.
    if pcs_node_fqn not in _SWTOR_DATA[legacy_prefix + 'pcs_nodes']:
        pcs_node_fqn = f'pcs.{sliders.pcs_class}.{sliders.pcs_gender}.{f"{species}_legacy"}'

    # Get the character's node
    pcs_node = _SWTOR_DATA[legacy_prefix + 'pcs_nodes'][pcs_node_fqn]




    # --------------------------------------------------------------------------------------------------
    # SEPARATE THE NODE'S DATA INTO TRACTABLE PIECES:
    # --------------------------------------------------------------------------------------------------

    # ----------------------------------
    # DATA THAT LEADS TO CUSTOMIZATIONS:
    # ----------------------------------

    # List of body tipes' IDs., in a fixed order: BxA, BxN, BxS, BxF/B.
    appPcsSkeletonDisplayList = pcs_node['appPcsSkeletonDisplayList']
    
    bt_ids = {
        '1':appPcsSkeletonDisplayList[0],  # bt1 (bma / bfa)
        '2':appPcsSkeletonDisplayList[1],  # bt2 (bmn / bfn)
        '3':appPcsSkeletonDisplayList[2],  # bt3 (bms / bfs)
        '4':appPcsSkeletonDisplayList[3],  # bt4 (bmf / bfb) 
    }

    # list of body types' sublists of head objects's appPcsCustomizationSlots.
    # They aren't in a fixed order: we'll use appPcsSkeletonDisplayList's IDs to get them by their body types.
    appPcsHeadSkeletonMap = pcs_node['appPcsHeadSkeletonMap']
    #       Auxilliary dict to be able to select the appPcsHeadSkeletonMap items per appPcsSkeletonDisplayList body type key.
    appPcsHeadSkeletonMap_indexed = {elem['key']:elem for elem in appPcsHeadSkeletonMap}
    
    
    # List of pertinent sliders and each of their positions'appPcsCustomizationSlots' IDs.
    # The ID to use matches the one for the head selection at appPcsHeadSkeletonMap.
    appPcsSliderMap = pcs_node['appPcsSliderMap']                 


    # List of all appearance entries' in the pcs node (with final Models and materials IDs, etc.)
    # that all our pcs node traversing and selecting will ultimately lead to.
    appPcsCustomizationSlots = pcs_node['appPcsCustomizationSlots']
    #       Auxilliary dict to make appPcsHeadSkeletonMap lookups faster.
    appPcsCustomizationSlots_indexed = {elem['key']:elem for elem in appPcsCustomizationSlots}

    # -------------------------------
    # SLIDER LABELS DATA FOR THE GUI:
    # -------------------------------

    # List of sliders' UI strings' IDs that map to the pcs.zip file (JSONized pcs.stb). 
    appPcsCustomizationSlotNameIds = pcs_node['appPcsCustomizationSlotNameIds']
    #       Auxilliary dict to make appPcsCustomizationSlotNameIds lookups faster.
    appPcsCustomizationSlotNameIds_indexed = {elem['key']:elem for elem in appPcsCustomizationSlotNameIds}
    
    # --------------------------------------------------------------------------------------------------





    # Clear slider_labels. They will be refilled with
    # only the ones for the chosen class/gender/species.
    # Unlabelled sliders will be hidden by the GUI.
    for slider_name in _SLIDERS_NAMES:
        setattr(sliders_labels, slider_name, "")



    # GATHERING THE AMI NODES (INDEX.XML FILES) DATA
    # We are using the index.xml versions of those nodes
    # that exist in the assets extraction, to avoid
    # having to store yet more JSON data in the add-on.

    # We'll store the appPcsCustomizationSlots' IDs here:
    ami_ids = {}
    # and their data here:
    ami_data = {}
    

    # HEAD SLIDER PROCESSING
    
    # List of ami IDs asociated to this node and bodytype's heads        
    list_of_customization_ids_for_head_slider = appPcsHeadSkeletonMap_indexed[ bt_ids[str(sliders.pcs_bodytype)] ] ['value']
    
    
    # Get head slider values' upper limit.
    # CHECK IF THIS IS STILL NEEDED, GIVEN THE SLIDERS' CALLBACK FUNCTIONS
    sliders_limits['appSlotHead'] = len(list_of_customization_ids_for_head_slider)
    # Set value down to highest if exceeded.
    if getattr(sliders, 'appSlotHead') > sliders_limits['appSlotHead']:
        setattr(sliders, 'appSlotHead', sliders_limits['appSlotHead'])
        

    # Get the head's appPcsCustomizationSlots ID.
    ami_ids['appSlotHead']  = list_of_customization_ids_for_head_slider[int( sliders.appSlotHead ) - 1]
    # ami_ids['appSlotHead']  = list_of_customization_ids_for_head_slider[sliders.pcs_bodytype - 1]
    ami_data['appSlotHead'] = appPcsCustomizationSlots_indexed[ ami_ids['appSlotHead'] ]



    # REST OF THE SLIDERS PROCESSING

    # Use the head slot's ID to find in appPcsSliderMap the relevant list of other slots
    # (IT ONLY CONTAINS THE SLOTS ACTUALLY IN USE FOR THE SPECIES AND GENDER).
    # Instead of using an aux indexed dict version of this list, it is cheaper to loop through it
    # as it is only used once (if we make this add-on interactive that could change).
    for elem in appPcsSliderMap:
        if elem['key'] == ami_ids['appSlotHead']:
            existing_slots = elem['value']
            # (Create an aux indexed dict version of this existing_slots list,
            # as we would have to loop through it several times otherwise).
            existing_slots_indexed = {elem['key']:elem['value'] for elem in existing_slots}
            break

    
    # With the list of slots we get the lists of appPcsCustomizationSlots ID each of those hold.
    for slider_name in _SLIDERS_NAMES:
        if slider_name in existing_slots_indexed:
            list_of_customization_ids_for_head_slider = existing_slots_indexed[slider_name]
            
            # Get max slider values' limits and set slider to max if exceeded.
            sliders_limits[slider_name] = len(list_of_customization_ids_for_head_slider)
            if getattr(sliders, slider_name) > sliders_limits[slider_name]:
                setattr(sliders, slider_name, sliders_limits[slider_name])

            # Get ami data
            ami_ids[slider_name]  = list_of_customization_ids_for_head_slider[ int(getattr(sliders, slider_name)) - 1 ]
            ami_data[slider_name] = appPcsCustomizationSlots_indexed[ ami_ids[slider_name] ]

            
            # LABELLING OF THE SLIDERS HAPPENS HERE:
            slider_label = _SWTOR_DATA["pcs_labels"][ str(appPcsCustomizationSlotNameIds_indexed[slider_name]['value']) ]
            setattr(sliders_labels, slider_name, slider_label)
        else:
            setattr(sliders_labels, slider_name, "")
            
    # Don't forget to label the head.
    slider_label = _SWTOR_DATA["pcs_labels"][ str(appPcsCustomizationSlotNameIds_indexed["appSlotHead"]['value']) ]
    setattr(sliders_labels, "appSlotHead", slider_label)


    # endregion
    
    # JSON DATA EXPORT
    # region
    # Build a paths.json file compatible with the existing char assembler add-ons.

    bodytype_code = _BODYTYPE_CODES[ f"{sliders.pcs_gender[0:1]}{sliders.pcs_bodytype}" ]


    # endregion
    return ami_data, bodytype_code, pcs_node_fqn


# DOESN'T SEEM TO BE NECESSARY
# def _run_pcs_assembler_operator_once_after_register():
#     '''
#     Launches this module's process_pcs operator once
#     after registering the module's operators and properties
#     in order to show valid sliders values, labels, and limits
#     on add-on enable.
#     '''
#     return
#     # Make sure Blender has a valid context before invoking.
#     try:
#         bpy.ops.zgswtor.pcs_assembler()
#     except RuntimeError as e:
#         print(f"Could not run main operator: {e}")

#     # Returning None means: don't run this timer again.
#     return None




# -----------------------------------------------------------------------------
# Character ami IDs to assets to JSON processor
# -----------------------------------------------------------------------------

def process_pcs_data(self, context, ami_data, bodytype_code, pcs_node_fqn):
    '''
    Convert ami nodes' IDs data to paths.json data
    (we are using the index.xml versions of those nodes)
    '''
    
    '''
    NOTE: ABOUT MATERIALS IN THE AMI SYSTEM (AMI NODES/INDEX.XML FILES) AND SkinMaterialIndex.
    If it's set to -1, the model has no skin, aka no material should be replaced by the skin material. If it's set to 1, then the material at index #1 (second material) must be replaced. If the field is missing, then it's set to 0, aka the material at index #0 (first material) must be replaced.
    
    E.g. in ami.chest:
    2533911: field is missing (default value 0) = replace material #0 with skin material
    3089413 field is set to 1 = replace material #1 with skin material
    1142781: field is set to -1 = do not replace any materials with skin material
    
    AN ISSUE IS THAT THE INPUT NAME IN TORC'S PATHS.JSON FILES IS MISTYPED: MaterialSkinIndex.
    Given that, I'm keeping the wrong name in the JSON data this module emits. I'm also testing
    adding it to all body parts to see if the SWTOR IO Tools add-on can handle it (current
    Jedipedia JSON exports seem to omit the datum, but creature-type NPCs might require it).
    '''
    
    
    print("processing character's data")
    
    

    # ALL DYNAMIC NODES DATA IS ALREADY LOADED IN ADDON_RESOURCES["dynamic"]

    # This preloads all index.xml data    
    if not 'root_xml_head' in _SWTOR_DATA:
        load_swtor_xml_data()

    
    swtor_io_tools_prefs = bpy.context.preferences.addons["swtor_io_tools"].preferences
    
    swtor_resources_dir = getattr(swtor_io_tools_prefs, "swtor_resources_dir")
    swtor_legacy_resources_dir = getattr(swtor_io_tools_prefs, "swtor_legacy_resources_dir")
    
    # Are we using Legacy assets?
    legacy_mode = context.scene.zgswtor_pcs_legacy_mode
    if legacy_mode:
        legacy_prefix = "legacy_"
        swtor_resources_variable_folderpath = swtor_legacy_resources_dir
    else:
        legacy_prefix = ""
        swtor_resources_variable_folderpath = swtor_resources_dir


    print(pcs_node_fqn)
    
    gender_code   = bodytype_code[1:2]


    char_data = {}
    
    
    
    # PROCESS SLOTS WITH ONLY COLORS (WHICH REQUIRE READING THE DYNAMIC NODES)
    # -----------------------------------------------------------------------------
    # THESE HAVE AS BASE FILES THE DYNAMIC NODES FOR RE-HUEING THE SKIN/HAIR/FACEHAIR SKINMATERIALS
    # region
    
    # Process appSlotSkinColor (this skin color will be applied to all SkinMats, save for the secondary hair "skin")
    if 'appSlotSkinColor' not in ami_data:
        dynamic_skincolor = ""
    else:
        data = ami_data['appSlotSkinColor']['value']
        appAppearanceSlotModelID = data['appAppearanceSlotModelID']
        
        # root_xml_skincolor = open_xml_file(os.path.normpath( f"{swtor_resources_dir}art/dynamic/skincolor/index.xml"))
        asset = _SWTOR_DATA['root_xml_skincolor'].find(f"./Asset[ID='{appAppearanceSlotModelID}']")
        
        basefile = asset.find('BaseFile').text
        node_name = f'dynamic.skincolor.{os.path.splitext(os.path.basename(basefile))[0]}'
        
        dynamic_skincolor = _SWTOR_DATA[legacy_prefix + 'dynamic_nodes'][node_name]


    # Process appSlotEyeColor
    if 'appSlotEyeColor' not in ami_data:
        dynamic_eyecolor = ""
    else:
        data = ami_data['appSlotEyeColor']['value']
        appAppearanceSlotModelID = data['appAppearanceSlotModelID']
        
        # root_xml_eyecolor = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/eyecolor/index.xml') )
        asset = _SWTOR_DATA['root_xml_eyecolor'].find(f"./Asset[ID='{appAppearanceSlotModelID}']")
        
        basefile = asset.find('BaseFile').text
        node_name = f'dynamic.eyecolor.{os.path.splitext(os.path.basename(basefile))[0]}'
        
        dynamic_eyecolor = _SWTOR_DATA[legacy_prefix + 'dynamic_nodes'][node_name]
    
    
    # Process appSlotHairColor
    if 'appSlotHairColor' not in ami_data:
        dynamic_haircolor = ""
    else:
        data = ami_data['appSlotHairColor']['value']
        appAppearanceSlotModelID = data['appAppearanceSlotModelID']
        
        # root_xml_haircolor = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/haircolor/index.xml') )
        asset = _SWTOR_DATA['root_xml_haircolor'].find(f"./Asset[ID='{appAppearanceSlotModelID}']")
        
        basefile = asset.find('BaseFile').text
        node_name = f'dynamic.haircolor.{os.path.splitext(os.path.basename(basefile))[0]}'
        
        dynamic_haircolor = _SWTOR_DATA[legacy_prefix + 'dynamic_nodes'][node_name]



    # PROCESS SLOTS WITH ONLY TEXTUREMAPS (TO BE APPLIED TO THE HEAD)
    # -----------------------------------------------------------------------------

    # Process appSlotAge
    if 'appSlotAge' not in ami_data:
        age_basefile = "/art/defaultassets/default_age.dds"
    else:
        data = ami_data['appSlotAge']['value']
        appAppearanceSlotModelID = data['appAppearanceSlotModelID']
        
        # root_xml_age = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/age/index.xml') )
        asset = _SWTOR_DATA['root_xml_age'].find(f"./Asset[ID='{appAppearanceSlotModelID}']")
        
        age_basefile = asset.find('BaseFile').text


    # Process appSlotComplexion
    if 'appSlotComplexion' not in ami_data:
        complexion_basefile = "/art/defaultassets/white.dds"
    else:
        data = ami_data['appSlotComplexion']['value']
        appAppearanceSlotModelID = data['appAppearanceSlotModelID']
        
        # root_xml_complexion = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/complexion/index.xml') )
        asset = _SWTOR_DATA['root_xml_complexion'].find(f"./Asset[ID='{appAppearanceSlotModelID}']")
        
        complexion_basefile = asset.find('BaseFile').text


    # Process appSlotFacePaint
    if 'appSlotFacePaint' not in ami_data:
        facepaint_basefile = "/art/defaultassets/default_facepaint.dds"
    else:
        data = ami_data['appSlotFacePaint']['value']
        appAppearanceSlotModelID = data['appAppearanceSlotModelID']
        
        # root_xml_facepaint = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/facepaint/index.xml') )
        asset = _SWTOR_DATA['root_xml_facepaint'].find(f"./Asset[ID='{appAppearanceSlotModelID}']")
        
        facepaint_basefile = asset.find('BaseFile').text


    # endregion
    
    
    # PROCESS SLOTS WITH MODELS AND MATERIALS
    # -----------------------------------------------------------------------------

    # Process appSlotHead
    data = ami_data['appSlotHead']['value']
    appAppearanceSlotModelID	    = data['appAppearanceSlotModelID']
    appAppearanceSlotMaterialIndex  = data['appAppearanceSlotMaterialIndex']
    appAppearanceSlotAttachments	= data['appAppearanceSlotAttachments']  # Probably never used for PC heads.
    # appAppearanceSlotFxSpecs	    = data['appAppearanceSlotFxSpecs']
    # appAppearanceSlotFxData         = data['appAppearanceSlotFxData']


    # root_xml_head = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/head/index.xml') )
    asset = _SWTOR_DATA['root_xml_head'].find( f"./Asset[ID='{appAppearanceSlotModelID}']" )
    
    # Base head model
    head_models = [asset.find("BaseFile").text]  # models accumulate in a list


    # -------------------------------
    # Head attachments models
    attachments = asset.find("Attachments")
    if attachments:
        for attachment in attachments:
            attachment_id = attachment.get("id")
            if int(attachment_id) in appAppearanceSlotAttachments:
                attachment_path = [attachment.get("filename")]
                head_models += attachment_path
    head_models = [process_wildcards(item, bodytype_code) for item in head_models]


    # -------------------------------
    # Head material
    materials = asset.find("Materials")
    head_material = materials.find(f"./Material/[@id='{appAppearanceSlotMaterialIndex}']")
    head_material_filepath = head_material.get("filename")
    head_material_filepath = process_wildcards(head_material_filepath, bodytype_code)
    head_material_data = get_matfile_data(os.path.normpath( f'{swtor_resources_variable_folderpath}{head_material_filepath}') )
    
    head_material_index = asset.find("SkinMaterialIndex").text
    head_hue_index = asset.find("SkinHueIndex").text
    
    head_material_index = "0"  # for some resason the -1 in the data goes wrong, so…
    if dynamic_skincolor:
        head_material_data = merge_mat_dynamic_node_data(head_material_data, dynamic_skincolor, head_material_index)


    # -------------------------------
    # Skinmaterials
    # for boot, chest, hand, and leg. There might be hair (horns, etc.) depending on species:
    skinmaterials_files = {}
    skinmaterials_data = {}
    skinmaterials = asset.find("CustomData/SkinMaterials")
    for skinmaterial in skinmaterials:
        slot = skinmaterial.get("slot")
        skinmaterial_filepath = skinmaterial.get("filename")
        skinmaterial_filepath = process_wildcards(skinmaterial_filepath, bodytype_code)
        skinmaterials_files[slot] = skinmaterial_filepath
        skinmaterials_data[slot]  = get_matfile_data(os.path.normpath( f'{swtor_resources_variable_folderpath}{skinmaterial_filepath}') )
        # Merge skincolor dynamic node data
        if dynamic_skincolor:
            skinmaterials_data[slot] = merge_mat_dynamic_node_data(skinmaterials_data[slot], dynamic_skincolor)


    # -------------------------------
    # Eye material
    # Second material for heads: eye, typically.
    # The index determines if it goes in the primary or scondary material slot.
    materialoverrides = head_material.find("MaterialOverrides")
    if materialoverrides:
        eye_material = materialoverrides[0]
        eye_material_filepath = eye_material.get("filename")
        eye_material_filepath = process_wildcards(eye_material_filepath, bodytype_code)
        eye_material_data = get_matfile_data(os.path.normpath( f'{swtor_resources_variable_folderpath}{eye_material_filepath}') )
        # Merge eyecolor dynamic node data
        eye_material_index = "0"  # for some resason the -1 in the data goes wrong, so…
        if dynamic_eyecolor:
            eye_material_data = merge_mat_dynamic_node_data(eye_material_data, dynamic_eyecolor, eye_material_index)



    # -------------------------------
    # hand model and materials:
    # -------------------------------
    hand_models = ["/art/dynamic/hand/model/hand_naked_[bt]_archetype.gr2"]  # models accumulate in a list
    hand_models = [process_wildcards(item, bodytype_code) for item in hand_models]

    # Same material as hand skinmaterial, already found and re-hued in head section.
    hand_material_data = skinmaterials_data["hand"]
    hand_material_index = hand_material_data.get("SkinMaterialIndex", "0")
    # No need to re-re-hue.


    # -------------------------------
    # boot model and materials:
    # -------------------------------
    boot_models = ["/art/dynamic/boot/model/boot_naked_[bt]_archetype.gr2"]  # models accumulate in a list
    boot_models = [process_wildcards(item, bodytype_code) for item in boot_models]

    # Same material as boot skinmaterial, already found and re-hued in head section.
    boot_material_data = skinmaterials_data["boot"]
    boot_material_index = boot_material_data.get("SkinMaterialIndex", "0")
    # No need to re-re-hue.


    # -------------------------------
    # Leg models and materials:
    # -------------------------------
    # Underwear materials:
    # - Females have leg and chest underwear.
    # - Males only have leg underwear and the chest uses the chest skinmaterial.

    leg_models = ["/art/dynamic/leg/model/leg_underwear_[bt]_archetype.gr2"]  # models accumulate in a list
    leg_models = [process_wildcards(item, bodytype_code) for item in leg_models]
    
    # chest material
    leg_material_filepath = "/art/shaders/materials/leg_pantskin_non_non_a01underwear02_[gen]_v01.mat"
    leg_material_filepath = process_wildcards(leg_material_filepath, bodytype_code)
    leg_material_data = get_matfile_data(os.path.normpath( f'{swtor_resources_variable_folderpath}{leg_material_filepath}') )
    # Merge garmenthue dynamic node data
    leg_material_index = leg_material_data.get("SkinMaterialIndex", "1")
    leg_material_index = "1"  # for some resason the -1 in the data goes wrong, so…
    # leg_material_data = merge_mat_dynamic_node_data(leg_material_data, dynamic_garmenthue_1, )




    # -------------------------------
    # Chest models and materials:
    # -------------------------------
    # Underwear materials:
    # - Females have leg and chest underwear.
    # - Males only have leg underwear and the chest uses the chest skinmaterial.

    # Male chest uses skinmat materials.
    # Female chest data not derivable from PCS or others, obtained from jedipedia.net's database:
    # Basic Women's Tank
    # https://swtor.jedipedia.net/en/itm/basic-womens-tank-2
    # itm.mtx.armor.season7.female_underwear.chest
    # ipp.mtx.season7.female_underwear.chest
    # AMI / index.xml ID = 2777239
    # garmenthue (for both primary and secondary): WE ARE NOT GOING TO RE-HUE, FOR SIMPLICITY'S SAKE.
    # garmenthue_bh_h02_p.xml
    # chest_tightskin_[bt]_archetype.gr2
    # chest_tightskin_non_non_a01underwear02_f.mat
    

    if gender_code == "m":    
        chest_models = [f"/art/dynamic/chest/model/chest_naked_{bodytype_code}_archetype.gr2"]  # models accumulate in a list

        # Same material as chest skinmaterial, already found and re-hued in head section.
        chest_material_filepath = skinmaterials_files["chest"]
        chest_material_data = skinmaterials_data["chest"]
        chest_material_index = "1"  # for some resason the -1 in the data goes wrong, so…
    else:
        chest_models = [f"/art/dynamic/chest/model/chest_tightskin_{bodytype_code}_archetype.gr2"]  # models accumulate in a list

        chest_material_filepath = "/art/shaders/materials/chest_tightskin_non_non_a01underwear02_f.mat"
        chest_material_data = get_matfile_data(os.path.normpath( f'{swtor_resources_variable_folderpath}{chest_material_filepath}') )
        chest_material_index = "1"  # for some resason the -1 in the data goes wrong, so…




    # -------------------------------
    # Process appSlotHair
    # -------------------------------
    # (for zabrak horns, hair_material_index ought to be "1")
    if 'appSlotHair' not in ami_data:  # bald PCs
        hair_models = None  # This will signal to skipe adding it to the JSON data
    else:
        data = ami_data['appSlotHair']['value']
        appAppearanceSlotModelID	    = data['appAppearanceSlotModelID']
        appAppearanceSlotMaterialIndex  = data['appAppearanceSlotMaterialIndex']
        appAppearanceSlotAttachments	= data['appAppearanceSlotAttachments']  # specific attachments to use
        
        # root_xml_hair = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/hair/index.xml') )
        asset = _SWTOR_DATA['root_xml_hair'].find(f"./Asset[ID='{appAppearanceSlotModelID}']")
        
        hair_models = []  # models accumulate in a list
        
        base_file = asset.find('BaseFile').text
        if base_file:
            hair_models += [base_file]


        # -------------------------------
        # hair attachments models
        hair_attachments = asset.find("Attachments")  # all possible attachments for this hair
        if hair_attachments:
            for hair_attachment in hair_attachments:
                hair_attachment_id = hair_attachment.get("id")
                if int(hair_attachment_id) in appAppearanceSlotAttachments:
                    hair_attachment_path = [hair_attachment.get("filename")]
                    hair_models += hair_attachment_path
        hair_models = [process_wildcards(item, bodytype_code) for item in hair_models]


        # -------------------------------
        # hair material
        materials = asset.find("Materials")
        hair_material = materials.find(f"./Material/[@id='{appAppearanceSlotMaterialIndex}']")
        hair_material_filepath = hair_material.get("filename")
        hair_material_filepath = process_wildcards(hair_material_filepath, bodytype_code)
        hair_material_data = get_matfile_data(os.path.normpath( f'{swtor_resources_variable_folderpath}{hair_material_filepath}') )
        hair_material_index  = asset.find('SkinMaterialIndex').text
        hair_hue_index  = asset.find('SkinHueIndex').text
        hair_material_index = "0"
        # if "togruta" in pcs_node_fqn:
        #     hair_material_index = "0"
        # Merge haircolor dynamic node data (facehair uses the same hair color)
        derived = hair_material_data['Derived']
        if derived == "Uber":
            pass
        elif derived == "HairC" and dynamic_haircolor:
            hair_material_data = merge_mat_dynamic_node_data(hair_material_data, dynamic_haircolor, hair_material_index)
        elif derived == "SkinB" and dynamic_skincolor:
            hair_material_data = merge_mat_dynamic_node_data(hair_material_data, dynamic_haircolor, hair_material_index)
        else:
            hair_material_data = merge_mat_dynamic_node_data(hair_material_data, dynamic_haircolor, hair_material_index)



    # -------------------------------
    # Process appSlotFaceHair
    # -------------------------------
    if 'appSlotFaceHair' not in ami_data:  # PCs without beards or other facial elements
        facehair_models = None  # This will signal to skipe adding it to the JSON data
    else:
        data = ami_data['appSlotFaceHair']['value']
        appAppearanceSlotModelID	    = data['appAppearanceSlotModelID']
        appAppearanceSlotMaterialIndex  = data['appAppearanceSlotMaterialIndex']
        appAppearanceSlotAttachments	= data['appAppearanceSlotAttachments']  # specific attachments to use
        
        # root_xml_facehair = open_xml_file( os.path.join(swtor_resources_dir, 'art/dynamic/facehair/index.xml') )
        asset = _SWTOR_DATA['root_xml_facehair'].find(f"./Asset[ID='{appAppearanceSlotModelID}']")
   
        facehair_models = []  # models accumulate in a list
     
        base_file = asset.find('BaseFile').text
        if base_file:
            facehair_models += [base_file]


        # -------------------------------
        # facehair attachments models
        facehair_attachments = asset.find("Attachments")  # all possible attachments for this facehair
        if facehair_attachments:
            for facehair_attachment in facehair_attachments:
                facehair_attachment_id = facehair_attachment.get("id")
                if int(facehair_attachment_id) in appAppearanceSlotAttachments:
                    facehair_attachment_path = [facehair_attachment.get("filename")]
                    facehair_models += facehair_attachment_path
        facehair_models = [process_wildcards(item, bodytype_code) for item in facehair_models]


        # -------------------------------
        # facehair material
        materials = asset.find("Materials")
        facehair_material = materials.find(f"./Material/[@id='{appAppearanceSlotMaterialIndex}']")
        facehair_material_filepath = facehair_material.get("filename")
        facehair_material_filepath = process_wildcards(facehair_material_filepath, bodytype_code)
        facehair_material_data = get_matfile_data(os.path.normpath( f'{swtor_resources_variable_folderpath}{facehair_material_filepath}') )
        facehair_material_index  = asset.find('SkinMaterialIndex').text
        facehair_material_index  = "0"
        facehair_hue_index  = asset.find('SkinHueIndex').text
        
        if "zabrak" in pcs_node_fqn:
            hair_material_index  = "0"
        else:
            hair_material_index  = "1"

        # Merge haircolor dynamic node data (facehair uses the same hair color)
        if dynamic_haircolor:
            derived = facehair_material_data['Derived']
            if derived == "Uber":
                pass
            if derived == "HairC" and dynamic_haircolor:
                facehair_material_data = merge_mat_dynamic_node_data(facehair_material_data, dynamic_haircolor, facehair_material_index)
            elif derived == "SkinB" and dynamic_skincolor:
                facehair_material_data = merge_mat_dynamic_node_data(facehair_material_data, dynamic_haircolor, facehair_material_index)
            elif derived == "Garment" and dynamic_skincolor:
                facehair_material_data = merge_mat_dynamic_node_data(facehair_material_data, dynamic_haircolor, facehair_material_index)
        
    # Build paths.json dict
    # -----------------------------------------------------------------------------
    # Create the blocks first and organize them later
    # region
    
    
    print("Generating JSON data")
    
    
    paths_data = []

    
    # Metadata
    # -------------------------------

    paths_data += [
        {
            "slotName"                  : "meta",
            "charType"                  : "pc",
            "charName"                  : "",
            "nppPath"                   : pcs_node_fqn,
            "bodyType"                  : bodytype_code,
            "prefer_legacy_materials"   : legacy_mode,
            "errors"                    : [],
        }
    ]

    
    # head + eye
    # -------------------------------
    paths_data += [
        {
            "slotName": "head",
            "models": head_models,
            "materialInfo": {
                "matPath": head_material_filepath,
                "ddsPaths": {
                    "paletteMap":           head_material_data["PaletteMap"]["value"] + ".dds",
                    "paletteMaskMap":       head_material_data["PaletteMaskMap"]["value"] + ".dds",
                    "diffuseMap":           head_material_data["DiffuseMap"]["value"] + ".dds",
                    "glossMap":             head_material_data["GlossMap"]["value"] + ".dds",
                    "rotationMap":          head_material_data["RotationMap1"]["value"] + ".dds",
                    "ageMap":               age_basefile,
                    "complexionMap":        complexion_basefile,
                    "facepaintMap":         facepaint_basefile,
                    # directionMap not upported right now in Atroxa's add-on, but maybe in Crunch's.
                    # WrinkleMaps have "variable" maps, but naming scheme seems 
                    # Consistent enough for the parser to deduce them with just these:
                    "directionMap":         head_material_data["DirectionMap"]["value"] + ".dds",  # Filled with a default black if none
                    "animatedWrinkleMap":   head_material_data["animatedWrinkleMap"]["value"] + ".dds",
                    "animatedWrinkleMask":  head_material_data["animatedWrinkleMask"]["value"] + ".dds",
                },
                "otherValues": {
                    "derived": head_material_data["Derived"],
                    "flush": [
                        head_material_data["FlushTone"]["value"][0],
                        head_material_data["FlushTone"]["value"][1],
                        head_material_data["FlushTone"]["value"][2],
                    ],
                    "fleshBrightness": head_material_data["FleshBrightness"]["value"],
                    "palette1": [
                        head_material_data["palette1"]["value"][0],
                        head_material_data["palette1"]["value"][1],
                        head_material_data["palette1"]["value"][2],
                        head_material_data["palette1"]["value"][3],
                    ],
                    "palette2": [
                        head_material_data["palette2"]["value"][0],
                        head_material_data["palette2"]["value"][1],
                        head_material_data["palette2"]["value"][2],
                        head_material_data["palette2"]["value"][3],
                    ],
                    "palette1Specular": [
                        head_material_data["palette1Specular"]["value"][0],
                        head_material_data["palette1Specular"]["value"][1],
                        head_material_data["palette1Specular"]["value"][2],
                    ],
                    "palette2Specular": [
                        head_material_data["palette2Specular"]["value"][0],
                        head_material_data["palette2Specular"]["value"][1],
                        head_material_data["palette2Specular"]["value"][2],
                    ],
                    "palette1MetallicSpecular": [
                        head_material_data["palette1MetallicSpecular"]["value"][0],
                        head_material_data["palette1MetallicSpecular"]["value"][1],
                        head_material_data["palette1MetallicSpecular"]["value"][2],
                    ],
                    "palette2MetallicSpecular": [
                        head_material_data["palette2MetallicSpecular"]["value"][0],
                        head_material_data["palette2MetallicSpecular"]["value"][1],
                        head_material_data["palette2MetallicSpecular"]["value"][2],
                    ],
                    "materialSkinIndex": head_material_index  # See this fn's docstrings
                },
                "eyeMatInfo": {
                    "matPath": eye_material_filepath,
                    "ddsPaths": {
                        "paletteMap":       eye_material_data["PaletteMap"]["value"] + ".dds",
                        "paletteMaskMap":   eye_material_data["PaletteMaskMap"]["value"] + ".dds",
                        "diffuseMap":       eye_material_data["DiffuseMap"]["value"] + ".dds",
                        "glossMap":         eye_material_data["GlossMap"]["value"] + ".dds",
                        "rotationMap":      eye_material_data["RotationMap1"]["value"] + ".dds",
                    },
                    "otherValues": {
                        "derived": eye_material_data["Derived"],
                        # Eyes have no FlushTone
                        # "flush": [
                        #     eye_material_data["FlushTone"]["value"][0],
                        #     eye_material_data["FlushTone"]["value"][1],
                        #     eye_material_data["FlushTone"]["value"][2],
                        # ],
                        # "fleshBrightness": eye_material_data["FleshBrightness"]["value"],
                        "palette1": [
                            eye_material_data["palette1"]["value"][0],
                            eye_material_data["palette1"]["value"][1],
                            eye_material_data["palette1"]["value"][2],
                            eye_material_data["palette1"]["value"][3],
                        ],
                        "palette2": [
                            eye_material_data["palette2"]["value"][0],
                            eye_material_data["palette2"]["value"][1],
                            eye_material_data["palette2"]["value"][2],
                            eye_material_data["palette2"]["value"][3],
                        ],
                        "palette1Specular": [
                            eye_material_data["palette1Specular"]["value"][0],
                            eye_material_data["palette1Specular"]["value"][1],
                            eye_material_data["palette1Specular"]["value"][2],
                        ],
                        "palette2Specular": [
                            eye_material_data["palette2Specular"]["value"][0],
                            eye_material_data["palette2Specular"]["value"][1],
                            eye_material_data["palette2Specular"]["value"][2],
                        ],
                        "palette1MetallicSpecular": [
                            eye_material_data["palette1MetallicSpecular"]["value"][0],
                            eye_material_data["palette1MetallicSpecular"]["value"][1],
                            eye_material_data["palette1MetallicSpecular"]["value"][2],
                        ],
                        "palette2MetallicSpecular": [
                            eye_material_data["palette2MetallicSpecular"]["value"][0],
                            eye_material_data["palette2MetallicSpecular"]["value"][1],
                            eye_material_data["palette2MetallicSpecular"]["value"][2],
                        ],
                        "materialSkinIndex": eye_material_index  # See this fn's docstrings
                    }
                }
            }
        }
    ]

    # hair
    # -------------------------------
    if hair_models:
        
        if skinmaterials_data['leg']["Derived"] == "SkinB":
            SkinB_data = {
                    "flush": [
                        skinmaterials_data['leg']["FlushTone"]["value"][0],
                        skinmaterials_data['leg']["FlushTone"]["value"][1],
                        skinmaterials_data['leg']["FlushTone"]["value"][2],
                    ],
                    "fleshBrightness": skinmaterials_data['leg']["FleshBrightness"]["value"],
                }
        else:
            SkinB_data = {
                "flush": ["0","0","0"],
                "fleshBrightness": "0",
            }

        paths_data += [
            {
                "slotName": "hair",
                "models": hair_models,
                "materialInfo": {
                    "matPath": hair_material_filepath,
                    "ddsPaths": {
                        "paletteMap":           hair_material_data["PaletteMap"]["value"] + ".dds",
                        "paletteMaskMap":       hair_material_data["PaletteMaskMap"]["value"] + ".dds",
                        "diffuseMap":           hair_material_data["DiffuseMap"]["value"] + ".dds",
                        "glossMap":             hair_material_data["GlossMap"]["value"] + ".dds",
                        "rotationMap":          hair_material_data["RotationMap1"]["value"] + ".dds",
                        # directionMap not upported right now in Atroxa's add-on, but maybe in Crunch's.
                        # WrinkleMaps have "variable" maps, but naming scheme seems 
                        # Consistent enough for the parser to deduce them with just these:
                        "directionMap":         hair_material_data["DirectionMap"]["value"],  # Filled with a default black if none
                    },
                    "otherValues": {
                        "derived": hair_material_data["Derived"],
                        "flush": SkinB_data["flush"],
                        "fleshBrightness": SkinB_data["fleshBrightness"],                    
                        "palette1": [
                            hair_material_data["palette1"]["value"][0],
                            hair_material_data["palette1"]["value"][1],
                            hair_material_data["palette1"]["value"][2],
                            hair_material_data["palette1"]["value"][3],
                        ],
                        "palette2": [
                            hair_material_data["palette2"]["value"][0],
                            hair_material_data["palette2"]["value"][1],
                            hair_material_data["palette2"]["value"][2],
                            hair_material_data["palette2"]["value"][3],
                        ],
                        "palette1Specular": [
                            hair_material_data["palette1Specular"]["value"][0],
                            hair_material_data["palette1Specular"]["value"][1],
                            hair_material_data["palette1Specular"]["value"][2],
                        ],
                        "palette2Specular": [
                            hair_material_data["palette2Specular"]["value"][0],
                            hair_material_data["palette2Specular"]["value"][1],
                            hair_material_data["palette2Specular"]["value"][2],
                        ],
                        "palette1MetallicSpecular": [
                            hair_material_data["palette1MetallicSpecular"]["value"][0],
                            hair_material_data["palette1MetallicSpecular"]["value"][1],
                            hair_material_data["palette1MetallicSpecular"]["value"][2],
                        ],
                        "palette2MetallicSpecular": [
                            hair_material_data["palette2MetallicSpecular"]["value"][0],
                            hair_material_data["palette2MetallicSpecular"]["value"][1],
                            hair_material_data["palette2MetallicSpecular"]["value"][2],
                        ],
                        # "materialSkinIndex": hair_material_index  # See this fn's docstrings
                    }
                }
            }
        ]

    # facehair
    # -------------------------------
    if facehair_models:
        
        if skinmaterials_data['leg']["Derived"] == "SkinB":
            SkinB_data = {
                    "flush": [
                        skinmaterials_data['leg']["FlushTone"]["value"][0],
                        skinmaterials_data['leg']["FlushTone"]["value"][1],
                        skinmaterials_data['leg']["FlushTone"]["value"][2],
                    ],
                    "fleshBrightness": skinmaterials_data['leg']["FleshBrightness"]["value"],
                }
        else:
            SkinB_data = {
                "flush": ["0","0","0"],
                "fleshBrightness": "0",
            }

        paths_data += [
            {
                "slotName": "facehair",
                "models": facehair_models,
                "materialInfo": {
                    "matPath": facehair_material_filepath,
                    "ddsPaths": {
                        "ddsPaths": {
                            "paletteMap":       facehair_material_data["PaletteMap"]["value"] + ".dds",
                            "paletteMaskMap":   facehair_material_data["PaletteMaskMap"]["value"] + ".dds",
                            "diffuseMap":       facehair_material_data["DiffuseMap"]["value"] + ".dds",
                            "glossMap":         facehair_material_data["GlossMap"]["value"] + ".dds",
                            "rotationMap":      facehair_material_data["RotationMap1"]["value"] + ".dds",
                            # directionMap not upported right now in Atroxa's add-on, but maybe in Crunch's.
                            # WrinkleMaps have "variable" maps, but naming scheme seems 
                            # Consistent enough for the parser to deduce them with just these:
                            "directionMap":     facehair_material_data["DirectionMap"]["value"],  # Filled with a default black if none
                        }
                    },
                    "otherValues": {
                        "derived": facehair_material_data["Derived"],
                        "flush": SkinB_data["flush"],
                        "fleshBrightness": SkinB_data["fleshBrightness"],                    
                        "palette1": [
                            facehair_material_data["palette1"]["value"][0],
                            facehair_material_data["palette1"]["value"][1],
                            facehair_material_data["palette1"]["value"][2],
                            facehair_material_data["palette1"]["value"][3],
                        ],
                        "palette2": [
                            facehair_material_data["palette2"]["value"][0],
                            facehair_material_data["palette2"]["value"][1],
                            facehair_material_data["palette2"]["value"][2],
                            facehair_material_data["palette2"]["value"][3],
                        ],
                        "palette1Specular": [
                            facehair_material_data["palette1Specular"]["value"][0],
                            facehair_material_data["palette1Specular"]["value"][1],
                            facehair_material_data["palette1Specular"]["value"][2],
                        ],
                        "palette2Specular": [
                            facehair_material_data["palette2Specular"]["value"][0],
                            facehair_material_data["palette2Specular"]["value"][1],
                            facehair_material_data["palette2Specular"]["value"][2],
                        ],
                        "palette1MetallicSpecular": [
                            facehair_material_data["palette1MetallicSpecular"]["value"][0],
                            facehair_material_data["palette1MetallicSpecular"]["value"][1],
                            facehair_material_data["palette1MetallicSpecular"]["value"][2],
                        ],
                        "palette2MetallicSpecular": [
                            facehair_material_data["palette2MetallicSpecular"]["value"][0],
                            facehair_material_data["palette2MetallicSpecular"]["value"][1],
                            facehair_material_data["palette2MetallicSpecular"]["value"][2],
                        ],
                        # "materialSkinIndex": facehair_material_index  # See this fn's docstrings
                    }
                }
            }
        ]

    # hand
    # -------------------------------
    paths_data += [
        {
            "slotName": "hand",
            "models": [
                f"/art/dynamic/hand/model/hand_naked_{bodytype_code}_archetype.gr2"
            ],
            "materialInfo": {
                "matPath": skinmaterials_files["hand"],
                "ddsPaths": {
                    "paletteMap":           skinmaterials_data['hand']["PaletteMap"]["value"] + ".dds",
                    "paletteMaskMap":       skinmaterials_data['hand']["PaletteMaskMap"]["value"] + ".dds",
                    "diffuseMap":           skinmaterials_data['hand']["DiffuseMap"]["value"] + ".dds",
                    "glossMap":             skinmaterials_data['hand']["GlossMap"]["value"] + ".dds",
                    "rotationMap":          skinmaterials_data['hand']["RotationMap1"]["value"] + ".dds",
                    # directionMap not upported right now in Atroxa's add-on, but maybe in Crunch's.
                    "directionMap":         skinmaterials_data['hand']["DirectionMap"]["value"] + ".dds",  # Filled with a default black if none
                },
                "otherValues": {
                    "derived": skinmaterials_data['hand']["Derived"],
                    "flush": [
                        skinmaterials_data['hand']["FlushTone"]["value"][0],
                        skinmaterials_data['hand']["FlushTone"]["value"][1],
                        skinmaterials_data['hand']["FlushTone"]["value"][2],
                    ],
                    "fleshBrightness": skinmaterials_data['hand']["FleshBrightness"]["value"],
                    "palette1": [
                        skinmaterials_data['hand']["palette1"]["value"][0],
                        skinmaterials_data['hand']["palette1"]["value"][1],
                        skinmaterials_data['hand']["palette1"]["value"][2],
                        skinmaterials_data['hand']["palette1"]["value"][3],
                    ],
                    "palette2": [
                        skinmaterials_data['hand']["palette2"]["value"][0],
                        skinmaterials_data['hand']["palette2"]["value"][1],
                        skinmaterials_data['hand']["palette2"]["value"][2],
                        skinmaterials_data['hand']["palette2"]["value"][3],
                    ],
                    "palette1Specular": [
                        skinmaterials_data['hand']["palette1Specular"]["value"][0],
                        skinmaterials_data['hand']["palette1Specular"]["value"][1],
                        skinmaterials_data['hand']["palette1Specular"]["value"][2],
                    ],
                    "palette2Specular": [
                        skinmaterials_data['hand']["palette2Specular"]["value"][0],
                        skinmaterials_data['hand']["palette2Specular"]["value"][1],
                        skinmaterials_data['hand']["palette2Specular"]["value"][2],
                    ],
                    "palette1MetallicSpecular": [
                        skinmaterials_data['hand']["palette1MetallicSpecular"]["value"][0],
                        skinmaterials_data['hand']["palette1MetallicSpecular"]["value"][1],
                        skinmaterials_data['hand']["palette1MetallicSpecular"]["value"][2],
                    ],
                    "palette2MetallicSpecular": [
                        skinmaterials_data['hand']["palette2MetallicSpecular"]["value"][0],
                        skinmaterials_data['hand']["palette2MetallicSpecular"]["value"][1],
                        skinmaterials_data['hand']["palette2MetallicSpecular"]["value"][2],
                    ],
                    "materialSkinIndex": hand_material_index  # See this fn's docstrings
                }
            }
        }
    ]
    
    # boot
    paths_data += [
        {
            "slotName": "boot",
            "models": [
                f"/art/dynamic/boot/model/boot_naked_{bodytype_code}_archetype.gr2"
            ],
            "materialInfo": {
                "matPath": skinmaterials_files["boot"],
                "ddsPaths": {
                    "paletteMap":           skinmaterials_data['boot']["PaletteMap"]["value"] + ".dds",
                    "paletteMaskMap":       skinmaterials_data['boot']["PaletteMaskMap"]["value"] + ".dds",
                    "diffuseMap":           skinmaterials_data['boot']["DiffuseMap"]["value"] + ".dds",
                    "glossMap":             skinmaterials_data['boot']["GlossMap"]["value"] + ".dds",
                    "rotationMap":          skinmaterials_data['boot']["RotationMap1"]["value"] + ".dds",
                    # directionMap not upported right now in Atroxa's add-on, but maybe in Crunch's.
                    "directionMap":         skinmaterials_data['boot']["DirectionMap"]["value"] + ".dds",  # Filled with a default black if none
                },
                "otherValues": {
                    "derived": skinmaterials_data['boot']["Derived"],
                    "flush": [
                        skinmaterials_data['boot']["FlushTone"]["value"][0],
                        skinmaterials_data['boot']["FlushTone"]["value"][1],
                        skinmaterials_data['boot']["FlushTone"]["value"][2],
                    ],
                    "fleshBrightness": skinmaterials_data['boot']["FleshBrightness"]["value"],
                    "palette1": [
                        skinmaterials_data['boot']["palette1"]["value"][0],
                        skinmaterials_data['boot']["palette1"]["value"][1],
                        skinmaterials_data['boot']["palette1"]["value"][2],
                        skinmaterials_data['boot']["palette1"]["value"][3],
                    ],
                    "palette2": [
                        skinmaterials_data['boot']["palette2"]["value"][0],
                        skinmaterials_data['boot']["palette2"]["value"][1],
                        skinmaterials_data['boot']["palette2"]["value"][2],
                        skinmaterials_data['boot']["palette2"]["value"][3],
                    ],
                    "palette1Specular": [
                        skinmaterials_data['boot']["palette1Specular"]["value"][0],
                        skinmaterials_data['boot']["palette1Specular"]["value"][1],
                        skinmaterials_data['boot']["palette1Specular"]["value"][2],
                    ],
                    "palette2Specular": [
                        skinmaterials_data['boot']["palette2Specular"]["value"][0],
                        skinmaterials_data['boot']["palette2Specular"]["value"][1],
                        skinmaterials_data['boot']["palette2Specular"]["value"][2],
                    ],
                    "palette1MetallicSpecular": [
                        skinmaterials_data['boot']["palette1MetallicSpecular"]["value"][0],
                        skinmaterials_data['boot']["palette1MetallicSpecular"]["value"][1],
                        skinmaterials_data['boot']["palette1MetallicSpecular"]["value"][2],
                    ],
                    "palette2MetallicSpecular": [
                        skinmaterials_data['boot']["palette2MetallicSpecular"]["value"][0],
                        skinmaterials_data['boot']["palette2MetallicSpecular"]["value"][1],
                        skinmaterials_data['boot']["palette2MetallicSpecular"]["value"][2],
                    ],
                    "materialSkinIndex": boot_material_index  # See this fn's docstrings
                }
            }
        }
    ]

    # leg
    # -------------------------------
    # (in males and females it is the character's underwear)
    
    if skinmaterials_data['leg']["Derived"] == "SkinB":
        SkinB_data = {
                "flush": [
                    skinmaterials_data['leg']["FlushTone"]["value"][0],
                    skinmaterials_data['leg']["FlushTone"]["value"][1],
                    skinmaterials_data['leg']["FlushTone"]["value"][2],
                ],
                "fleshBrightness": skinmaterials_data['leg']["FleshBrightness"]["value"],
            }
    else:
        SkinB_data = {
            "flush": ["0","0","0"],
            "fleshBrightness": "0",
        }

    paths_data += [
        {
            "slotName": "leg",  # This material is for the underwear. not for the skin. Check the material's "index"
            "models": leg_models,
            "materialInfo": {
                "matPath": f"/art/shaders/materials/leg_pantskin_non_non_a01underwear02_{gender_code}_v01.mat",
                "ddsPaths": {
                    "paletteMap":       leg_material_data["PaletteMap"]["value"] + ".dds",
                    "paletteMaskMap":   leg_material_data["PaletteMaskMap"]["value"] + ".dds",
                    "diffuseMap":       leg_material_data["DiffuseMap"]["value"] + ".dds",
                    "glossMap":         leg_material_data["GlossMap"]["value"] + ".dds",
                    "rotationMap":      leg_material_data["RotationMap1"]["value"] + ".dds",
                    # directionMap not upported right now in Atroxa's add-on, but maybe in Crunch's.
                    "directionMap":     leg_material_data["DirectionMap"]["value"] + ".dds",  # Filled with a default black if none
                },
                "otherValues": {
                    "derived": leg_material_data["Derived"],
                    "flush": SkinB_data["flush"],
                    "fleshBrightness": SkinB_data["fleshBrightness"],                    
                    "palette1": [
                        leg_material_data["palette1"]["value"][0],
                        leg_material_data["palette1"]["value"][1],
                        leg_material_data["palette1"]["value"][2],
                        leg_material_data["palette1"]["value"][3],
                    ],
                    "palette2": [
                        leg_material_data["palette2"]["value"][0],
                        leg_material_data["palette2"]["value"][1],
                        leg_material_data["palette2"]["value"][2],
                        leg_material_data["palette2"]["value"][3],
                    ],
                    "palette1Specular": [
                        leg_material_data["palette1Specular"]["value"][0],
                        leg_material_data["palette1Specular"]["value"][1],
                        leg_material_data["palette1Specular"]["value"][2],
                    ],
                    "palette2Specular": [
                        leg_material_data["palette2Specular"]["value"][0],
                        leg_material_data["palette2Specular"]["value"][1],
                        leg_material_data["palette2Specular"]["value"][2],
                    ],
                    "palette1MetallicSpecular": [
                        leg_material_data["palette1MetallicSpecular"]["value"][0],
                        leg_material_data["palette1MetallicSpecular"]["value"][1],
                        leg_material_data["palette1MetallicSpecular"]["value"][2],
                    ],
                    "palette2MetallicSpecular": [
                        leg_material_data["palette2MetallicSpecular"]["value"][0],
                        leg_material_data["palette2MetallicSpecular"]["value"][1],
                        leg_material_data["palette2MetallicSpecular"]["value"][2],
                    ],
                    "materialSkinIndex": leg_material_index  # See this fn's docstrings
                }
            }
        }
    ]

    # chest
    # -------------------------------
    # (in females it is the character's underwear.
    # In males the material should be the skinmat. This requires
    # handling FlushTone and FleshBrightness)
    
    if chest_material_data["Derived"] == "SkinB":
        SkinB_data = {
            "flush": [
                chest_material_data["FlushTone"]["value"][0],
                chest_material_data["FlushTone"]["value"][1],
                chest_material_data["FlushTone"]["value"][2],
            ],
            "fleshBrightness": chest_material_data["FleshBrightness"]["value"],
        }
    else:
        SkinB_data = {
            "flush": ["0","0","0"],
            "fleshBrightness": "0",
        }

    paths_data += [
        {
            "slotName": "chest",
            "models": chest_models,
            "materialInfo": {
                "matPath": chest_material_filepath,
                "ddsPaths": {
                    "paletteMap":       skinmaterials_data['chest']["PaletteMap"]["value"] + ".dds",
                    "paletteMaskMap":   skinmaterials_data['chest']["PaletteMaskMap"]["value"] + ".dds",
                    "diffuseMap":       skinmaterials_data['chest']["DiffuseMap"]["value"] + ".dds",
                    "glossMap":         skinmaterials_data['chest']["GlossMap"]["value"] + ".dds",
                    "rotationMap":      skinmaterials_data['chest']["RotationMap1"]["value"] + ".dds",
                    # directionMap not upported right now in Atroxa's add-on, but maybe in Crunch's.
                    "directionMap":     skinmaterials_data['chest']["DirectionMap"]["value"] + ".dds",  # Filled with a default black if none
                },
                "otherValues": {
                    "derived": chest_material_data["Derived"],
                    "flush": SkinB_data["flush"],
                    "fleshBrightness": SkinB_data["fleshBrightness"],                    
                    "palette1": [
                        chest_material_data["palette1"]["value"][0],
                        chest_material_data["palette1"]["value"][1],
                        chest_material_data["palette1"]["value"][2],
                        chest_material_data["palette1"]["value"][3],
                    ],
                    "palette2": [
                        chest_material_data["palette2"]["value"][0],
                        chest_material_data["palette2"]["value"][1],
                        chest_material_data["palette2"]["value"][2],
                        chest_material_data["palette2"]["value"][3],
                    ],
                    "palette1Specular": [
                        chest_material_data["palette1Specular"]["value"][0],
                        chest_material_data["palette1Specular"]["value"][1],
                        chest_material_data["palette1Specular"]["value"][2],
                    ],
                    "palette2Specular": [
                        chest_material_data["palette2Specular"]["value"][0],
                        chest_material_data["palette2Specular"]["value"][1],
                        chest_material_data["palette2Specular"]["value"][2],
                    ],
                    "palette1MetallicSpecular": [
                        chest_material_data["palette1MetallicSpecular"]["value"][0],
                        chest_material_data["palette1MetallicSpecular"]["value"][1],
                        chest_material_data["palette1MetallicSpecular"]["value"][2],
                    ],
                    "palette2MetallicSpecular": [
                        chest_material_data["palette2MetallicSpecular"]["value"][0],
                        chest_material_data["palette2MetallicSpecular"]["value"][1],
                        chest_material_data["palette2MetallicSpecular"]["value"][2],
                    ],
                        "materialSkinIndex": chest_material_index  # See this fn's docstrings
                }
            }
        }
    ]
    # endregion
    
    
    
    # skinMats
    # --------------------------------------------------------------
    # As the skinMats list's hair element's presence depends on the species,
    # we have to pre-compose the materials list before adding it to paths_data.
    # region
    skinMats_list = [
        # boot
        {
            "slotName": "boot",
            "materialInfo": {
                "matPath": skinmaterials_files["boot"]
            },
            "ddsPaths": {
                "paletteMap":           skinmaterials_data['boot']["PaletteMap"]["value"] + ".dds",
                "paletteMaskMap":       skinmaterials_data['boot']["PaletteMaskMap"]["value"] + ".dds",
                "diffuseMap":           skinmaterials_data['boot']["DiffuseMap"]["value"] + ".dds",
                "glossMap":             skinmaterials_data['boot']["GlossMap"]["value"] + ".dds",
                "rotationMap":          skinmaterials_data['boot']["RotationMap1"]["value"] + ".dds",
                # directionMap not upported right now in Atroxa's add-on, but maybe in Crunch's.
                "directionMap":         skinmaterials_data['boot']["DirectionMap"]["value"] + ".dds",  # Filled with a default black if none
            },
            "otherValues": {
                "derived": skinmaterials_data['boot']["Derived"],
                "flush": [
                    skinmaterials_data['boot']["FlushTone"]["value"][0],
                    skinmaterials_data['boot']["FlushTone"]["value"][1],
                    skinmaterials_data['boot']["FlushTone"]["value"][2],
                ],
                "fleshBrightness": skinmaterials_data['boot']["FleshBrightness"]["value"],
                "palette1": [
                    skinmaterials_data['boot']["palette1"]["value"][0],
                    skinmaterials_data['boot']["palette1"]["value"][1],
                    skinmaterials_data['boot']["palette1"]["value"][2],
                    skinmaterials_data['boot']["palette1"]["value"][3],
                ],
                "palette2": [
                    skinmaterials_data['boot']["palette2"]["value"][0],
                    skinmaterials_data['boot']["palette2"]["value"][1],
                    skinmaterials_data['boot']["palette2"]["value"][2],
                    skinmaterials_data['boot']["palette2"]["value"][3],
                ],
                "palette1Specular": [
                    skinmaterials_data['boot']["palette1Specular"]["value"][0],
                    skinmaterials_data['boot']["palette1Specular"]["value"][1],
                    skinmaterials_data['boot']["palette1Specular"]["value"][2],
                ],
                "palette2Specular": [
                    skinmaterials_data['boot']["palette2Specular"]["value"][0],
                    skinmaterials_data['boot']["palette2Specular"]["value"][1],
                    skinmaterials_data['boot']["palette2Specular"]["value"][2],
                ],
                "palette1MetallicSpecular": [
                    skinmaterials_data['boot']["palette1MetallicSpecular"]["value"][0],
                    skinmaterials_data['boot']["palette1MetallicSpecular"]["value"][1],
                    skinmaterials_data['boot']["palette1MetallicSpecular"]["value"][2],
                ],
                "palette2MetallicSpecular": [
                    skinmaterials_data['boot']["palette2MetallicSpecular"]["value"][0],
                    skinmaterials_data['boot']["palette2MetallicSpecular"]["value"][1],
                    skinmaterials_data['boot']["palette2MetallicSpecular"]["value"][2],
                ]
            },
        },
        
        # chest
        {
            "slotName": "chest",
            "materialInfo": {
                "matPath": skinmaterials_files["chest"],
            },
            "ddsPaths": {
                "paletteMap":           skinmaterials_data['chest']["PaletteMap"]["value"] + ".dds",
                "paletteMaskMap":       skinmaterials_data['chest']["PaletteMaskMap"]["value"] + ".dds",
                "diffuseMap":           skinmaterials_data['chest']["DiffuseMap"]["value"] + ".dds",
                "glossMap":             skinmaterials_data['chest']["GlossMap"]["value"] + ".dds",
                "rotationMap":          skinmaterials_data['chest']["RotationMap1"]["value"] + ".dds",
                # directionMap not upported right now in Atroxa's add-on, but maybe in Crunch's.
                "directionMap":         skinmaterials_data['chest']["DirectionMap"]["value"] + ".dds",  # Filled with a default black if none
            },
            "otherValues": {
                "derived": skinmaterials_data['chest']["Derived"],
                "flush": [
                    skinmaterials_data['chest']["FlushTone"]["value"][0],
                    skinmaterials_data['chest']["FlushTone"]["value"][1],
                    skinmaterials_data['chest']["FlushTone"]["value"][2],
                ],
                "fleshBrightness": skinmaterials_data['chest']["FleshBrightness"]["value"],
                "palette1": [
                    skinmaterials_data['chest']["palette1"]["value"][0],
                    skinmaterials_data['chest']["palette1"]["value"][1],
                    skinmaterials_data['chest']["palette1"]["value"][2],
                    skinmaterials_data['chest']["palette1"]["value"][3],
                ],
                "palette2": [
                    skinmaterials_data['chest']["palette2"]["value"][0],
                    skinmaterials_data['chest']["palette2"]["value"][1],
                    skinmaterials_data['chest']["palette2"]["value"][2],
                    skinmaterials_data['chest']["palette2"]["value"][3],
                ],
                "palette1Specular": [
                    skinmaterials_data['chest']["palette1Specular"]["value"][0],
                    skinmaterials_data['chest']["palette1Specular"]["value"][1],
                    skinmaterials_data['chest']["palette1Specular"]["value"][2],
                ],
                "palette2Specular": [
                    skinmaterials_data['chest']["palette2Specular"]["value"][0],
                    skinmaterials_data['chest']["palette2Specular"]["value"][1],
                    skinmaterials_data['chest']["palette2Specular"]["value"][2],
                ],
                "palette1MetallicSpecular": [
                    skinmaterials_data['chest']["palette1MetallicSpecular"]["value"][0],
                    skinmaterials_data['chest']["palette1MetallicSpecular"]["value"][1],
                    skinmaterials_data['chest']["palette1MetallicSpecular"]["value"][2],
                ],
                "palette2MetallicSpecular": [
                    skinmaterials_data['chest']["palette2MetallicSpecular"]["value"][0],
                    skinmaterials_data['chest']["palette2MetallicSpecular"]["value"][1],
                    skinmaterials_data['chest']["palette2MetallicSpecular"]["value"][2],
                ]
            },
        },
        
        # hand
        {
            "slotName": "hand",
            "materialInfo": {
                "matPath": skinmaterials_files["hand"],
            },
            "ddsPaths": {
                "paletteMap":           skinmaterials_data['hand']["PaletteMap"]["value"] + ".dds",
                "paletteMaskMap":       skinmaterials_data['hand']["PaletteMaskMap"]["value"] + ".dds",
                "diffuseMap":           skinmaterials_data['hand']["DiffuseMap"]["value"] + ".dds",
                "glossMap":             skinmaterials_data['hand']["GlossMap"]["value"] + ".dds",
                "rotationMap":          skinmaterials_data['hand']["RotationMap1"]["value"] + ".dds",
                # directionMap not upported right now in Atroxa's add-on, but maybe in Crunch's.
                "directionMap":         skinmaterials_data['hand']["DirectionMap"]["value"] + ".dds",  # Filled with a default black if none
            },
            "otherValues": {
                "derived": skinmaterials_data['hand']["Derived"],
                "flush": [
                    skinmaterials_data['hand']["FlushTone"]["value"][0],
                    skinmaterials_data['hand']["FlushTone"]["value"][1],
                    skinmaterials_data['hand']["FlushTone"]["value"][2],
                ],
                "fleshBrightness": skinmaterials_data['hand']["FleshBrightness"]["value"],
                "palette1": [
                    skinmaterials_data['hand']["palette1"]["value"][0],
                    skinmaterials_data['hand']["palette1"]["value"][1],
                    skinmaterials_data['hand']["palette1"]["value"][2],
                    skinmaterials_data['hand']["palette1"]["value"][3],
                ],
                "palette2": [
                    skinmaterials_data['hand']["palette2"]["value"][0],
                    skinmaterials_data['hand']["palette2"]["value"][1],
                    skinmaterials_data['hand']["palette2"]["value"][2],
                    skinmaterials_data['hand']["palette2"]["value"][3],
                ],
                "palette1Specular": [
                    skinmaterials_data['hand']["palette1Specular"]["value"][0],
                    skinmaterials_data['hand']["palette1Specular"]["value"][1],
                    skinmaterials_data['hand']["palette1Specular"]["value"][2],
                ],
                "palette2Specular": [
                    skinmaterials_data['hand']["palette2Specular"]["value"][0],
                    skinmaterials_data['hand']["palette2Specular"]["value"][1],
                    skinmaterials_data['hand']["palette2Specular"]["value"][2],
                ],
                "palette1MetallicSpecular": [
                    skinmaterials_data['hand']["palette1MetallicSpecular"]["value"][0],
                    skinmaterials_data['hand']["palette1MetallicSpecular"]["value"][1],
                    skinmaterials_data['hand']["palette1MetallicSpecular"]["value"][2],
                ],
                "palette2MetallicSpecular": [
                    skinmaterials_data['hand']["palette2MetallicSpecular"]["value"][0],
                    skinmaterials_data['hand']["palette2MetallicSpecular"]["value"][1],
                    skinmaterials_data['hand']["palette2MetallicSpecular"]["value"][2],
                ],
            },
        },
        
        # leg
        {
            "slotName": "leg",
            "materialInfo": {
                "matPath": skinmaterials_files["leg"],
            },
            "ddsPaths": {
                "paletteMap":           skinmaterials_data['leg']["PaletteMap"]["value"] + ".dds",
                "paletteMaskMap":       skinmaterials_data['leg']["PaletteMaskMap"]["value"] + ".dds",
                "diffuseMap":           skinmaterials_data['leg']["DiffuseMap"]["value"] + ".dds",
                "glossMap":             skinmaterials_data['leg']["GlossMap"]["value"] + ".dds",
                "rotationMap":          skinmaterials_data['leg']["RotationMap1"]["value"] + ".dds",
                # directionMap not upported right now in Atroxa's add-on, but maybe in Crunch's.
                "directionMap":         skinmaterials_data['leg']["DirectionMap"]["value"] + ".dds",  # Filled with a default black if none
            },
            "otherValues": {
                "derived": skinmaterials_data['leg']["Derived"],
                "flush": [
                    skinmaterials_data['leg']["FlushTone"]["value"][0],
                    skinmaterials_data['leg']["FlushTone"]["value"][1],
                    skinmaterials_data['leg']["FlushTone"]["value"][2],
                ],
                "fleshBrightness": skinmaterials_data['leg']["FleshBrightness"]["value"],
                "palette1": [
                    skinmaterials_data['leg']["palette1"]["value"][0],
                    skinmaterials_data['leg']["palette1"]["value"][1],
                    skinmaterials_data['leg']["palette1"]["value"][2],
                    skinmaterials_data['leg']["palette1"]["value"][3],
                ],
                "palette2": [
                    skinmaterials_data['leg']["palette2"]["value"][0],
                    skinmaterials_data['leg']["palette2"]["value"][1],
                    skinmaterials_data['leg']["palette2"]["value"][2],
                    skinmaterials_data['leg']["palette2"]["value"][3],
                ],
                "palette1Specular": [
                    skinmaterials_data['leg']["palette1Specular"]["value"][0],
                    skinmaterials_data['leg']["palette1Specular"]["value"][1],
                    skinmaterials_data['leg']["palette1Specular"]["value"][2],
                ],
                "palette2Specular": [
                    skinmaterials_data['leg']["palette2Specular"]["value"][0],
                    skinmaterials_data['leg']["palette2Specular"]["value"][1],
                    skinmaterials_data['leg']["palette2Specular"]["value"][2],
                ],
                "palette1MetallicSpecular": [
                    skinmaterials_data['leg']["palette1MetallicSpecular"]["value"][0],
                    skinmaterials_data['leg']["palette1MetallicSpecular"]["value"][1],
                    skinmaterials_data['leg']["palette1MetallicSpecular"]["value"][2],
                ],
                "palette2MetallicSpecular": [
                    skinmaterials_data['leg']["palette2MetallicSpecular"]["value"][0],
                    skinmaterials_data['leg']["palette2MetallicSpecular"]["value"][1],
                    skinmaterials_data['leg']["palette2MetallicSpecular"]["value"][2],
                ],
            },
        },
    ]
    
    # hair (This hair refers to second materials in hair models, such as horns in hair+horns)
    if 'hair' in skinmaterials_data:
        
        if skinmaterials_data['hair']["Derived"] == "SkinB":
            SkinB_data = {
                    "flush": [
                        skinmaterials_data['hair']["FlushTone"]["value"][0],
                        skinmaterials_data['hair']["FlushTone"]["value"][1],
                        skinmaterials_data['hair']["FlushTone"]["value"][2],
                    ],
                    "fleshBrightness": skinmaterials_data['hair']["FleshBrightness"]["value"],
                }
        else:
            SkinB_data = {
                "flush": ["0","0","0"],
                "fleshBrightness": "0",
            }

        skinMats_list += [
            {
                "slotName": "hair",  
                "materialInfo": {
                    "matPath": skinmaterials_files["hair"],
                },
                "ddsPaths": {
                    "paletteMap":           skinmaterials_data['hair']["PaletteMap"]["value"] + ".dds",
                    "paletteMaskMap":       skinmaterials_data['hair']["PaletteMaskMap"]["value"] + ".dds",
                    "diffuseMap":           skinmaterials_data['hair']["DiffuseMap"]["value"] + ".dds",
                    "glossMap":             skinmaterials_data['hair']["GlossMap"]["value"] + ".dds",
                    "rotationMap":          skinmaterials_data['hair']["RotationMap1"]["value"] + ".dds",
                    # directionMap not upported right now in Atroxa's add-on, but maybe in Crunch's.
                    "directionMap":         skinmaterials_data['hair']["DirectionMap"]["value"] + ".dds",  # Filled with a default black if none
                },
                "otherValues": {
                    "derived": skinmaterials_data['hair']["Derived"],
                    "flush": SkinB_data["flush"],
                    "fleshBrightness": SkinB_data["fleshBrightness"],                    
                    "palette1": [
                        skinmaterials_data['hair']["palette1"]["value"][0],
                        skinmaterials_data['hair']["palette1"]["value"][1],
                        skinmaterials_data['hair']["palette1"]["value"][2],
                        skinmaterials_data['hair']["palette1"]["value"][3],
                    ],
                    "palette2": [
                        skinmaterials_data['hair']["palette2"]["value"][0],
                        skinmaterials_data['hair']["palette2"]["value"][1],
                        skinmaterials_data['hair']["palette2"]["value"][2],
                        skinmaterials_data['hair']["palette2"]["value"][3],
                    ],
                    "palette1Specular": [
                        skinmaterials_data['hair']["palette1Specular"]["value"][0],
                        skinmaterials_data['hair']["palette1Specular"]["value"][1],
                        skinmaterials_data['hair']["palette1Specular"]["value"][2],
                    ],
                    "palette2Specular": [
                        skinmaterials_data['hair']["palette2Specular"]["value"][0],
                        skinmaterials_data['hair']["palette2Specular"]["value"][1],
                        skinmaterials_data['hair']["palette2Specular"]["value"][2],
                    ],
                    "palette1MetallicSpecular": [
                        skinmaterials_data['hair']["palette1MetallicSpecular"]["value"][0],
                        skinmaterials_data['hair']["palette1MetallicSpecular"]["value"][1],
                        skinmaterials_data['hair']["palette1MetallicSpecular"]["value"][2],
                    ],
                    "palette2MetallicSpecular": [
                        skinmaterials_data['hair']["palette2MetallicSpecular"]["value"][0],
                        skinmaterials_data['hair']["palette2MetallicSpecular"]["value"][1],
                        skinmaterials_data['hair']["palette2MetallicSpecular"]["value"][2],
                    ]
                },
            },
        ]
  
  
    # add SkinMats element
    paths_data += [
        {
            "slotName": "skinMats",
            "models": [],
            "materialInfo": {
                "mats": skinMats_list
            }
        }
    ]
    
    # endregion

    # UPDATE JSON DATA FILE
    with open( os.path.normpath(f"{ADDON_TEMP_FILES}/My Player Character.json"), "w" ) as f:
        f.write( json.dumps(paths_data, indent=4) )
        print("paths.json file saved")




# -----------------------------------------------------------------------------
# Scene updater (clear previous character and call SWTOR IO Tools)
# -----------------------------------------------------------------------------

def generate_character(self, context):
    
    # Process slider data
    ami_data, bodytype_code, fqn = parse_pcs_node_and_sliders(self, context)
    
    process_pcs_data(self, context, ami_data, bodytype_code, fqn)


    # Delete previous results (collections and its objects)
    for coll in bpy.data.collections:
        if coll.name.startswith("My Player Character"):
            delete_collection_recursive(coll)
    purge = bpy.ops.outliner.orphans_purge(do_recursive=True)
        
    # Call SWTOR IO Tools's import_mesh.gr2_json()
    # to process the JSON data and assemble the character.
    try:
        paths_json_filepath = f"{ADDON_TEMP_FILES}/My Player Character.json"
        result = bpy.ops.import_mesh.gr2_json(filepath = paths_json_filepath, prefer_legacy_materials = context.scene.zgswtor_pcs_legacy_mode)
        print(result)
        if result == {"CANCELLED"}:
            print(f"\n\nWARNING: SWTOR IO Tools Add-on failed to import {paths_json_filepath}\n\n")
        else:
            print("\n\nCharacter's Path File successfully processed!\n\n")
    except Exception as e:
        print(f"\n\nWARNING: the SWTOR IO Tools add-on CRASHED while importing:\n{paths_json_filepath}\n\n")
        print("Its error report was:")
        print("-" * 80)
        print(e)
        print("-" * 80)
        print()
        print("CANCELLING CHARACTER IMPORT")
        report_text = "The SWTOR IO Tools Add-on crashed while processing this character's Path file. \nPlease check if any of its assets is missing. "
        if swtor_resources_folderpath == None:
            report_text += "\nIf a SWTOR assets extraction's 'resources' folder is available, set it in this Add-on's Preferences and try again."
        self.report({"WARNING"}, report_text)
        bpy.context.window.cursor_set("DEFAULT")  # Show normal cursor icon
        return {"CANCELLED"}

    bpy.ops.object.select_all(action='DESELECT')
    
    
    

# -----------------------------------------------------------------------------
# Some properties updater functions
# -----------------------------------------------------------------------------

# Property update function for some ZGSWTOR_PCS_Sliders.
# In "interactive mode" it also regenerates the character's model. 
def node_data_and_sliders_labels_updater(self, context):
    parse_pcs_node_and_sliders(self, context)
    
    if context.scene.zgswtor_pcs_interactive_mode:
        generate_character(self, context)


def sliders_values_limiter(self, context):
    sliders = context.scene.zgswtor_pcs_sliders
    sliders_limits = context.scene.zgswtor_pcs_sliders_limits
    for slider_name in _SLIDERS_NAMES:
        if slider_name in sliders and getattr(sliders, slider_name) > sliders_limits[slider_name]:
            setattr(sliders, slider_name, sliders_limits[slider_name])

    if context.scene.zgswtor_pcs_interactive_mode:
        generate_character(self, context)

# endregion ###################################################################






# #############################################################################
# PROPERTY GROUPS
# region ######################################################################

class ZGSWTOR_PCS_Sliders(PropertyGroup):
    """
    GUI menus that will be set as per
    SWTOR's Character Creator's Sliders.
    
    Default values are for Jedi Human Male.
    """

    pcs_class: EnumProperty(
        name="Class",
        description="Character's Class",
        items=[
            ('jedi_knight', "Jedi Knight", ""),
            ('jedi_consular', "Jedi Consular", ""),
            ('trooper', "Trooper", ""),
            ('smuggler', "Smuggler", ""),
            ('sith_warrior', "Sith Warrior", ""),
            ('sith_inquisitor', "Sith Inquisitor", ""),
            ('imperial_agent', "Imperial Agent", ""),
            ('bounty_hunter', "Bounty Hunter", ""),
        ],
        default="jedi_knight",
        update=node_data_and_sliders_labels_updater,
    )

    pcs_gender: EnumProperty(
        name="Gender",
        description="Gender",
        items=[
            ('male', "Male", ""),
            ('female', "Female", ""),
        ],
        default="male",
        update=node_data_and_sliders_labels_updater,
    )

    pcs_species: EnumProperty(
        # All species lack "_legacy" because that's solved
        # during the composition of the node's FQN.
        name="Species",
        description="Species",
        items=[
            ('cathar', "Cathar", ""),
            ('chiss', "Chiss", ""),
            ('cyborg', "Cyborg", ""),
            ('human', "Human", ""),
            ('miralukan', "Miraluka", ""),
            ('mirialan', "Mirialan", ""),
            ('nautolan', "Nautolan", ""),
            ('rattataki', "Rattataki", ""),
            ('sith', "Sith Pureblood", ""),
            ('togruta', "Togruta", ""),
            ('twilek', "Twi'lek", ""),
            ('zabrak_imp', "Zabrak (Empire)", ""),
            ('zabrak_rep', "Zabrak (Republic)", ""),
        ],
        default="human",
        update=node_data_and_sliders_labels_updater,
    )
    
    pcs_bodytype: IntProperty(
        name="Body Type",
        description="Body Type",
        min=1,
        max=4,
        default=2,
        update=node_data_and_sliders_labels_updater,
    )
    
# PROGRAMMATIC ADDER OF PROPERTIES BY PROPERTY NAME.
# ADDS PROPERTIES NAMED AFTER THE SLIDERS' INTERNAL NAMES
# LISTED IN _SLIDERS_NAMES TO THE PROPERTY GROUP ZGSWTOR_PCS_Sliders.
#
# The "appSlot…" props, that are a chore to write one by one,
# are defined proceduraly via annotations here, after the class
# has been defined (watch the indentation: it happens OUTSIDE
# the block defining the PropertyGroup).
for property_name in _SLIDERS_NAMES:
    ZGSWTOR_PCS_Sliders.__annotations__[property_name] = bpy.props.IntProperty(
        name=property_name,
        default=1,
        soft_min=1,
        soft_max=100,
        min=1,
        max=100,
        update=sliders_values_limiter,
    )

# -----------------------------------------------------------------------------

class ZGSWTOR_PCS_Sliders_Labels(PropertyGroup):
    """
    GUI menus' labels, whose strings are changed per
    class-gender-species sliders menus choices.
    
    Default values are for Jedi Human Male.
    """

    appSlotHead       : StringProperty(name="appSlothead",          default="Head")
    appSlotAge        : StringProperty(name="appSlotAge",           default="Scars")
    appSlotComplexion : StringProperty(name="appSlotComplexion",    default="Complexion")
    appSlotEyeColor   : StringProperty(name="appSlotEyeColor",      default="Eye Color")
    appSlotFaceHair   : StringProperty(name="appSlotFaceHair",      default="Beards")
    appSlotFacePaint  : StringProperty(name="appSlotFacePaint",     default="Face Paint")
    appSlotHair       : StringProperty(name="appSlotHair",          default="Hair")
    appSlotHairColor  : StringProperty(name="appSlotHairColor",     default="Hair Color")
    appSlotSkinColor  : StringProperty(name="appSlotSkinColor",     default="Skin Color")

# -----------------------------------------------------------------------------


class ZGSWTOR_PCS_Sliders_Limits(PropertyGroup):
    # No properties defined here. All will be defined
    # programmatically via __annotations__.
    pass

# PROGRAMMATIC ADDER OF PROPERTIES BY PROPERTY NAME.
# ADDS PROPERTIES NAMED AFTER THE SLIDERS' INTERNAL NAMES
# LISTED IN _SLIDERS_NAMES TO THE PROPERTY GROUP ZGSWTOR_PCS_Sliders_Labels.
#
# Props are defined proceduraly via annotations here, after the class
# has been defined (watch the indentation: it happens OUTSIDE
# the block defining the PropertyGroup).
for property_name in _SLIDERS_NAMES:
    ZGSWTOR_PCS_Sliders_Limits.__annotations__[property_name] = bpy.props.IntProperty(
        name=property_name,
        default=1,
    )
    
# endregion ###################################################################






# #############################################################################
# MAIN OPERATOR
# region ######################################################################

class ZGSWTOR_PCS_OT_assembler(Operator):
    bl_label = "Assemble Player Character"
    bl_idname = "zgswtor.pcs_assembler"
    bl_description = (
        "Assembles a SWTOR Player Character per its settings in SWTOR's Appearance Designer Kiosk\n"
        "\n"
        "We recommend using the settings shown in the Appearance Designer Kiosk instead of\n"
        "the ones used at character creation, as the latter hides unlocked Cartel Market\n"
        "customizations and renumbers the rest, while the former lists them all.\n"
        "\n"
        "There is an Appearance Designer Kiosk at the Cartel Bazaar in the Fleets' stations\n"
        "where a player character's settings can be read for free"
    )
    bl_options = {'REGISTER', 'UNDO'}


    @classmethod
    def poll(cls, context):
        checks = requirements_checks()
        return checks["resources"]


    def execute(self, context):
        
        bpy.context.window.cursor_set("WAIT")

        generate_character(self, context)

        bpy.context.window.cursor_set("DEFAULT")

        return {"FINISHED"}

# endregion ###################################################################






# #############################################################################
# SAVE FILE OPERATOR
# region ######################################################################

"""Operator that copies a JSON file bundled with the add-on to a user-chosen location.

Integration:
    1. Place this code in the add-on (e.g. in operators.py).
    2. Adjust BUNDLED_JSON_PATH to point at the bundled file.
    3. Register EXPORT_OT_bundled_json (see register()/unregister() below, or add
       the class to the add-on's existing registration list).
    4. Invoke it from a menu/panel:
           layout.operator(EXPORT_OT_bundled_json.bl_idname)
           
           
Requires:
import shutil
from pathlib import Path
import bpy
from bpy.props import StringProperty
from bpy.path import ensure_ext
from bpy_extras.io_utils import ExportHelper
"""

# Required extension for the destination file.
JSON_EXT = ".json"

# Absolute path of the bundled JSON file, resolved relative to this module so
# it works wherever Blender installs the add-on/extension.
# Adjust the subfolder and file name to match the add-on's layout.
CHARACTER_JSON_PATH = ADDON_TEMP_FILES / "My Player Character.json"


class EXPORT_OT_bundled_json(bpy.types.Operator, ExportHelper):
    """Copy the add-on's bundled JSON file to a chosen folder and file name"""
    
    bl_idname = "zgswtor.pcs_json_saver"  # Rename with the add-on's prefix if desired.
    bl_label = "Export Player Character as a JSON file"
    bl_description = (
        "Exports the last assembled Player Character as a JSON file, which\n"
        "can be opened by the SWTOR IO Tools Add-on's JSON importer"
    )
    bl_options = {'REGISTER'}  # No scene data is modified, so no UNDO needed.

    # --- ExportHelper configuration -------------------------------------
    # Extension that ExportHelper appends automatically in the file browser
    # when the user has not typed it.
    filename_ext = JSON_EXT
 
    # Restrict the file browser listing to JSON files.
    filter_glob: StringProperty(
        default="*" + JSON_EXT,
        options={'HIDDEN'},
        maxlen=255,
    )
    # `filepath` (destination) and `check_existing` (overwrite confirmation)
    # are provided by ExportHelper.
 
    @classmethod
    def poll(cls, context):
        """Enable the operator only if the file exists."""
        return CHARACTER_JSON_PATH.is_file()
 
 
    def invoke(self, context, event):
        """Pre-fill the file browser with the bundled file's name, then open it."""
        if not self.filepath:
            self.filepath = CHARACTER_JSON_PATH.name
        return super().invoke(context, event)
 
 
    def execute(self, context):
        """Copy the bundled file to the destination chosen by the user."""
        # Safety net: guarantee the .json extension even if the file browser's
        # automatic handling was bypassed (e.g. operator called from a script).
        # case_sensitive=False keeps an existing ".JSON" untouched.
        destination = Path(
            ensure_ext(bpy.path.abspath(self.filepath), JSON_EXT, case_sensitive=False)
        )
 
        # Refuse to copy a file onto itself (shutil.SameFileError otherwise).
        if destination.resolve() == CHARACTER_JSON_PATH.resolve():
            self.report({'ERROR'}, "Destination is the bundled file itself")
            return {'CANCELLED'}
 
        try:
            # Create missing intermediate folders, then copy contents.
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(CHARACTER_JSON_PATH, destination)
        except OSError as exc:  # Permissions, disk full, invalid path, etc.
            self.report({'ERROR'}, f"Could not copy file: {exc}")
            return {'CANCELLED'}
 
        self.report({'INFO'}, f"Saved: {destination}")
        return {'FINISHED'}
    
# endregion ###################################################################






# #############################################################################
# REGISTRATIONS
# region ######################################################################

# Registration order: property group before anything that references it.
classes = (
    ZGSWTOR_PCS_Sliders,
    ZGSWTOR_PCS_Sliders_Labels,
    ZGSWTOR_PCS_Sliders_Limits,
    ZGSWTOR_PCS_OT_assembler,
    EXPORT_OT_bundled_json,
)


def register():
    
    global _SWTOR_DATA
    
    if not _SWTOR_DATA:
        load_swtor_bundled_data()
    
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.zgswtor_pcs_sliders        = PointerProperty(type=ZGSWTOR_PCS_Sliders)
    bpy.types.Scene.zgswtor_pcs_sliders_labels = PointerProperty(type=ZGSWTOR_PCS_Sliders_Labels)
    bpy.types.Scene.zgswtor_pcs_sliders_limits = PointerProperty(type=ZGSWTOR_PCS_Sliders_Limits)
    
    bpy.types.Scene.zgswtor_pcs_interactive_mode = BoolProperty(
        name="Interactive Mode",
        description=(
        "In Interactive Mode the character is regenerated at every settings change\n"
        "instead of waiting for clicking on the 'Assemble' button for confirmation"
        ),
        default=False,
        update=sliders_values_limiter,
    )
    
    bpy.types.Scene.zgswtor_pcs_legacy_mode = BoolProperty(
        name="Legacy Materials Mode",
        description="Use materials from before SWTOR Game Update 7.6's characters modernization",
        default=False,
        update=node_data_and_sliders_labels_updater,
    )

    
    # DOESN'T SEEM TO BE NECESSARY
    # Run once, after the classes and properties' registrations have completed,
    # in order to produce a first refresh of the UI with default values.
    # bpy.app.timers.register(_run_pcs_assembler_operator_once_after_register, first_interval=0.0)

def unregister():
    # Remove the scene attribute first, then unregister classes in reverse.
    del bpy.types.Scene.zgswtor_pcs_sliders
    del bpy.types.Scene.zgswtor_pcs_sliders_labels
    del bpy.types.Scene.zgswtor_pcs_sliders_limits
    del bpy.types.Scene.zgswtor_pcs_interactive_mode
    del bpy.types.Scene.zgswtor_pcs_legacy_mode
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

# Allows running the file directly from Blender's Text Editor for testing.
if __name__ == "__main__":
    register()
    
# endregion ###################################################################