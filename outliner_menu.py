import bpy


def draw_ls_menu(self, context):

    layout = self.layout

    layout.separator()

    layout.operator(
        "ls.add_scene_data",
        icon='OUTLINER_OB_EMPTY'
    )


def register():

    bpy.types.OUTLINER_MT_object.append(draw_ls_menu)


def unregister():

    bpy.types.OUTLINER_MT_object.remove(draw_ls_menu)