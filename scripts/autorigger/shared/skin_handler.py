import maya.cmds as cmds
from scripts.autorigger.shared.file_handle import file_dialog_yaml, file_read_yaml


def save_skin(source_object): # works only for single mesh skin
    skin_data = {}
    geometry = cmds.listRelatives(source_object)[0]
    skin_cluster = cmds.listConnections(geometry, t="skinCluster")
    influences = cmds.skinCluster(skin_cluster, query=True, influence=True)
    vertex_count = cmds.polyEvaluate(geometry, vertex=True)
    skin_data[geometry] = {'Vertices': {}}
    for vertex_index in range(vertex_count):
        vertex = '{}.vtx[{}]'.format(geometry, vertex_index)
        skin_data[geometry]['Vertices'][vertex] = {}

        weights = cmds.skinPercent(skin_cluster[0], vertex, query=True, value=True)
        for influence, weight in zip(influences, weights):
            if weight != 0.0:
                skin_data[geometry]['Vertices'][vertex][influence] = weight

            influences.sort()

            skin_data[geometry]['Influences'] = influences

    return skin_data


def save_skin_weights():
    meshes = cmds.listRelatives('geometry')
    skinned_meshes = []
    skin_data = {}
    for obj in meshes:
        objHist = cmds.listHistory(obj, pdo=True)
        skinCluster = cmds.ls(objHist, type="skinCluster") or [None]
        scluster = skinCluster[0]
        if scluster:
            skinned_meshes.append(obj)
            influences = cmds.skinCluster(scluster, query=True, influence=True)
            vertex_count = cmds.polyEvaluate(obj, vertex=True)
            skin_data[obj] = {'Vertices': {}}
            for vertex_index in range(vertex_count):
                vertex = '{}.vtx[{}]'.format(obj, vertex_index)
                skin_data[obj]['Vertices'][vertex] = {}

                weights = cmds.skinPercent(scluster, vertex, query=True, value=True)
                for influence, weight in zip(influences, weights):
                    if weight != 0.0:
                        skin_data[obj]['Vertices'][vertex][influence] = weight

                    # influences.sort()

                    skin_data[obj]['Influences'] = influences

    return skin_data


# def load_skin_weights(skin_data):
#     meshes = cmds.listRelatives('geometry')
#     for obj in meshes:
#         objHist = cmds.listHistory(obj, pdo=True)
#         skinCluster = cmds.ls(objHist, type="skinCluster") or [None]
#         scluster = skinCluster[0]
#         if scluster:
#             # set normalization to post
#             cmds.skinCluster(scluster, e=True, nw=2)
#
#             # Now assign the loaded weights
#             for vtx in skin_data[obj]['Vertices'].keys():
#                 for influence, weight in skin_data[obj]['Vertices'][vtx].items():
#                     cmds.skinPercent(scluster, vtx, tv=[influence, weight], nrm=False, r=False)

# Gemini Solution Below
def load_skin_weights(skin_data):
    meshes = cmds.listRelatives('geometry')
    for obj in meshes:
        objHist = cmds.listHistory(obj, pdo=True)
        skinCluster = cmds.ls(objHist, type="skinCluster") or [None]
        scluster = skinCluster[0]
        if scluster:
            # Assign the loaded weights
            for vtx in skin_data[obj]['Vertices'].keys():
                weights = []
                for influence, weight in skin_data[obj]['Vertices'][vtx].items():
                    weights.append([influence, weight])
                cmds.skinPercent(scluster, vtx, tv=weights, nrm=True)
        remove_unused_influences(obj)


def load_skin(skin_data, geometry):
    skin_cluster = cmds.listConnections(geometry, t="skinCluster")
    for vtx in skin_data[geometry]['Vertices'].keys():
        for influence, weight in skin_data[geometry]['Vertices'][vtx].items():
            cmds.skinPercent(skin_cluster[0], vtx, tv=[influence, weight], nrm=False)


def save_selected_skin_yaml():
    source_object = cmds.ls(sl=True)
    skin_data = save_skin(source_object)
    file_dialog_yaml("Save Skin Weights", "w", skin_data)


def save_skin_yaml():
    skin_data = save_skin_weights()
    file_dialog_yaml("Save Skin Weights", "w", skin_data)


def load_selected_skin_yaml():
    skin_data = file_dialog_yaml("Load Skin Weights", "r")
    geometry = cmds.ls(sl=True)[0]
    load_skin(skin_data, geometry)


def load_skin_yaml():
    skin_data = file_dialog_yaml("Load Skin Weights", "r")
    load_skin_weights(skin_data)


def load_skin_yaml_with_file(filepath):
    skin_data = file_read_yaml(filepath)
    load_skin_weights(skin_data)


def remove_unused_influences(mesh):
    """
    Removes unused skin influences from the specified mesh.

    Args:
        mesh (str): The name of the mesh.
    """

    objHist = cmds.listHistory(mesh, pdo=True)
    skin_cluster_list = cmds.ls(objHist, type="skinCluster") or [None]
    skin_cluster = skin_cluster_list[0]

    if skin_cluster:
        all_influences = cmds.skinCluster(skin_cluster, query=True, influence=True)
        unused_influences = []
        for influence in all_influences:
            # Get all vertices of the mesh
            vertices = cmds.polyListComponentConversion(mesh, toVertex=True)
            unused_influence = True
            for vertex in vertices:
                weight = cmds.skinPercent(skin_cluster, vertex, transform=influence, query=True, value=True)
                if weight > 0:
                    unused_influence = False
                    break
            if unused_influence:
                unused_influences.append(influence)

        if unused_influences:
            cmds.skinCluster(skin_cluster, edit=True, removeInfluence=unused_influences)





