import bpy
import addon_utils

from .addon_checks import requirements_checks


ADDON_ROOT = __file__.rsplit(__name__.rsplit(".")[0])[0] + __name__.rsplit(".")[0]

Y_SCALING_GRAL = 0.9
Y_SCALING_INFO = 0.75
Y_SCALING_SPACER = 0.6




# ################################################################################
# 3D VIEWPORT SIDEBAR
# ################################################################################
# region



# ---------------------------------------------------------------
# Addon Status Tab
# ---------------------------------------------------------------
class ZGSWTOR_PT_status_3dview(bpy.types.Panel):
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ZG SWTOR"
    bl_label = "ZG SWTOR Tools NX Status"

    def draw(self, context):
        
        checks = requirements_checks()

        layout = self.layout
        layout.scale_y = Y_SCALING_GRAL




        # ZG Status
        # region
        # ------------------------
        tool_section_zgstatus = layout.column(align=True)
        tool_section_zgstatus.scale_y = Y_SCALING_INFO


        # Status lines
        tool_section_zgstatus.alert = not checks["gr2"]
        tool_section_zgstatus.label(text="• SWTOR IO Tools Add-on: " + checks["gr2_status"])

        tool_section_zgstatus.alert = not checks["resources"]
        tool_section_zgstatus.label(text="• 'resources' Folder: " + checks["resources_status"])

        tool_section_zgstatus.alert = not checks["custom_shaders"]
        tool_section_zgstatus.label(text="• Custom Shaders: " + checks["custom_shaders_status"])
        
        
        # Visible explanation for items in red
        if (
            not checks["resources"]
            or not checks["custom_shaders"]
            or not checks["gr2"]
            ):
                        
            tool_section_info = layout.column(align=True)
            tool_section_info.scale_y = Y_SCALING_INFO
            tool_section_info.label(text="Tools showing up in red need")
            tool_section_info.label(text="to satisfy certain requirements")
            tool_section_info.label(text="(more info in their tooltips).")


        # swtor_ui_tools prefs and partial settings UI
        if checks["gr2_status"] == "DISABLED":
            
            tool_section_gr2pref = layout.box().column(align=False)
            tool_section_gr2pref.scale_y = Y_SCALING_GRAL
            tool_section_gr2pref.separator(factor=Y_SCALING_SPACER)
            tool_section_gr2pref.operator("zgswtor.open_gr2_addon_preferences", text=".gr2 Add-on's Prefs")
            
        elif checks["gr2_status"] == "ENABLED":
            
            gr2_addon_prefs = bpy.context.preferences.addons["swtor_io_tools"].preferences

            tool_section_gr2pref = layout.box().column(align=False)
            tool_section_gr2pref.separator(factor=Y_SCALING_SPACER)
            
            tool_section_gr2pref.scale_y = Y_SCALING_GRAL
            tool_section_gr2pref.label(text=".gr2 Models Import Settings:")
            split_row = tool_section_gr2pref.split(factor=0.5)
            col1 = split_row.column()
            col2 = split_row.column()
            col1.prop(gr2_addon_prefs,"gr2_scale_object", text="Scale By",)
            col2.prop(gr2_addon_prefs,"gr2_scale_factor", text="")
            col2.enabled = gr2_addon_prefs.gr2_scale_object

            tool_section_gr2pref.prop(gr2_addon_prefs,"gr2_apply_axis_conversion")
            
            tool_section_gr2pref.alert = not checks["gr2"]
            tool_section_gr2pref.operator("zgswtor.open_gr2_addon_preferences", text="SWTOR IO Tools Add-on's Prefs")
                


        # use swtor_ui_tools .gr2 import settings checkbox
        tool_section = layout.column()
        tool_section.scale_y = Y_SCALING_GRAL

        zg_swtor_tools_prefs = context.preferences.addons["zg_swtor_tools"].preferences
        tool_section.prop(zg_swtor_tools_prefs,"use_gr2_scale_custom_prop", text="Use SWTOR Obj. Scale Data")
        # ------------------------
        # endregion



# ---------------------------------------------------------------
# Area Tools Tab
# ---------------------------------------------------------------
class ZGSWTOR_PT_area_tools(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ZG SWTOR"
    bl_label = "SWTOR Area Tools"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        checks = requirements_checks()
        
        layout = self.layout
        layout.scale_y = Y_SCALING_GRAL




        # exclude_all_collections UI
        # region
        # ------------------------
        tool_section = layout.box().column(align=False)
        tool_section.label(text="Outliner Collections' Visibility")

        split = tool_section.split(factor= 0.75, align=True)
        col_left, col_right = split.column(align=True).row(align=True), split.column(align=True).row(align=True)
        disable_all = col_left.operator("zgswtor.exclude_include_collections", text="Disable Selected")
        disable_all.action = "DISABLE_SEL"
        disable_sel = col_right.operator("zgswtor.exclude_include_collections", text="All")
        disable_sel.action = "DISABLE_ALL"
        
        split = tool_section.split(factor= 0.75, align=True)
        col_left, col_right = split.column(align=True).row(align=True), split.column(align=True).row(align=True)
        disable_all = col_left.operator("zgswtor.exclude_include_collections", text="Enable Selected")
        disable_all.action = "ENABLE_SEL"
        disable_sel = col_right.operator("zgswtor.exclude_include_collections", text="All")
        disable_sel.action = "ENABLE_ALL"

        tool_section.prop(context.scene, "EAC_recursive", text="Include Their Offspring")
        # ------------------------
        # endregion




        # group_collections UI
        # region
        # ------------------------
        tool_section = layout.box().column(align=False)
        
        tool_section.label(text="Group Areas' Collections")
        
        split = tool_section.split(factor= 0.75, align=True)
        col_left, col_right = split.column(align=True).row(align=True), split.column(align=True).row(align=True)
        group_selected = col_left.operator("zgswtor.group_collections", text="Selected Collections")
        group_selected.action = "GROUP_SEL"
        group_all = col_right.operator("zgswtor.group_collections", text="All")
        group_all.action = "GROUP_ALL"

        split = tool_section.split(factor= 0.60, align=True)
        col_left, col_right = split.column(align=True).row(align=True), split.column(align=True).row(align=True)
        col_left_split=col_left.split(factor=0.68, align=True)
        col_left_split.label(text="Separator")
        col_left_split.prop(context.scene, "GC_coll_grouping_separator", text="")
        col_right.prop(context.scene, "GC_coll_grouping_position", text="Pos.")
        
        tool_section.prop(context.scene, "GC_disable_collections", text="Disable Collections After Grouping")
        
        tool_section.prop(context.scene, "GC_sort_collections", text="Keep Collections Sorted")
        # ------------------------
        # endregion




# ---------------------------------------------------------------
# Character Tools Tab
# ---------------------------------------------------------------

class ZGSWTOR_PT_character_tools(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ZG SWTOR"
    bl_label = "SWTOR Character Tools"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        checks = requirements_checks()        

        layout = self.layout
        layout.scale_y = Y_SCALING_GRAL




        # Pose Position / Reset Position UI
        # region
        # ------------------------
        # (this one is fully defined here, without
        # calling any Add-on operators)
        tool_section = layout.box().column(align=True)
        tool_section.label(text="Armatures In Scene:")
        if context.scene.objects:
            armature_col = tool_section.column(align=True)
            armatures = []
            for obj in context.scene.objects:
                if obj.type == "ARMATURE":
                    armatures.append(obj)
                    tool_section.separator(factor=Y_SCALING_SPACER)
                    armature_col = tool_section.column(align=True)
                    armature_col.label(text=obj.name)
                    armature_buttons = armature_col.row(align=True)
                    armature_buttons.prop(obj.data, "pose_position", expand=True)
            if not armatures:
                armature_col.label(text="      No armatures present.")
        # ------------------------
        # endregion




        # clear_bone_translations UI
        # region
        # ------------------------
        tool_section = layout.box().column(align=True)
        tool_section.operator("zgswtor.clear_bone_translations", text="Clear Bones' Translations")
        # ------------------------
        # endregion




        # prefixer UI
        # region
        # ------------------------
        tool_section = layout.box()
        
        tool_section_info = tool_section.column(align=True)
        tool_section_info.scale_y = Y_SCALING_INFO
        tool_section_info.label(text="It is advisable to rename the")
        tool_section_info.label(text="character's Objects, Materials")
        tool_section_info.label(text="Skeleton, and Collections in")
        tool_section_info.label(text="order to avoid conflicts with")
        tool_section_info.label(text="further imports.")
        
        col=tool_section.column(align=False)
        col.operator("zgswtor.prefixer", text="Prefix Selected Items")
        col.prop(context.scene, "zg_prefix", text = "Prefix")
        col.prop(context.scene, "zg_prefix_mats_skeletons_bool", text="Materials & Skeletons Too")
        # ------------------------
        # endregion




        # merge_phys_vertex_groups UI
        # region
        # ------------------------
        tool_section = layout.box()
        
        col = tool_section.column(align=True)

        col.label(text="Merge Physics Bones' VGs.")
        
        split = col.split(factor= 0.7, align=True)
        col_left, col_right = split.column(align=True), split.column(align=True)

        col_left.enabled = len(bpy.context.selected_objects) != 0
        merge_vg_sel = col_left.operator("zgswtor.merge_phys_vgs", text="Selected Objects")
        merge_vg_sel.use_selection_only = True

        col_right.enabled = len(bpy.data.objects) != 0
        merge_vg_sel = col_right.operator("zgswtor.merge_phys_vgs", text="All")
        merge_vg_sel.use_selection_only = False
                
        col.prop(context.scene, "MPVG_use_best_guess", text="Best-Guess Their Names")
        dimmable_field = col.row()
        dimmable_field.prop(context.scene, "MPVG_vg_names_common_part", text="Match")
        dimmable_field.enabled = not context.scene.MPVG_use_best_guess

        col.prop(context.scene, "MPVG_delete_originals", text="Delete Original Phys. VGs.")
        # ------------------------
        # endregion




# ---------------------------------------------------------------
# Materials Tools Tab
# ---------------------------------------------------------------

class ZGSWTOR_PT_materials_tools(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ZG SWTOR"
    bl_label = "SWTOR Materials Tools"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        checks = requirements_checks()

        layout = self.layout
        layout.scale_y = Y_SCALING_GRAL




        # set_backface_culling UI
        # region
        # ------------------------
        tool_section = layout.box()
        row = tool_section.row(align=True)
        row.operator("zgswtor.set_backface_culling", text="Set Backface Culling On").action="BACKFACE_CULLING_ON"
        
        in_row = row.row()  # for setting a non-50% contiguous row region
        in_row.scale_x = 0.35
        in_row.operator("zgswtor.set_backface_culling", text="Off").action="BACKFACE_CULLING_OFF"
        # ------------------------
        # endregion




        # process_named_materials UI
        # region
        # ------------------------
        tool_section = layout.box().column(align=True)
        tool_section.enabled = checks["resources"] and checks["gr2"]
        tool_section.alert = tool_section.enabled is False

        tool_section.label(text="Process Named Materials In")

        split = tool_section.split(factor= 0.7, align=True)
        col_left, col_right = split.column(align=True), split.column(align=True)

        process_mats_sel = col_left.operator("zgswtor.process_named_mats", text="Selected Objects")
        col_left.enabled = len(bpy.context.selected_objects) != 0
        process_mats_sel.use_selection_only = True

        process_mats_all = col_right.operator("zgswtor.process_named_mats", text="All")
        col_right.enabled = len(bpy.data.objects) != 0
        process_mats_all.use_selection_only = False

        process_mats_sel = tool_section.prop(context.scene, "use_deprecated_materials", text="Use Deprecated Materials")
        process_mats_sel = tool_section.prop(context.scene, "use_overwrite_bool", text="Overwrite Materials")
        process_mats_all = tool_section.prop(context.scene, "use_collect_colliders_bool", text="Collect Collider Objects")
        # ------------------------
        # endregion




        # CUSTOM SWTOR SHADERS SECTION
        # add_custom_external_swtor_shaders UI
        # region
        # ------------------------
        tool_section = layout.box().column(align=True)
        
        tool_section.row(align=True).label(text="Convert To ZG Custom Shaders")
        tool_section.row(align=True).label(text="(For Deprecated Shaders Only)")
        # tool_section.operator("zgswtor.customize_swtor_shaders", text="Convert to Custom Shaders")
        
        split = tool_section.split(factor= 0.7, align=True)

        col_left, col_right = split.column(align=True), split.column(align=True)
        col_left.alert = col_right.alert = not checks["gr2"]

        process_mats_sel = col_left.operator("zgswtor.customize_swtor_shaders", text="Selected Objects")
        col_left.enabled = len(bpy.context.selected_objects) != 0
        process_mats_sel.use_selection_only = True

        process_mats_all = col_right.operator("zgswtor.customize_swtor_shaders", text="All")
        col_right.enabled = len(bpy.data.objects) != 0
        process_mats_all.use_selection_only = False
        
        dimmable_row1 = tool_section.row(align=True)
        dimmable_row1.enabled = context.scene.enable_adding_custom_shaders
        dimmable_row1.operator("zgswtor.add_custom_external_swtor_shaders", text="Just Add Shaders To Project")
        
        dimmable_row2 = tool_section.row(align=True)
        dimmable_row2.enabled = context.scene.enable_linking_custom_shaders
        dimmable_row2.prop(context.scene, "use_linking_bool", text="Link instead of Append")
        
        dimmable_row3 = tool_section.row(align=True)
        dimmable_row3.enabled = checks["gr2"]
        dimmable_row3.prop(context.scene, "preserve_atroxa_bool", text="Preserve Original Shaders")
        # ------------------------
        # endregion




        tool_section.separator(factor=1.4)

        # skinsettings_ng_in_3d_viewer UI
        # region
        # ------------------------
        # (belongs to the same Custom Shaders toolset)
        tool_section.label(text="Apply Skin Settings Group to ZG Shaders")
        tool_section.operator("zgswtor.skinsettings_ng_in_3d_viewer", text="Create & Apply To Selection")
        split=tool_section.split(factor=0.52, align=True)
        split.label(text="PC-NPC name")
        split.prop(context.scene, "apply_skinsettings_name", text="")
        tool_section.prop(context.scene, "apply_skinsettings_twilek", text="Override Twi'lek Gloss")
        # ------------------------
        # endregion




        # set_custom_shaders_values UI
        # region
        # ------------------------
        # (belongs to the same Custom Shaders toolset)

        tool_section = layout.box().column(align=True)

        tool_section.label(text="Modify Custom Mat. Settings")
        
        tool_section.label(text="• Nodegroup-Level Settings:")
        split=tool_section.split(factor=0.68)
        split.scale_y = 0.7
        
        col = split.column(align=True)
        col.prop(context.scene, "scsv_specular_checkbox", text="Specular Str.")
        col.prop(context.scene, "scsv_roughness_checkbox", text="Roughness Fac.")
        col.prop(context.scene, "scsv_emission_checkbox", text="Emission Str.")
        col.prop(context.scene, "scsv_saturation_checkbox", text="Emission Sat.")
        col.prop(context.scene, "scsv_normal_checkbox", text="Normal Str.")
        
        col = split.column(align=True)
        col.prop(context.scene, "scsv_specular", text="")
        col.prop(context.scene, "scsv_roughness", text="")
        col.prop(context.scene, "scsv_emission", text="")
        col.prop(context.scene, "scsv_saturation", text="")
        col.prop(context.scene, "scsv_normal", text="")

        tool_section.label(text="• Material-Level Settings:")
        split=tool_section.split(factor=0.65)
        split.scale_y = 0.7
        
        col = split.column(align=True)
        if checks["blender_version"] < 4.2:
            col.prop(context.scene, "scsv_blend_mode_checkbox", text="Alpha Mode")
        col.prop(context.scene, "scsv_show_backface_checkbox", text="Show Backface")

        col = split.column(align=True)
        if checks["blender_version"] < 4.2:
            col.prop(context.scene, "scsv_blend_mode", text="")
        col.prop(context.scene, "scsv_show_backface", text="")

        tool_section.separator(factor=1)

        split = tool_section.split(factor= 0.7, align=True)
        col_left, col_right = split.column(align=True), split.column(align=True)

        scsv_to_selection = col_left.operator("zgswtor.set_custom_shaders_values", text="Selected Objects")
        col_left.enabled = len(bpy.context.selected_objects) != 0
        scsv_to_selection.use_selection_only = True

        scsv_to_all = col_right.operator("zgswtor.set_custom_shaders_values", text="All")
        col_right.enabled = len(bpy.data.objects) != 0
        scsv_to_all.use_selection_only = False
        # ------------------------
        # endregion




        # deduplicate_images, deduplicate_nodegroups and deduplicate_materials UIs
        # region
        # ------------------------
        tool_section = layout.box().column(align=True)
        tool_section.operator("zgswtor.deduplicate_materials", text="Deduplicate All Materials")
        tool_section.operator("zgswtor.deduplicate_nodegroups", text="Deduplicate All Nodegroups")
        tool_section.operator("zgswtor.deduplicate_images", text="Deduplicate All Images")
        # Already existing Purge operator
        tool_section.operator("outliner.orphans_purge", text="Purge All Orphan Data").do_recursive=True
        # ------------------------
        # endregion




        # set_dds UIs
        # region
        # ------------------------
        tool_section = layout.box()
        col=tool_section.column(align=False)
        col.operator("zgswtor.set_dds", text="Set all .dds to Non-Color")
        # ------------------------
        # endregion



# ---------------------------------------------------------------
# Objects Tools Tab
# ---------------------------------------------------------------

class ZGSWTOR_PT_objects_tools(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ZG SWTOR"
    bl_label = "SWTOR Objects Tools"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        
        layout = self.layout
        layout.scale_y = Y_SCALING_GRAL




        # quickscale UI
        # region
        # ------------------------
        tool_section = layout.box().column(align=False)
        row = tool_section.row(align=True).label(text="QuickScale Selected Objects")
        row = tool_section.row(align=True)
        row.operator("zgswtor.quickscale", text="Down").action = "DOWNSCALE"
        in_row = row.row()
        in_row.scale_x = 0.9  # for a non-50% contiguous row region
        in_row.prop(context.scene, "zgswtor_quickscale_factor", text="",)
        row.operator("zgswtor.quickscale", text="Up").action = "UPSCALE"

        tool_section.separator(factor=2)
        # ------------------------
        # endregion




        # Apply Transforms UI
        # region
        # ------------------------

        split = tool_section.split(factor= 0.75, align=False)
        
        col1 = split.column(align=True)
        row = col1.row(align=True)
        row.label(text="Apply")
        row.operator("zgswtor.apply_transforms", text="Rot.").action = 'ROTATION'
        row.operator("zgswtor.apply_transforms", text="Scale").action = 'SCALE'
        row = col1.row(align=True)
        row.operator("zgswtor.apply_transforms", text="Rotation + Scale").action = 'ROTATION_SCALE'
        
        col2 = split.column(align=True)
        col2.operator("zgswtor.apply_transforms", text="Pos.").action = 'LOCATION'
        col2.operator("zgswtor.apply_transforms", text="ALL").action = 'ALL'
        # ------------------------
        # endregion




        row = tool_section.row(align=True)
        row.prop(context.scene, "OAT_set_custom_props", text="Annotate Objs.")


        # Show the active object's transforms data as a representative
        # of all selected objects to be affected by the previous tool
        # so that we can see that the tools have produced changes
        # (completely implemented here, no operators called).
        selected_obj = context.object
        
        col=tool_section.column(align=True)
        col.scale_y = Y_SCALING_INFO
        if selected_obj:
            col.separator()
            col.label(text="Active Obj. Data (represent.):")
            
            row = col.row(align=True)
            row.enabled = False
            row.prop(selected_obj, "location", text="")

            row = col.row(align=True)
            row.enabled = False
            rotation_mode = selected_obj.rotation_mode
            if rotation_mode == 'QUATERNION':
                row.prop(selected_obj, "rotation_quaternion", text="")
            elif rotation_mode == 'AXIS_ANGLE':
                row.prop(selected_obj, "rotation_axis_angle", text="")
            else:
                row.prop(selected_obj, "rotation_euler", text="")
            
            row = col.row(align=True)
            row.enabled = False
            row.prop(selected_obj, "scale", text="")
            
            if 'gr2_scale' in selected_obj:
                col.label(text=f"gr2_axis_conversion: {selected_obj['gr2_axis_conversion']}")
                col.label(text=f"gr2_scale: {selected_obj['gr2_scale']}")
            else:
                col.label(text="No gr2_axis_conversion info.")
                col.label(text="No gr2_scale info.")
        else:
            pass




        # remove_doubles UI
        # region
        # ------------------------
        tool_section = layout.box()
        
        col=tool_section.column(align=False)
        col.label(text="Merge Double Vertices")
        
        split = col.split(factor= 0.7, align=True)
        col_left, col_right = split.column(align=True), split.column(align=True)

        remove_doubles = col_left.operator("zgswtor.remove_doubles", text="Selected Objects")
        col_left.enabled = len(bpy.context.selected_objects) != 0
        remove_doubles.use_selection_only = True

        remove_doubles = col_right.operator("zgswtor.remove_doubles", text="All")
        col_right.enabled = len(bpy.data.objects) != 0
        remove_doubles.use_selection_only = False
        # ------------------------
        # endregion




        # remove_doubles_edit_mode UI
        # region
        # ------------------------
        # col.separator(factor=1)
        
        col=tool_section.column(align=False)
        col.operator("zgswtor.remove_doubles_edit_mode", text="Selected Verts. (Edit Mode)")
        
        col_info=col.column(align=True)
        col_info.scale_y = Y_SCALING_INFO
        col_info.enabled = context.mode == 'EDIT_MESH'
        
        col_info.separator(factor=2)
        col_info.label(text="Use ONLY if merging vertices")
        col_info.label(text="creates NEW sharp edges:")
        col.enabled = context.mode == 'EDIT_MESH'
        btn_clear_sharp = col.operator("mesh.mark_sharp", text="Clear Sharps In Selected")
        btn_clear_sharp.clear = True
        col.prop(context.space_data.overlay, "show_edge_sharp", text="Display Sharp Edges", toggle=False)
        # ------------------------
        # endregion




        # clear_splitnormals_layers UI
        # region
        # ------------------------
        # tool_section = layout.box()
        # col=tool_section.column(align=False)
        # col.label(text="Clear Split Normals Layers")
        
        # split = col.split(factor= 0.7, align=True)
        # col_left, col_right = split.column(align=True), split.column(align=True)

        # clear_spl_normals = col_left.operator("zgswtor.clear_splitnormals_layers", text="Selected Objects")
        # col_left.enabled = len(bpy.context.selected_objects) != 0
        # clear_spl_normals.use_selection_only = True

        # clear_spl_normals = col_right.operator("zgswtor.clear_splitnormals_layers", text="All")
        # col_right.enabled = len(bpy.data.objects) != 0
        # clear_spl_normals.use_selection_only = False

                
        # tris_to_quads = col.operator("mesh.tris_convert_to_quads", text="Tris to Quads (Comparing)")
        # tris_to_quads.uvs = True
        # tris_to_quads.materials = True
        # ------------------------
        # endregion




        # set_modifiers UI
        # region
        # ------------------------
        tool_section = layout.box()
        col=tool_section.column(align=False)
        col.label(text="Add Modifiers To Selection")
        grid = col.grid_flow(row_major=True, columns=2, align=True)
        grid.operator("zgswtor.set_modifiers", text="SubD").action = "add_subd"
        grid.operator("zgswtor.set_modifiers", text="Multires").action = "add_multires"
        grid.operator("zgswtor.set_modifiers", text="Displace").action = "add_displace"
        grid.operator("zgswtor.set_modifiers", text="Solidify").action = "add_solidify"
        grid.operator("zgswtor.set_modifiers", text="Smooth Corrective").action = "add_smooth_corrective"
        shbutton=grid.row(align=True)
        shbutton.active = (bpy.context.scene.ZGshrinkwrap_target is not None)
        shbutton.operator("zgswtor.set_modifiers", text="Shrinkwrap").action = "add_shrinkwrap"
        row = col.row(align=True)
        split = row.split(factor=0.57, align=True)
        split.label(text="Shrinkw. Target")
        split.prop(context.scene, "ZGshrinkwrap_target", text="")

        row = col.row()
        row.operator("zgswtor.set_modifiers", text="Remove These Modifiers").action = "remove_them"

        row = col.row()
        row.label(text="Set Armature as")
        in_row = row.row(align=True)  # for setting a non-50% contiguous row region
        in_row.scale_x = 0.55
        in_row.operator("zgswtor.set_modifiers", text="First").action = "armature_first"
        in_row.operator("zgswtor.set_modifiers", text="Last").action = "armature_last"

        row = col.row()
        row.label(text="Preserve Volume")
        in_row = row.row(align=True)  # for setting a non-50% contiguous row region
        in_row.scale_x = 0.55  # Percentage of a full half row
        in_row.operator("zgswtor.set_modifiers", text="On").action = "preserve_volume_on"
        in_row.operator("zgswtor.set_modifiers", text="Off").action = "preserve_volume_off"
        # ------------------------
        # endregion




        # set_swtor_obj_custom_props UI
        # region
        # ------------------------
        tool_section = layout.box()

        col=tool_section.column(align=True)
        
        col.label(text="Set Obj. Properties Manually")
        split = col.split(factor= 0.7, align=True)
        col_left, col_right = split.column(align=True), split.column(align=True)

        set_props = col_left.operator("zgswtor.set_swtor_obj_custom_props", text="Selected Objects")
        col_left.enabled = len(bpy.context.selected_objects) != 0
        set_props.use_selection_only = True
        set_props.delete_props = False

        set_props = col_right.operator("zgswtor.set_swtor_obj_custom_props", text="All")
        col_right.enabled = len(bpy.data.objects) != 0
        set_props.use_selection_only = False
        set_props.delete_props = False
        
        split = col.split(factor= 0.9, align=True)
        split.prop(context.scene, "OCP_gr2_axis_conversion")
        split = col.split(factor= 0.8, align=True)
        split.prop(context.scene, "OCP_gr2_scale")

        # Show object data related to this tool
        # (completely implemented here, no operators called)
        selected_obj = context.object
        
        col=tool_section.column(align=True)
        col.scale_y = Y_SCALING_INFO
        if selected_obj:
            col.label(text="Active Obj. Data (represent.):")
                        
            if 'gr2_scale' in selected_obj:
                col.label(text=f"gr2_axis_conversion: {selected_obj['gr2_axis_conversion']}")
                col.label(text=f"gr2_scale: {selected_obj['gr2_scale']}")
            else:
                col.label(text="No gr2_axis_conversion info.")
                col.label(text="No gr2_scale info.")
        else:
            pass

        col=tool_section.column(align=True)

        col.label(text="Clear Objetcs Properties")
        split = col.split(factor= 0.7, align=True)
        col_left, col_right = split.column(align=True), split.column(align=True)

        set_props = col_left.operator("zgswtor.set_swtor_obj_custom_props", text="Selected Objects")
        col_left.enabled = len(bpy.context.selected_objects) != 0
        set_props.use_selection_only = True
        set_props.delete_props = True

        set_props = col_right.operator("zgswtor.set_swtor_obj_custom_props", text="All")
        col_right.enabled = len(bpy.data.objects) != 0
        set_props.use_selection_only = False
        set_props.delete_props = True
        # ------------------------
        # endregion



# ---------------------------------------------------------------
# Baking Tools Tab
# ---------------------------------------------------------------

class ZGSWTOR_PT_baking_tools(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ZG SWTOR"
    bl_label = "SWTOR Baking Tools"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        Y_SCALING_GRAL = 0.9
        Y_SCALING_INFO = 0.75
        Y_SCALING_SPACER = 0.3

        layout = self.layout
        layout.scale_y = Y_SCALING_GRAL




        # correct_twilek_uv UI
        # region
        # ------------------------
        tool_section = layout.box()
        tool_section.operator("zgswtor.correct_twilek_uv", text="Correct Twi'lek eyes' UVs")
        # ------------------------
        # endregion




        # bake_convert_to_legacy_materials UI
        # region
        # ------------------------
        tool_section = layout.box().column(align=True)

        tool_section.label(text="Convert Deprecated Shaders To")
        tool_section.label(text="Baking-Friendly Legacy Materials")
                
        split = tool_section.split(factor= 0.7, align=True)
        col_left, col_right = split.column(align=True), split.column(align=True)

        process_mats_sel = col_left.operator("zgswtor.convert_to_legacy_materials", text="Selected Objects")
        col_left.enabled = len(bpy.context.selected_objects) != 0
        process_mats_sel.clm_use_selection_only = True

        process_mats_all = col_right.operator("zgswtor.convert_to_legacy_materials", text="All")
        col_right.enabled = len(bpy.data.objects) != 0
        process_mats_all.clm_use_selection_only = False

        tool_section.prop(context.scene, "zg_add_baking_targets_bool", text="Add Baking Target Nodes")
        # ------------------------
        # endregion




        # bake_save_baked_images UI
        # region
        # ------------------------
        tool_section = layout.box()
        tool_heading = tool_section.column(align=True)
        tool_heading.scale_y = Y_SCALING_INFO
        tool_heading.label(text="Export All Images Having")
        tool_heading.label(text="This Text Inside Their Names")
        tool_heading.separator()
        tool_heading.label(text="(No Text Exports All Images)")
        tool_controls = tool_section.column(align=False)
        tool_controls.scale_y = Y_SCALING_GRAL
        tool_controls.prop(context.scene, "SBI_common_text_in_names", text="")
        tool_controls.prop(context.scene, "SBI_case_sensitive", text="Match Upper/Lower Case")
        tool_controls.operator("zgswtor.save_images_by_substring", text="Choose Destination Folder")
        # ------------------------
        # endregion

# endregion




# ################################################################################
# SHADER EDITOR SIDEBAR
# ################################################################################
# region




# ---------------------------------------------------------------
# Addon Status Tab
# ---------------------------------------------------------------

class ZGSWTOR_PT_status_node_editor(bpy.types.Panel):
    
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "ZG SWTOR"
    bl_label = "ZG SWTOR Tools Status"

    def draw(self, context):
        
        checks = requirements_checks()

        layout = self.layout
        layout.scale_y = Y_SCALING_GRAL




        # ZG Status report
        # region
        # ------------------------
        
        
        # Status lines
        tool_section_zgstatus = layout.column(align=True)
        tool_section_zgstatus.scale_y = Y_SCALING_INFO

        tool_section_zgstatus.alert = not checks["gr2"]
        tool_section_zgstatus.label(text="• .gr2 Add-on: " + checks["gr2_status"])

        tool_section_zgstatus.alert = not checks["resources"]
        tool_section_zgstatus.label(text="• 'resources' Folder: " + checks["resources_status"])

        tool_section_zgstatus.alert = not checks["custom_shaders"]
        tool_section_zgstatus.label(text="• Custom Shaders: " + checks["custom_shaders_status"])


        # Visible explanation for items in red
        if (
            not checks["resources"]
            or not checks["custom_shaders"]
            or not checks["gr2"]
            ):
                        
            tool_section_info = layout.column(align=True)
            tool_section_info.scale_y = Y_SCALING_INFO
            tool_section_info.label(text="Tools showing up in red need")
            tool_section_info.label(text="to satisfy certain requirements")
            tool_section_info.label(text="(more info in their tooltips).")



        # .gr2 Prefs
        if checks["gr2_status"] == "DISABLED":
            
            tool_section_gr2pref = layout.column(align=False)
            tool_section_gr2pref.scale_y = Y_SCALING_GRAL
            tool_section_gr2pref.separator(factor=Y_SCALING_SPACER)
            tool_section_gr2pref.operator("zgswtor.open_gr2_addon_preferences", text=".gr2 Add-on's Prefs")
        # ------------------------
        # endregion




# ---------------------------------------------------------------
# SWTOR Shader Editor Tools Tab
# ---------------------------------------------------------------

class ZGSWTOR_PT_shader_tools(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "ZG SWTOR"
    bl_label = "SWTOR Material Tools"

    def draw(self, context):
                
        checks = requirements_checks()

        layout = self.layout




        # process_named_materials UI
        # region
        # ------------------------
        tool_section = layout.box().column(align=True)
        
        tool_section.enabled = checks["resources"] and checks["gr2"] and bpy.context.material is not None
        tool_section.alert = not checks["resources"] and checks["gr2"]

        tool_section.label(text="Named Materials Processor")
            
        process_mats_sel = tool_section.operator("zgswtor.process_named_mats", text="Process This Material")
        if bpy.context.material:
            process_mats_sel.convert_this_material = bpy.context.material.name
        process_mats_sel.use_overwrite_bool = True
        # ------------------------
        # endregion



        # skinsettings_ng_in_shader_editor UI
        # region
        # ------------------------
        tool_section = layout.box().column(align=False)
        tool_section.enabled = True
        tool_section.alert = False

        tool_section.operator("zgswtor.skinsettings_ng_in_shader_editor", text="Add New ZG Skin Settings Group").action="ADD_NEW_SKINSETTINGS"
        row = tool_section.row()
        in_row = row.row(align=False)  # for setting a non-50% contiguous row region
        in_row.scale_x = 0.90  # Percentage of a full half row
        in_row.label(text="PC-NPC Name")
        row.prop(context.scene, "use_skinsettings_name", text="")

        # tool_section.operator("zgswtor.skinsettings_ng_in_shader_editor", text="Add existing Skin Settings Group").action="ADD_EXISTING_SKINSETTINGS"
        # build skinsettings nodegroups list
        # skinsettings_nodegroups = []
        # for ng in bpy.data.node_groups:
        #     if "Skin Settings" in ng.name and not "Template" in ng.name:
        #         skinsettings_nodegroups.append(ng)
        # Show list
        # col = tool_section.column()
        # for ng in skinsettings_nodegroups:
        #     op = col.operator('matalogue.goto_group', text=ng.name, emboss=True, icon='NODETREE')
        #     op.tree_type = "ShaderNodeTree"
        #     op.tree = ng.name



        tool_section.operator("zgswtor.skinsettings_ng_in_shader_editor", text="Copy ZG SkinB Data to Skin Settings Group").action="COPY_TO_SKINSETTINGS"
        tool_section.operator("zgswtor.skinsettings_ng_in_shader_editor", text="Connect Skin Group to ZG SkinB Shader").action="CONNECT_SKINSETTINGS"
        tool_section.prop(context.scene,"use_skinsettings_twilek", text="Override Twi'lek GlossMap")
        tool_section.operator("zgswtor.skinsettings_ng_in_shader_editor", text="Disconnect Skin Group from ZG SkinB Shader").action="DISCONNECT_SKINSETTINGS"

        tool_section = layout.box()
        row = tool_section.row(align=True)
        row.operator("zgswtor.shaders_io_linker", text="Link Matching Inputs/Outputs")

        tool_section = layout.box()
        col = tool_section.column(align=True)
        col.label(text="Copy Matching Inputs/Outputs' Values:")
        col.operator("zgswtor.shaders_io_copier", text="From Nodegroup To Active Nodegroup").action = "ng_to_ng"
        col.operator("zgswtor.shaders_io_copier", text="From Nodegroup To Settings Group").action = "ng_to_st"
        col.operator("zgswtor.shaders_io_copier", text="From Settings Group To Nodegroup").action = "st_to_ng"
        # ------------------------
        # endregion

# endregion




# #############
# Registrations
# #############
# region

classes = [
    ZGSWTOR_PT_status_3dview,
    ZGSWTOR_PT_area_tools,
    ZGSWTOR_PT_character_tools,
    ZGSWTOR_PT_materials_tools,
    ZGSWTOR_PT_objects_tools,
    ZGSWTOR_PT_baking_tools,
    ZGSWTOR_PT_status_node_editor,
    ZGSWTOR_PT_shader_tools,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

# endregion



    
if __name__ == "__main__":
    register()