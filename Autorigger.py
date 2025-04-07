from maya.api import OpenMaya
from scripts.autorigger.ui.Autorigger_menu import menu

maya_useNewAPI = True


class Autorigger():
    """My Custom rig tool."""
    # Maya provides the node ids from
    # 0x00000000 to 0x0007ffff
    # for users to customize.
    type_id = OpenMaya.MTypeId(0x00006000)
    type_name = "autoRigger"

    @classmethod
    def initialize(cls):
        """Call the rig menu."""
        menu()

    @classmethod
    def creator(cls):
        """Create class instance.

        Returns:
            Autorigger: instance of this class.
        """
        return cls()


def initializePlugin(plugin):
    """Called when plugin is loaded.

    Args:
        plugin (MObject): The plugin.
    """
    plugin_fn = OpenMaya.MFnPlugin(plugin, "Reberson Alves da Silva", "0.0.1")

    try:
        plugin_fn.registerNode(
            Autorigger.type_name,
            Autorigger.type_id,
            Autorigger.creator,
            Autorigger.initialize,
        )
    except:
        print("failed to register node {0}".format(Autorigger.type_name))
        raise


def uninitializePlugin(plugin):
    """Called when plugin is unloaded.

    Args:
        plugin (MObject): The plugin.
    """
    plugin_fn = OpenMaya.MFnPlugin(plugin)

    try:
        plugin_fn.deregisterNode(Autorigger.type_id)
    except:
        print("failed to deregister node {0}".format(Autorigger.type_name))
        raise
