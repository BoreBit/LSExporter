import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty

from . import exporter
# import exporter

class LS_OT_AddSceneData(bpy.types.Operator):
    bl_idname = "ls.add_scene_data"
    bl_label = "Add in LS_scene_data"

    def execute(self, context):

        scene = context.scene

        for obj in context.selected_objects:

            # avoid duplicates
            exists = False

            for item in scene.ls_scene_data:
                if item.object_ref == obj:
                    exists = True
                    break

            if exists:
                continue

            item = scene.ls_scene_data.add()
            item.object_ref = obj
            item.display_name = obj.name

        return {'FINISHED'}


class LS_OT_RemoveSceneData(bpy.types.Operator):
    bl_idname = "ls.remove_scene_data"
    bl_label = "Remove"

    index: bpy.props.IntProperty()

    def execute(self, context):

        context.scene.ls_scene_data.remove(self.index)

        return {'FINISHED'}


class LS_OT_ExecuteSceneData(bpy.types.Operator):
    bl_idname = "ls.execute_scene_data"
    bl_label = "Execute Scene Data"

    index: bpy.props.IntProperty()

    def execute(self, context):

        scene = context.scene

        if not scene.ls_export_path:
            bpy.ops.ls.select_export_folder('INVOKE_DEFAULT')
            return {'CANCELLED'}

        item = scene.ls_scene_data[self.index]
        
        # Keep display name synchronized with object name
        if item.object_ref and item.display_name != item.object_ref.name:
            item.display_name = item.object_ref.name

        exporter.make_datasheet(item)

        self.report(
            {'INFO'},
            f"SceneData '{item.display_name}' exported successfully."
        )

        return {'FINISHED'}


class LS_OT_ExecuteAllSceneData(bpy.types.Operator):
    bl_idname = "ls.execute_all_scene_data"
    bl_label = "Execute All"

    def execute(self, context):

        scene = context.scene

        if not scene.ls_export_path:
            bpy.ops.ls.select_export_folder('INVOKE_DEFAULT')
            return {'CANCELLED'}

        count = 0

        for item in scene.ls_scene_data:
            
        # Keep display name synchronized with object name
            if item.object_ref and item.display_name != item.object_ref.name:
                item.display_name = item.object_ref.name
                
            exporter.make_datasheet(item)
            print(f"{item.display_name}_executed")
            count += 1

        self.report(
            {'INFO'},
            f"Successfully exported {count} SceneData file(s)."
        )

        return {'FINISHED'}
    
class LS_OT_SelectExportFolder(bpy.types.Operator):
    bl_idname = "ls.select_export_folder"
    bl_label = "Select Export Folder"

    directory: StringProperty(
        subtype='DIR_PATH'
    )

    def execute(self, context):

        context.scene.ls_export_path = self.directory

        self.report({'INFO'}, f"Export folder set to:\n{self.directory}")

        return {'FINISHED'}

    def invoke(self, context, event):

        context.window_manager.fileselect_add(self)

        return {'RUNNING_MODAL'}

class EXPORT_SCENE_OT_ls_modular_fbx(Operator, ExportHelper):
    bl_idname = "export_scene.ls_modular_fbx"
    bl_label = "LS Modular FBX"

    filename_ext = ".fbx"

    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'}
    )
    
    

    def execute(self, context):

        selected = context.selected_objects

        if not selected:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}

        # ---------------------------------
        # Save original transforms
        # ---------------------------------

        transforms = {}

        for obj in selected:
            transforms[obj] = obj.matrix_world.copy()

        # ---------------------------------
        # Move selected objects to origin
        # (simple version)
        # ---------------------------------

        for obj in selected:
            obj.location = (0.0, 0.0, 0.0)
            obj.rotation_euler = (0.0, 0.0, 0.0)
            obj.scale = (1.0, 1.0, 1.0)

        # Force scene update
        context.view_layer.update()

        # ---------------------------------
        # Export FBX
        # ---------------------------------

        bpy.ops.export_scene.fbx(
            filepath=self.filepath,
            use_selection=True,
            mesh_smooth_type='FACE'
        )

        # ---------------------------------
        # Restore transforms
        # ---------------------------------

        for obj, matrix in transforms.items():
            obj.matrix_world = matrix

        context.view_layer.update()

        self.report({'INFO'}, "FBX Exported")

        return {'FINISHED'}

class LS_OT_ClearSceneData(bpy.types.Operator):
    bl_idname = "ls.clear_scene_data"
    bl_label = "Clear All"
    bl_description = "Remove all Scene Data entries"

    def execute(self, context):

        scene = context.scene

        scene.ls_scene_data.clear()

        self.report(
            {'INFO'},
            "All Scene Data entries cleared."
        )

        return {'FINISHED'}


classes = (
    LS_OT_AddSceneData,
    LS_OT_RemoveSceneData,
    LS_OT_ExecuteSceneData,
    LS_OT_ExecuteAllSceneData,
    LS_OT_SelectExportFolder,
    EXPORT_SCENE_OT_ls_modular_fbx,
    LS_OT_ClearSceneData,
)

def menu_func_export(self, context):
        self.layout.operator(
            EXPORT_SCENE_OT_ls_modular_fbx.bl_idname,
            text="LS Modular FBX (.fbx)"
        )
        



def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)