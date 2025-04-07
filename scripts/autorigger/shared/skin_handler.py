import maya.cmds as cmds
from scripts.autorigger.shared.file_handle import file_dialog_yaml, file_read_yaml


def get_skin_weights():
    """
    Get all skinned meshes in the scene and store into dictionary

    :return: dictionary containing all skin information to be saved (skin_data)
    """
    # list all meshes in the scene
    meshes = cmds.ls(type="mesh", long=True)

    # skin dictionary
    skin_data = {}

    for mesh_obj in meshes:
        # Get the transform node of the mesh
        transform = cmds.listRelatives(mesh_obj, parent=True, fullPath=True)[0]

        # Retrieves the history of the mesh, then filters for skin clusters.
        objHist = cmds.listHistory(transform, pdo=True)
        skinClusters = cmds.ls(objHist, type="skinCluster")

        if skinClusters:
            skin_cluster = skinClusters[0]

            # Get the influence objects (joints) affecting the skin cluster
            influences = cmds.skinCluster(skin_cluster, query=True, influence=True)

            # Prepare dictionary to store weights for this mesh
            skin_data[transform] = {'Vertices': {}}

            # Loop over each vertex and get its weight per influence
            vertex_count = cmds.polyEvaluate(mesh_obj, vertex=True)
            for vertex_index in range(vertex_count):

                vertex = '{}.vtx[{}]'.format(transform, vertex_index)
                skin_data[transform]['Vertices'][vertex] = {}
                weights = cmds.skinPercent(skin_cluster, vertex, query=True, value=True)

                for influence, weight in zip(influences, weights):
                    if weight != 0.0:
                        skin_data[transform]['Vertices'][vertex][influence] = weight

                    # influences.sort()

                    skin_data[transform]['Influences'] = influences

    return skin_data


def apply_skin_weights(skin_data):
    """
    Apply skin weights to meshes based on the skin_data dictionary.

    :param skin_data: Dictionary containing skin information to be applied
    """
    for transform, data in skin_data.items():
        # Check if the transform exists in the scene
        if not cmds.objExists(transform):
            print(f"Object {transform} does not exist in the scene. Skipping...")
            continue

        # Get the influences (joints) affecting the mesh
        influences = data['Influences']

        # Check if there's an existing skinCluster, or create a new one
        skin_cluster = None
        objHist = cmds.listHistory(transform, pdo=True)
        skinClusters = cmds.ls(objHist, type="skinCluster")

        if skinClusters:
            skin_cluster = skinClusters[0]
        else:
            # Create a new skinCluster with the provided influences
            skin_cluster = cmds.skinCluster(influences, transform, toSelectedBones=True)[0]

        # Iterate over each vertex and apply the stored weights
        for vertex, vertex_weights in data['Vertices'].items():
            # Create a list of weights for the current vertex
            weight_list = []

            # Collect weights for each influence (joint)
            for influence in influences:
                weight_list.append(vertex_weights.get(influence, 0.0))  # Use 0.0 if no weight is stored

            # Normalize weights to ensure they sum to 1
            total_weight = sum(weight_list)
            if total_weight != 1.0 and total_weight != 0.0:
                weight_list = [w / total_weight for w in weight_list]

            # Apply the skin weights to the vertex
            cmds.skinPercent(skin_cluster, vertex, transformValue=list(zip(influences, weight_list)))

    print("Skin weights applied successfully.")


def load_skin_selected(skin_data, geometry):
    skin_cluster = cmds.listConnections(geometry, t="skinCluster")
    for vtx in skin_data[geometry]['Vertices'].keys():
        for influence, weight in skin_data[geometry]['Vertices'][vtx].items():
            cmds.skinPercent(skin_cluster[0], vtx, tv=[influence, weight], nrm=False)


def save_skin_yaml():
    skin_data = get_skin_weights()
    file_dialog_yaml("Save Skin Weights", "w", skin_data)


def load_skin_yaml():
    skin_data = file_dialog_yaml("Load Skin Weights", "r")
    apply_skin_weights(skin_data)


def load_skin_yaml_with_file(filepath):
    skin_data = file_read_yaml(filepath)
    apply_skin_weights(skin_data)


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





