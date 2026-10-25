# LS Exporter

A Blender add-on designed to generate instance placement data and modular assets for use in Unreal Engine via the [LS Importer](https://github.com/BoreBit/LSImporter) plugin.

It exports instance placement data as CSV files and modular assets as FBX. The CSV files contain object transforms from Blender, which should be validated in Unreal Engine to ensure the expected placement and orientation.

## Setup

In the Outliner, `LS_modular_collection` holds all the modular (unique) pieces. These objects are not included in the scene generation data (their transforms will not be recorded in the CSV files). In File $\rightarrow$ Export, find LS Modular FBX (.fbx) to export the currently selected modular pieces as a single FBX file for import into Unreal Engine.

`LS_scene_collection` holds all the placed copies of the modular pieces. Note that the copies need not be instances; they can be complete duplicates. However, for the standard instance-matching and CSV export workflow, objects must share the same mesh datablock.

In the 3D Viewport sidebar (`N` panel), find the `LS` tab and the `LS Scene Exporter` panel to register source objects, view the registered items, and export CSV files containing transform data for matching mesh objects to your desired location.

## Tools

The add-on offers multiple tools to streamline this process. Below is a list of the available tools.

**In Object Mode:** Right-click in the 3D Viewport and find the `LS_objects` submenu near the bottom.

1. `LS_get_modular_objects`: In the current selection, keep one representative for each unique mesh datablock.
2. `LS_create_modular_objects`: Find unique mesh datablocks in the current selection and create representative objects in `LS_modular_collection`.
3. `LS_place_instances`: Place copies of additional selected objects at the locations of instances of the active object. For example, placing doorknobs on doors you've already placed. (Select the door first, then the doorknob. Note that the door copies should be in `LS_scene_collection`.)
4. `LS_merge_objects`: If you have instances of two objects and wish to join (`Ctrl + J`) them, this tool removes matching placed instances of the other selected mesh datablocks from `LS_scene_collection` before joining the selected objects.
5. `LS_build_instances`: If two objects look alike but are not yet instances of each other, use this tool to link their mesh data when their geometry passes the tool's comparison checks. (The relevant objects should be in `LS_scene_collection`.)

**In Edit Mode:** Right-click in the 3D Viewport and find the `LS_editor` submenu.

1. `LS_change_pivot`: By default, changing an object's mesh pivot can affect the placement of its linked instances. Use this tool to move the pivot to a selected vertex without intentionally displacing the linked instances. Select a single vertex of the object to use as the new pivot, then click `LS_change_pivot`.