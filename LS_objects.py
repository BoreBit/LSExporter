import bpy
import bmesh


# ---------------------------------------------------------
# Operator
# ---------------------------------------------------------

class LS_OT_place_instances(bpy.types.Operator):
    bl_idname = "ls.place_instances"
    bl_label = "LS Place Instances"

    @staticmethod
    def place(active_mesh, other_meshes):

        # -------------------------------------------------
        # Get LS_scene_collection
        # -------------------------------------------------

        scene_collection = bpy.data.collections.get("LS_scene_collection")

        if scene_collection is None:
            bpy.context.window_manager.popup_menu(
                lambda self, context: self.layout.label(
                    text="LS_scene_collection not found."
                ),
                title="Error",
                icon='ERROR'
            )
            return

        # -------------------------------------------------
        # Iterate over every instance of active mesh
        # -------------------------------------------------

        for obj in list(scene_collection.objects):

            if obj.type != 'MESH':
                continue

            if obj.data != active_mesh.data:
                continue

            # obj is one instance of active mesh

            for mesh in other_meshes:

                new_instance = mesh.copy()

                # Share mesh data (instance)
                new_instance.data = mesh.data

                # Same transform as active instance
                new_instance.matrix_world = obj.matrix_world.copy()

                scene_collection.objects.link(new_instance)

    def execute(self, context):

        active = context.active_object

        if active is None:
            self.report({'ERROR'}, "No active object.")
            return {'CANCELLED'}

        if active.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh.")
            return {'CANCELLED'}

        selected = [
            obj for obj in context.selected_objects
            if obj.type == 'MESH'
        ]

        other_meshes = [
            obj for obj in selected
            if obj != active
        ]

        if not other_meshes:
            self.report({'ERROR'}, "Select at least one additional mesh.")
            return {'CANCELLED'}

        LS_OT_place_instances.place(active, other_meshes)

        self.report({'INFO'}, "Instances placed.")

        return {'FINISHED'}


# ---------------------------------------------------------
# Merge Objects
# ---------------------------------------------------------

class LS_OT_merge_objects(bpy.types.Operator):
    bl_idname = "ls.merge_objects"
    bl_label = "LS Merge Objects"
    bl_description = "Merge selected objects into the active object"

    @staticmethod
    def merge(active_mesh, other_meshes):

        # -------------------------------------------------
        # Get LS_scene_collection
        # -------------------------------------------------

        scene_collection = bpy.data.collections.get("LS_scene_collection")

        if scene_collection is None:
            print("LS_scene_collection not found.")
            return

        # -------------------------------------------------
        # Delete every instance of the other meshes
        # -------------------------------------------------

        for obj in list(scene_collection.objects):

            if obj.type != 'MESH':
                continue

            for mesh in other_meshes:

                if obj.data == mesh.data:
                    bpy.data.objects.remove(obj, do_unlink=True)
                    break

        view_layer = bpy.context.view_layer

        # Deselect everything
        bpy.ops.object.select_all(action='DESELECT')

        # Select active + other meshes
        active_mesh.select_set(True)

        for obj in other_meshes:
            obj.select_set(True)

        # Make active_mesh the active object
        view_layer.objects.active = active_mesh

        # Join meshes
        bpy.ops.object.join()

        print(f"Merged {len(other_meshes)} mesh(es) into {active_mesh.name}")

    def execute(self, context):

        active = context.active_object

        if active is None:
            self.report({'ERROR'}, "No active object selected.")
            return {'CANCELLED'}

        if active.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh.")
            return {'CANCELLED'}

        selected = [
            obj for obj in context.selected_objects
            if obj.type == 'MESH'
        ]

        other_meshes = [
            obj for obj in selected
            if obj != active
        ]

        if not other_meshes:
            self.report({'ERROR'}, "Select at least one additional mesh.")
            return {'CANCELLED'}

        LS_OT_merge_objects.merge(active, other_meshes)

        self.report({'INFO'}, "Merge placeholder executed.")

        return {'FINISHED'}


#-----------------modular pieces from scene---------
class LS_OT_get_modular_objects(bpy.types.Operator):
    bl_idname = "ls.get_modular_objects"
    bl_label = "LS Get Modular Objects"
    bl_description = "Keep one object selected for each unique mesh"

    def execute(self, context):

        selected = [
            obj for obj in context.selected_objects
            if obj.type == 'MESH'
        ]

        if not selected:
            self.report({'WARNING'}, "No mesh objects selected.")
            return {'CANCELLED'}

        unique_meshes = set()

        # Deselect duplicates
        for obj in selected:

            mesh = obj.data

            if mesh in unique_meshes:
                obj.select_set(False)
            else:
                unique_meshes.add(mesh)
                obj.select_set(True)

        self.report(
            {'INFO'},
            f"Selected {len(unique_meshes)} unique modular object(s)."
        )

        return {'FINISHED'}
    
#-----------------make modular collection----------------
class LS_OT_create_modular_objects(bpy.types.Operator):
    bl_idname = "ls.create_modular_objects"
    bl_label = "LS Create Modular Objects"
    bl_description = "Create one modular object for every unique mesh"

    def execute(self, context):

        selected = [
            obj for obj in context.selected_objects
            if obj.type == 'MESH'
        ]

        if not selected:
            self.report({'WARNING'}, "No mesh objects selected.")
            return {'CANCELLED'}

        # -------------------------------------------------
        # Keep only one object per mesh datablock
        # -------------------------------------------------

        unique_objects = []
        seen_meshes = set()

        for obj in selected:

            if obj.data in seen_meshes:
                continue

            seen_meshes.add(obj.data)
            unique_objects.append(obj)

        # -------------------------------------------------
        # Get / Create LS_modular_collection
        # -------------------------------------------------

        collection_name = "LS_modular_collection"

        modular_collection = bpy.data.collections.get(collection_name)

        if modular_collection is None:
            modular_collection = bpy.data.collections.new(collection_name)
            context.scene.collection.children.link(modular_collection)

        # -------------------------------------------------
        # Create modular objects
        # -------------------------------------------------

        created = 0
        skipped = 0

        for obj in unique_objects:
            
            # ---------------------------------------------
            # Check if this mesh already exists in
            # LS_modular_collection
            # ---------------------------------------------

            exists = False

            for modular_obj in modular_collection.objects:

                if modular_obj.type != 'MESH':
                    continue

                if modular_obj.data == obj.data:
                    exists = True
                    break

            if exists:
                skipped += 1
                continue

            # ---------------------------------------------
            # Create linked modular object
            # ---------------------------------------------

            new_obj = obj.copy()

            # Share the same mesh datablock
            new_obj.data = obj.data

            # Preserve transform
            new_obj.matrix_world = obj.matrix_world.copy()

            # Naming
            new_obj.name = obj.name + "_LS_modular"

            # Link only to LS_modular_collection
            modular_collection.objects.link(new_obj)

            for col in list(new_obj.users_collection):
                if col != modular_collection:
                    col.objects.unlink(new_obj)

            created += 1

        self.report(
            {'INFO'},
            f"Created {created} modular object(s)."
        )

        return {'FINISHED'}
    

# ---------------------------------------------------------
# Build Instances
# ---------------------------------------------------------

class LS_OT_build_instances(bpy.types.Operator):
    bl_idname = "ls.build_instances"
    bl_label = "LS Build Instances"
    bl_description = "Placeholder for building instances"
    

    @staticmethod
    def compare(obj_a, obj_b, tolerance=1e-6):

        print(f"Comparing {obj_a.name} with {obj_b.name}")

        mesh_a = obj_a.data
        mesh_b = obj_b.data

        # -------------------------------------------------
        # Vertex Count
        # -------------------------------------------------

        if len(mesh_a.vertices) != len(mesh_b.vertices):
            return False

        # -------------------------------------------------
        # Edge Count
        # -------------------------------------------------

        if len(mesh_a.edges) != len(mesh_b.edges):
            return False

        # -------------------------------------------------
        # Face Count
        # -------------------------------------------------

        if len(mesh_a.polygons) != len(mesh_b.polygons):
            return False

        # -------------------------------------------------
        # Bounding Box
        # -------------------------------------------------

        min_a = [min(v.co[i] for v in mesh_a.vertices) for i in range(3)]
        max_a = [max(v.co[i] for v in mesh_a.vertices) for i in range(3)]

        min_b = [min(v.co[i] for v in mesh_b.vertices) for i in range(3)]
        max_b = [max(v.co[i] for v in mesh_b.vertices) for i in range(3)]

        for i in range(3):

            if abs(min_a[i] - min_b[i]) > tolerance:
                return False

            if abs(max_a[i] - max_b[i]) > tolerance:
                return False

        # -------------------------------------------------
        # Surface Area
        # -------------------------------------------------

        bm = bmesh.new()
        bm.from_mesh(mesh_a)
        area_a = sum(f.calc_area() for f in bm.faces)
        bm.free()

        bm = bmesh.new()
        bm.from_mesh(mesh_b)
        area_b = sum(f.calc_area() for f in bm.faces)
        bm.free()

        if abs(area_a - area_b) > tolerance:
            return False

        # -------------------------------------------------
        # Volume
        # -------------------------------------------------

        bm = bmesh.new()
        bm.from_mesh(mesh_a)
        volume_a = bm.calc_volume(signed=False)
        bm.free()

        bm = bmesh.new()
        bm.from_mesh(mesh_b)
        volume_b = bm.calc_volume(signed=False)
        bm.free()

        if abs(volume_a - volume_b) > tolerance:
            return False

        # -------------------------------------------------
        # Vertex Positions
        # -------------------------------------------------

        for v1, v2 in zip(mesh_a.vertices, mesh_b.vertices):

            if (v1.co - v2.co).length > tolerance:
                return False

        return True

    @staticmethod
    def buildInstance(obj):

        scene_collection = bpy.data.collections.get("LS_scene_collection")

        if scene_collection is None:
            print("LS_scene_collection not found.")
            return

        for i in scene_collection.objects:

            # Must be a mesh
            if i.type != 'MESH':
                continue

            # Already sharing same mesh datablock
            if i.data == obj.data:
                # print("same datablock")
                continue

            # Compare geometry (placeholder)
            if LS_OT_build_instances.compare(i, obj):

                print(f"{i.name} linked to {obj.name}")

                i.data = obj.data

    def execute(self, context):

        selected = [
            obj for obj in context.selected_objects
            if obj.type == 'MESH'
        ]

        if len(selected) == 0:

            self.report(
                {'ERROR'},
                "Select objects to build instances."
            )

            return {'CANCELLED'}

        for obj in selected:
            LS_OT_build_instances.buildInstance(obj)

        self.report(
            {'INFO'},
            f"Built instances for {len(selected)} object(s)."
        )

        return {'FINISHED'}

# ---------------------------------------------------------
# Submenu
# ---------------------------------------------------------

class LS_MT_objects(bpy.types.Menu):
    bl_label = "LS_objects"
    bl_idname = "LS_MT_objects"

    def draw(self, context):

        layout = self.layout

        layout.operator(
            LS_OT_place_instances.bl_idname,
            text="LS_place_instances"
        )
        layout.separator()

        layout.operator(
            LS_OT_merge_objects.bl_idname,
            text="LS_merge_objects"
        )
        
        layout.separator()

        layout.operator(
            LS_OT_get_modular_objects.bl_idname,
            text="LS_get_modular_objects"
        )
        layout.separator()

        layout.operator(
            LS_OT_create_modular_objects.bl_idname,
            text="LS_create_modular_objects"
        )
        
        layout.separator()

        layout.operator(
            LS_OT_build_instances.bl_idname,
            text="LS_build_instances"
        )
        
        
        

# ---------------------------------------------------------
# Object Mode Right Click Menu
# ---------------------------------------------------------

def draw_menu(self, context):

    layout = self.layout

    layout.separator()

    layout.menu(LS_MT_objects.bl_idname)


# ---------------------------------------------------------
# Registration
# ---------------------------------------------------------

classes = (
    LS_OT_place_instances,
    LS_OT_merge_objects,
    LS_OT_get_modular_objects,
    LS_OT_create_modular_objects,
    LS_OT_build_instances,
    LS_MT_objects,
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object_context_menu.append(draw_menu)


def unregister():

    bpy.types.VIEW3D_MT_object_context_menu.remove(draw_menu)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)