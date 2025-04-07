import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import pymel.core as pm

# ------------------------Save--------------------------
dict = {}
lattice = pm.selected()[0]
lat_obj = cmds.ls(sl=True)[0]
# lat_parent = cmds.listRelatives(lat_obj, p=True)
lattice_pos = cmds.xform(lat_obj, q=True, t=True, ws=True)
lattice_rot = cmds.xform(lat_obj, q=True, ro=True, ws=True)
print(lattice_pos)
for index, point in enumerate(lattice.pt):
    list = []
    list.append(pm.pointPosition(point)[0])
    list.append(pm.pointPosition(point)[1])
    list.append(pm.pointPosition(point)[2])
    item = str(point)[len(str(point)) - 11:len(str(point))]
    dict[item] = list

# return dict, lattice_pos, lattice_rot
# --------------------------Load--------------------------------

lattice = pm.selected()[0]
lat_obj = cmds.ls(sl=True)[0]
# lat_parent = cmds.listRelatives(lat_obj, p=True)
print(lat_parent)
cmds.xform(lat_obj, t=lattice_pos, ws=True)
cmds.xform(lat_obj, ro=lattice_rot, ws=True)

for key in dict:
    print(key)
    cmds.select(str(lattice) + "." + key, r=True)
    cmds.move(dict[key][0], dict[key][1], dict[key][2], ws=True)