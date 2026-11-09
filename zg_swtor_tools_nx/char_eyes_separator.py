import bpy
import bmesh



# Auxiliary functions

def separate_by_material(obj, material_slot_name):
    """
    Separate the polygons of an object that are associated to one of its material slots into a new object.

    Args:
        obj (str or bpy.data.objects): The name of the object or the object itself.
        material_slot_name (str): The name of the material slot.

    Returns:
        bpy.data.objects: The new object with the separated polygons.

    Note:
        The new object preserves attributes such as UVs, vertex groups, and weights.
    """
    if isinstance(obj, str):
        obj = bpy.data.objects[obj]
    

    # Get the material slot
    material_slot = obj_data.material_slots[material_slot_name]

    # Get the active material
    active_material = material_slot.material

    # Get the material index of the active material
    material_index = active_material.material_index

    # Get the polygons of the object
    polygons = obj_data.polygons

    # Create a new mesh for this object
    new_mesh = bpy.data.meshes.new(material_slot_name)

    # Create a new object for this mesh
    new_obj = bpy.data.objects.new(material_slot_name, new_mesh)

    # Link the new object to the scene
    bpy.context.collection.objects.link(new_obj)

    # Get the bmesh of the original object
    bm = bmesh.new()
    bm.from_mesh(obj_data)

    # Create a new bmesh for the new object
    new_bm = bmesh.new()
    new_mesh.from_pydata([p.co for p in [p for p in polygons if p.material_index == material_index]], [], [p.normal for p in [p for p in polygons if p.material_index == material_index]])
    new_mesh.update()
    new_bm.from_mesh(new_mesh)

    # Transfer UVs
    for poly in [p for p in polygons if p.material_index == material_index]:
        uv_layer = bm.loops[poly.loop_indices[0]].uv
        new_uv_layer = new_bm.loops[poly.loop_indices[0]].uv
        new_uv_layer[0] = uv_layer[0]
        new_uv_layer[1] = uv_layer[1]

    # Transfer vertex groups and weights
    for vg in obj_data.vertex_groups:
        new_vg = new_obj.vertex_groups.new(name=vg.name)
        for poly in [p for p in polygons if p.material_index == material_index]:
            for loop in poly.loop_indices:
                new_bm.loops[loop].vec = bm.loops[loop].vec
                new_vg.add([loop], 1.0, 'REPLACE')

    # Transfer material
    new_obj.active_material = active_material

    # Free the bmesh
    bm.free()
    new_bm.free()

    # Return the new object
    return new_obj

def separate_obj_by_specific_materials(obj_or_obj_name, materials_names, separate = True):

    """
    Separates an object's polys associated to specified materials
    into separate objects per those materials. By default it
    deletes those polys AND materials from the original object.
    
    Args:
        obj_or_obj_name (bpy.types.object or string): object to be separated.
        materials_names (list): list of materials names.
        separate (bool, optional): If False, no separate objects are produced and the polys are just deleted.
    Returns:
        list of bpy.types.object: list of separated objects, empty if there were no materials matches.
    """

    if type(obj_or_obj_name) == str:
        original_obj = bpy.data.objects[obj_or_obj_name]
    else:
        original_obj = obj_or_obj_name
        
    original_mesh = original_obj.data
    new_objs = []
    
    # Get material indices to separate
    mat_indices = [i for i, mat in enumerate(original_mesh.materials) if mat.name in materials_names]
    
    if separate:
        for mat_index in mat_indices:
            # Create a duplicate object
            new_obj = original_obj.copy()
            new_obj.data = original_obj.data.copy()
            bpy.context.collection.objects.link(new_obj)
            new_obj.name = f"{original_obj.name}_{original_mesh.materials[mat_index].name}"
            
            # Create a new bmesh to work with
            bm = bmesh.new()
            bm.from_mesh(new_obj.data)
            
            # Iterate through all faces and hide those that don't use the current material
            faces_to_delete = [f for f in bm.faces if f.material_index != mat_index]
            bmesh.ops.delete(bm, geom=faces_to_delete, context='FACES')
            
            # Update the mesh
            bm.to_mesh(new_obj.data)
            bm.free()
            
            new_objs.append(new_obj)
    
    # Update original object to remove specified materials' polys
    bm = bmesh.new()
    bm.from_mesh(original_mesh)
    faces_to_delete = [f for f in bm.faces if f.material_index in mat_indices]
    bmesh.ops.delete(bm, geom=faces_to_delete, context='FACES')
    bm.to_mesh(original_mesh)
    bm.free()

    # Update original object to remove specified materials' material slots
    for i, slot in enumerate(original_obj.material_slots[:]):  # Use a copy of the list to modify it safely
        if slot.material and slot.material.name in materials_names:
            # Remove the material slot by removing
            # the object.data.materials' element
            original_obj.data.materials.pop(index=i)

    return new_objs

def delete_polygons_on_side(obj_or_obj_name, side='LEFT'):
    
    if type(obj_or_obj_name) == str:
        obj = bpy.data.objects[obj_or_obj_name]
    else:
        obj = obj_or_obj_name

    # Ensure we're in object mode
    if obj.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Get the mesh data
    mesh = obj.data

    # Create a BMesh from the mesh data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Select polygons based on the side parameter
    for face in bm.faces:
        center = face.calc_center_median()
        if side == 'LEFT' and center.x < 0:
            face.select_set(True)
        elif side == 'RIGHT' and center.x >= 0:
            face.select_set(True)
        else:
            face.select_set(False)

    # Remove the selected faces
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.select], context='FACES')

    # Update the mesh with the BMesh data
    bm.to_mesh(mesh)
    bm.free()

    # Update the scene to reflect changes. NECESSARY???
    # mesh.update()  # This refreshes the mesh data
    # obj.data.update()  # Ensure that the object data is up-to-date
    # bpy.context.view_layer.update()  # Refresh the view layer to reflect changes

    print(f"Polygons on the {side} side have been deleted.")

def find_highest_lowest_vertices(obj_or_obj_name):
    
    if type(obj_or_obj_name) == str:
        obj = bpy.data.objects[obj_or_obj_name]
    else:
        obj = obj_or_obj_name

    # Get the mesh data from the object
    mesh = obj.data
    
    # Initialize variables to store highest and lowest vertices
    highest_vertex = None
    lowest_vertex = None
    
    # Initialize variables to store maximum and minimum Z coordinates
    max_z = -float('inf')
    min_z = float('inf')
    
    # Iterate through all vertices in the mesh
    for vert in mesh.vertices:
        # Get the world coordinates of the vertex
        world_vert = obj.matrix_world @ vert.co
        
        # Update highest and lowest vertices based on Z coordinate
        if world_vert.z > max_z:
            max_z = world_vert.z
            highest_vertex = world_vert
        
        if world_vert.z < min_z:
            min_z = world_vert.z
            lowest_vertex = world_vert
    
    return highest_vertex, lowest_vertex

def get_highest_and_lowest_vertices(obj_or_obj_name):
    
    if type(obj_or_obj_name) == str:
        obj = bpy.data.objects[obj_or_obj_name]
    else:
        obj = obj_or_obj_name

    # Ensure we are in object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create a bmesh from the object's mesh data
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    
    # Transform matrix to convert local coordinates to global
    global_matrix = obj.matrix_world
    
    highest_vertex = None
    lowest_vertex = None
    
    for v in bm.verts:
        global_coord = global_matrix @ v.co
        if highest_vertex is None or global_coord.z > highest_vertex.z:
            highest_vertex = global_coord
        if lowest_vertex is None or global_coord.z < lowest_vertex.z:
            lowest_vertex = global_coord
    
    bm.free()
    
    return highest_vertex, lowest_vertex

def set_obj_origin(obj_or_obj_name, new_origin):

    if type(obj_or_obj_name) == str:
        obj = bpy.data.objects[obj_or_obj_name]
    else:
        obj = obj_or_obj_name

    new_origin = Vector(new_origin)
    
    # Get the object's world matrix
    obj_matrix = obj.matrix_world
    
    # Calculate the current origin in world space
    current_origin_world = obj_matrix @ Vector((0, 0, 0))
    
    # Calculate the delta vector from current origin to new origin in world space
    delta_world = new_origin - current_origin_world
    
    # Apply the inverse world matrix to get delta in object space
    delta_object_space = obj_matrix.inverted() @ delta_world
    
    # Move the object's location to compensate for the delta
    obj.location += delta_world
    
    # Transform the mesh data to correct for the origin adjustment
    # Note: Applying the inverse translation in object space
    obj.data.transform(Matrix.Translation(-delta_object_space))
    
    # Update the mesh data to apply the changes
    obj.data.update()



class ZGSWTOR_OT_eyes_separator(bpy.types.Operator):
    bl_label = "Separate characters' eyesinto their own objects"
    bl_idname = "zgswtor.eyes_separator"
    bl_description = "Detects a material slot with 'eyes' in its material's name,/nselects its polygons, and separates them into one or two objects,/nrecentering their origins and linking them to the skeleton if any"
    bl_options = {'REGISTER', 'UNDO'}


    # Check that there is a selection of objects 
    # in the 3D Viewer and/or in any Outliner,
    # (which lets us include hidden objects)
    # in order to enable the operator.
    @classmethod
    def poll(cls,context):
        if bpy.context.mode == "OBJECT" and bpy.context.selected_objects:
            return True
        else:
            return False


    # Some properties
    
    bind_to_skeleton: bpy.props.BoolProperty(
        name="Bind Objects To Skeleton",
        description="Bind all objects to the skeleton, if imported.",
        default = True,
        # options={'HIDDEN'}
    )

    separate_eyes: bpy.props.BoolProperty(
        name="Separate Eyes From Head Object",
        description="Separates the eyes from the character's head object to make them\neasier to rig and animate (certain rigging systems require that).\nNeeds them to be using a material with 'eye' in its name, as separating criteria.\n\nThe result is a single object with both eyes.\n\nTo further separate them into individual eyes,\nuse the 'Separate Eyes From Each Other' option, too",
        default = False,
        # options={'HIDDEN'}
    )
    
    separate_each_eye: bpy.props.BoolProperty(
        name="   Separate Eyes From Each Other",
        description="When separating the eyes from the character's head object\nmake each eye its own object and set their origin points\nso that they can also be posed via simple rotations",
        default = False,
        # options={'HIDDEN'}
    )
    
    
    

    def execute(self, context):
        
        # Separate character's eye objects

        objs = list(bpy.context.selected_objects)

        for obj in character_objects:
            mat_slots = obj.material_slots
            for mat_slot in mat_slots:
                if not "eye" in obj.material_slots[1].name.lower():
                    continue
                else:         
                    # Duplicate head object
                    eyes_obj = duplicate_obj(obj)
                    
                    # Delete eyes' polys and material from head object
                    separate_obj_by_specific_materials(obj, mat_slot.name, separate = False)
                    
                    # Delete head's polys and material from eyes object (the duplicate head object)
                    separate_obj_by_specific_materials(eyes_obj, eyes_obj.material_slots[0].name, separate = False)
                    
                    if not self.separate_each_eye:
                        # Rename eyes object
                        eyes_obj.name = f"{obj.name}.eyes"
                        character_objects.append(eyes_obj)
                    else:
                        eyes_obj_right = eyes_obj
                        eyes_obj_left  = duplicate_obj(eyes_obj)
                        
                        delete_polygons_on_side(eyes_obj_right, side='LEFT')
                        highest_vertex, lowest_vertex = get_highest_and_lowest_vertices(eyes_obj_right)
                        new_origin_location = (highest_vertex.x, highest_vertex.y, (highest_vertex.z + lowest_vertex.z) / 2)
                        set_obj_origin(eyes_obj_right, new_origin_location)
                        
                        eyes_obj_right.name = f"{obj.name}.eyes.right"
                        character_objects.append(eyes_obj_right)

                        delete_polygons_on_side(eyes_obj_left, side='RIGHT')
                        highest_vertex, lowest_vertex = get_highest_and_lowest_vertices(eyes_obj_left)
                        new_origin_location = (highest_vertex.x, highest_vertex.y, (highest_vertex.z + lowest_vertex.z) / 2)
                        set_obj_origin(eyes_obj_left, new_origin_location)
                        
                        eyes_obj_left.name = f"{obj.name}.eyes.left"
                        character_objects.append(eyes_obj_left)
                        
                    
                    # eyes_obj, eye_r_obj, eye_l_obj, head_obj = separate_eyes(self, obj)
            
                    if eyes_obj:
                        character_objects.append(eyes_obj)
                            
                    # if eye_r_obj:
                    #     character_objects.extend( [eye_r_obj, eye_l_obj, head_obj] )
            break



        return {'FINISHED'}




def register():
    bpy.utils.register_class(ZGSWTOR_OT_eyes_separator)
    
    bpy.types.Scene.zgswtor_SWCA_bind_to_skeleton = bpy.props.BoolProperty(
        name="Bind Objects To Skeleton",
        description="Bind all objects to the skeleton, if imported",
        default = True,
    )

    bpy.types.Scene.zgswtor_SWCA_separate_eyes = bpy.props.BoolProperty(
        name="Separate Eyes From Head Object",
        description="Separates the eyes from the character's head object to make them\neasier to rig and animate (certain rigging systems require that).\nNeeds them to be using a material with 'eye' in its name, as separating criteria.\n\nThe result is a single object with both eyes.\nTo further separate them into individual eyes,\nuse the 'As Two Eye Objects' option, too.\n\nThis doesn't affect the ability to keep using\nSWTOR skeletons with the model's eyes",
        default = False,
    )

    bpy.types.Scene.zgswtor_SWCA_separate_each_eye = bpy.props.BoolProperty(
        name="As Two Eye Objects",
        description="When separating the eyes from the character's head object\nmake each eye its own object and set their origin points\nso that they can also be posed via simple rotations.\n\nThis doesn't affect the ability to keep using\nSWTOR skeletons with the model's eyes",
        default = False,
        # options={'HIDDEN'}
    )

def unregister():
    bpy.utils.unregister_class(ZGSWTOR_OT_eyes_separator)
    
    del bpy.types.Scene.zgswtor_SWCA_bind_to_skeleton
    del bpy.types.Scene.zgswtor_SWCA_separate_eyes
    del bpy.types.Scene.zgswtor_SWCA_separate_each_eye


if __name__ == "__main__":
    register()













