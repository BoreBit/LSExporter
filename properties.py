import bpy
from bpy.app.handlers import persistent
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    PointerProperty,
    CollectionProperty,
    IntProperty,
)



# ---------------------------------------------------------
# Scene Data Item
# ---------------------------------------------------------

class LS_SceneDataItem(PropertyGroup):

    # Object reference (never changes unless object deleted)
    object_ref: PointerProperty(
        name="Object",
        type=bpy.types.Object
    )

    # Editable display/export name
    display_name: StringProperty(
        name="Scene Name",
        default=""
    )


classes = (
    LS_SceneDataItem,
)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ls_scene_data = CollectionProperty(
        type=LS_SceneDataItem
    )

    bpy.types.Scene.ls_scene_data_index = IntProperty()
    bpy.types.Scene.ls_export_path = StringProperty(
        name="Export Folder",
        subtype='DIR_PATH',
        default=""
    )
    


def unregister():

    del bpy.types.Scene.ls_scene_data
    del bpy.types.Scene.ls_scene_data_index
    del bpy.types.Scene.ls_export_path

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)