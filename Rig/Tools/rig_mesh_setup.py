import maya.cmds as cmds


def move_meshes():
    """Grab all Mesh groups in the scene and move into geometry group"""

    meshes = cmds.ls(type="mesh")
    mesh_parents = []

    for mesh in meshes:
        path = cmds.listRelatives(mesh, ap=True, f=True)[0]
        obj_first = path.split("|")[1]
        if obj_first not in mesh_parents:
            mesh_parents.append(obj_first)

    for parent_item in mesh_parents:
        cmds.parent(parent_item, "geometry")