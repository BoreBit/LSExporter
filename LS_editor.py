import bpy
import bmesh



# ---------------------------------------------------------
# Operator
# ---------------------------------------------------------

class LS_OT_change_pivot(bpy.types.Operator):
    bl_idname = "ls.change_pivot"
    bl_label = "LS Change Pivot"
    bl_description = "Move pivot to selected vertex while preserving all instances"

    @staticmethod
    def get_selected_or_first_vertex(obj):

        bm = bmesh.from_edit_mesh(obj.data)

        selected = [v for v in bm.verts if v.select]

        if len(selected) == 1:
            return selected[0].index

        return bm.verts[0].index

    @staticmethod
    def change_pivot(source_obj):

        mesh = source_obj.data

        vertex_index = LS_OT_change_pivot.get_selected_or_first_vertex(source_obj)

        pivot_local = mesh.vertices[vertex_index].co.copy()

        # Find every instance sharing this mesh
        instances = []

        for obj in bpy.data.objects:

            if obj.type != 'MESH':
                continue

            if obj.data == mesh:
                instances.append(obj)

        # Exit edit mode for this mesh so mesh data can be edited
        bpy.ops.object.mode_set(mode='OBJECT')

        # Move mesh vertices
        for v in mesh.vertices:
            v.co -= pivot_local

        mesh.update()

        # Offset every instance so nothing moves visually
        for obj in instances:

            offset = obj.matrix_world.to_3x3() @ pivot_local

            obj.location += offset

        # Return to Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')

        print(f"Pivot changed : {source_obj.name}")

    def execute(self, context):

        if context.mode != 'EDIT_MESH':
            self.report({'ERROR'}, "Run in Edit Mode.")
            return {'CANCELLED'}

        selected = [o for o in context.objects_in_mode if o.type == 'MESH']

        if not selected:
            self.report({'WARNING'}, "No mesh selected.")
            return {'CANCELLED'}

        for obj in selected:
            LS_OT_change_pivot.change_pivot(obj)

        self.report({'INFO'}, "Pivot changed.")

        return {'FINISHED'}



# ---------------------------------------------------------
# Menu
# ---------------------------------------------------------

class LS_MT_editor(bpy.types.Menu):
    bl_label = "LS_editor"
    bl_idname = "LS_MT_editor"

    def draw(self, context):

        layout = self.layout

        layout.operator(
            LS_OT_change_pivot.bl_idname,
            text="LS_change_pivot"
        )


# ---------------------------------------------------------
# Context Menu
# ---------------------------------------------------------

def draw_menu(self, context):

    self.layout.separator()
    self.layout.menu(LS_MT_editor.bl_idname)


# ---------------------------------------------------------
# Register
# ---------------------------------------------------------

classes = (
    LS_OT_change_pivot,
    LS_MT_editor,
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(draw_menu)


def unregister():

    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(draw_menu)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)