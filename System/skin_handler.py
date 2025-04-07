import maya.cmds as cmds
from System.file_handle import file_dialog_yaml, file_read_yaml


def save_skin(source_object):
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


def load_skin(skin_data, geometry):
    skin_cluster = cmds.listConnections(geometry, t="skinCluster")
    for vtx in skin_data[geometry]['Vertices'].keys():
        for influence, weight in skin_data[geometry]['Vertices'][vtx].items():
            cmds.skinPercent(skin_cluster[0], vtx, tv=[influence, weight], nrm=False)


def save_selected_skin_yaml():
    source_object = cmds.ls(sl=True)
    skin_data = save_skin(source_object)
    file_dialog_yaml("Save Skin Weights", "w", skin_data)


def load_selected_skin_yaml():
    skin_data = file_dialog_yaml("Load Skin Weights", "r")
    geometry = cmds.ls(sl=True)[0]
    load_skin(skin_data, geometry)


# TODO: remove unused influences
# TODO: prune wheights
# TODO: make file dialog to both load and save skins
