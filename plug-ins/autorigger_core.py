import maya.api.OpenMaya as om
import maya.cmds as cmds
import logging
from importlib.resources import files


__menu_node = None
maya_useNewAPI = None  # noqa: dummy informs Maya this plugin uses Maya Python API 2.0


def load_menu():
    global __menu_node


def unload_menu_item():
    global __menu_node


def load_plugin(plugin_name: str):
    if not cmds.pluginInfo(plugin_name, query=True, loaded=True):
        cmds.loadPlugin(plugin_name, quiet=True)
        cmds.pluginInfo(plugin_name, edit=True, autoload=True)
    if not cmds.pluginInfo(plugin_name, query=True, loaded=True):
        logging.warning(f"Failed to load plugin '{plugin_name}'")


def initializePlugin(plugin):  # noqa, camelCase required by Maya
    load_menu()


def uninitializePlugin(plugin):  # noqa, camelCase required by Maya
    unload_menu_item()
