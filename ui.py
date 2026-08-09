import bpy


class LS_UL_SceneDataList(bpy.types.UIList):

    def draw_item(
        self,
        context,
        layout,
        data,
        item,
        icon,
        active_data,
        active_propname,
        index,
    ):

        row = layout.row(align=True)

        row.prop(item, "display_name", text="")

        op = row.operator(
            "ls.execute_scene_data",
            text="",
            icon='PLAY'
        )
        op.index = index

        op = row.operator(
            "ls.remove_scene_data",
            text="",
            icon='X'
        )
        op.index = index
        
        


class LS_PT_SceneExporter(bpy.types.Panel):

    bl_label = "LS Scene Exporter"
    bl_idname = "LS_PT_scene_exporter"

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "LS"

    def draw(self, context):

        layout = self.layout
        scene = context.scene
        
        layout.prop(
            scene,
            "ls_export_path",
            text="Export Folder"
        )
        
        layout.separator()

        layout.template_list(
            "LS_UL_SceneDataList",
            "",
            scene,
            "ls_scene_data",
            scene,
            "ls_scene_data_index"
        )
        
        layout.separator()

        layout.operator(
            "ls.execute_all_scene_data",
            icon='PLAY'
        )
        
        layout.operator(
            "ls.clear_scene_data",
            text="Clear All",
            icon='TRASH'
        )
    
        

        



classes = (
    LS_UL_SceneDataList,
    LS_PT_SceneExporter,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)