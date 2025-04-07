import maya.cmds as cmds


def move_meshes():
    """Grab all Mesh groups in the scene and move into geometry group, it keeps the transform hierarchy intact"""

    meshes = cmds.ls(type="mesh")
    mesh_parents = []

    for mesh in meshes:
        path = cmds.listRelatives(mesh, ap=True, f=True)[0]
        obj_first = path.split("|")[1]
        if obj_first not in mesh_parents:
            mesh_parents.append(obj_first)

    for parent_item in mesh_parents:
        cmds.parent(parent_item, "geometry")


def list_deformation_joints(grp_def):
    defjnts = cmds.listRelatives(grp_def, ad=True) or []
    # Remove joints that we are sure it does not need to be bound
    defjnts = [jnt for jnt in defjnts if not any(keyword in jnt.lower() for keyword in ["_end", "footsidein_", "footsideout_", "heel_"])]
    return defjnts


def list_mesh_objects(grp_geo):
    meshobj = []
    # Get all objects under the 'grp_geo' group
    geometries = cmds.listRelatives(grp_geo, ad=True) or []
    for obj in geometries:
        shapes = cmds.listRelatives(obj, shapes=True) or []
        if any(cmds.objectType(shape) == "mesh" for shape in shapes):
            meshobj.append(obj)
    return meshobj


def bind_mesh_to_joints(meshobj, defjnts):
    for mesh in meshobj:
        # Bind the mesh to the joints using the skinCluster command
        cmds.skinCluster(defjnts, mesh, toSelectedBones=True)
        print(f"Bound {mesh} to deformation joints")
