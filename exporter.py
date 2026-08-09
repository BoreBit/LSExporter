import bpy
import csv
import math
import os
import re


def make_datasheet(item):

    scene = bpy.context.scene

    folder = bpy.path.abspath(scene.ls_export_path)

    # Sanitize filename
    safe_name = re.sub(r'[^A-Za-z0-9_]', '_', item.display_name)

    # Optional: collapse multiple underscores
    safe_name = re.sub(r'_+', '_', safe_name)

    # Optional: remove leading/trailing underscores
    safe_name = safe_name.strip('_')

    datasheet = f"SceneData_{safe_name}.csv"

    filepath = os.path.join(folder, datasheet)

    # --------------------------------------------------------
    # Create LS_scene_collection if it doesn't exist
    # --------------------------------------------------------

    collection = bpy.data.collections.get("LS_scene_collection")

    if collection is None:
        collection = bpy.data.collections.new("LS_scene_collection")
        bpy.context.scene.collection.children.link(collection)

    # --------------------------------------------------------

    col = [
        '',
        'id',
        'tx',
        'ty',
        'tz',
        'rx',
        'ry',
        'rz',
        'sx',
        'sy',
        'sz'
    ]
    
    c=0

    with open(filepath, 'w', newline='') as f:

        writer = csv.writer(f)
        writer.writerow(col)

        # Mesh datablock of current SceneData object
        mesh = item.object_ref.data

        for obj in collection.objects:

            if obj.type != 'MESH':
                continue

            if obj.data != mesh:
                continue

            data = []

            # First column (blank column in csv)
            data.append(c)
            c+=1

            # ID
            data.append(obj.name)

            # Translation (m -> cm)
            data.append(obj.location.x * 100)
            data.append(obj.location.y * 100)
            data.append(obj.location.z * 100)

            # Rotation
            data.append(math.degrees(obj.rotation_euler.x))
            data.append(math.degrees(obj.rotation_euler.y))
            data.append(math.degrees(obj.rotation_euler.z))

            # Scale
            data.append(obj.scale.x)
            data.append(-obj.scale.y)
            data.append(obj.scale.z)

            writer.writerow(data)

    print(datasheet, "created")