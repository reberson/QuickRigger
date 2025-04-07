import maya.cmds as cmds
from scripts.autorigger.shared.utils import calculatePVPosition as calc_pv
from scripts.autorigger.shared.utils import connect_point_constraint, connect_orient_constraint, mirror_object
from scripts.autorigger.shared.utils import disconnect_shape_drawinfo
from scripts.autorigger.resources.definitions import CONTROLS_DIR
from scripts.autorigger.shared.file_handle import file_read_yaml, import_curve
from scripts.autorigger.shared.utils import create_stretch, create_twist_joint


def create_wing_rig(dict, twist=True):
    # List all necessary joints
    arm_joints = ["Shoulder_R", "Elbow_R", "Wrist_R", "Shoulder_L", "Elbow_L", "Wrist_L"]
    arm_switchers = ["ikfk_arm_R", "ikfk_arm_L"]
    layer1_objects = []

    wing_prefix = "Wing_"  # change to whatever it's best

    arm_joints = [wing_prefix + joint for joint in arm_joints]
    arm_switchers = [wing_prefix + joint for joint in arm_switchers]
