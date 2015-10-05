# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
from pynodes_framework import *
from pynodes_framework.node_param import NodeParamFloat

class MathNodeTree(bpy.types.NodeTree, node_base.NodeTree):
    bl_idname = "MathNodeTree"
    bl_icon = 'PLUS'
    bl_label = "Math"

math_node_category = node_category.NodeCategorizer(MathNodeTree)

@math_node_category("Arithmetic")
class AddNode(bpy.types.Node, node_base.Node):
    bl_idname = "MathNodeAdd"
    bl_label = "Add"

    input_a = NodeParamFloat(label="Value")
    input_b = NodeParamFloat(label="Value")
    result = NodeParamFloat(label="Result", is_output=True)

@math_node_category("Arithmetic")
class SubtractNode(bpy.types.Node, node_base.Node):
    bl_idname = "MathNodeSubtract"
    bl_label = "Subtract"

    input_a = NodeParamFloat(label="Value")
    input_b = NodeParamFloat(label="Value")
    result = NodeParamFloat(label="Result", is_output=True)


def register():
    bpy.utils.register_module(__name__)

    math_node_category.register()

def unregister():
    math_node_category.unregister()

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
