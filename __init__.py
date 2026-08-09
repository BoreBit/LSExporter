bl_info = {
    "name": "LS Scene Exporter",
    "author": "LS Studio",
    "version": (0, 1, 1),
    "blender": (5, 1, 0),
    "category": "Import-Export",
}

from . import properties
from . import operators
from . import ui
from . import outliner_menu
from . import LS_editor
from . import LS_objects

# import properties
# import operators
# import ui
# import outliner_menu
# import LS_editor
# import LS_objects


def register():

    properties.register()
    operators.register()
    ui.register()
    outliner_menu.register()
    LS_editor.register()
    LS_objects.register()


def unregister():

    LS_objects.unregister()
    LS_editor.unregister()
    outliner_menu.unregister()
    ui.unregister()
    operators.unregister()
    properties.unregister()
    


if __name__ == "__main__":
    register()