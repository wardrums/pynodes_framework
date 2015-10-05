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
from bpy.types import PropertyGroup
from bpy_types import StructRNA, RNAMetaPropGroup, OrderedDictMini
from bpy.props import *
from collections import OrderedDict
from pynodes_framework.parameter import *
from pynodes_framework.idref import MetaIDRefContainer


class MetaNodeSocket(RNAMetaPropGroup):
    def __new__(cls, name, bases, classdict):
        socket_cls = RNAMetaPropGroup.__new__(cls, name, bases, classdict)

        # define the "datatype" property
        socket_cls.datatype = EnumProperty(name="Data Type", items=parameter_enum(socket_cls.parameter_types))

        return socket_cls

class NodeSocket(metaclass=MetaNodeSocket):
    parameter_types = [] # should be defined in subclasses

    # shortcut to the property value, needs explicit node
    def value(self, node):
        return getattr(node.socket_data(), self.identifier)

    @property
    def is_output(self):
        return self.in_out == 'OUT'

    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            node.find_node_parameter(self.is_output, self.identifier).draw_socket(layout, node.socket_data(), self.identifier, text)

    def draw_color(self, context, node):
        return node.find_node_parameter(self.is_output, self.identifier).color


# standard socket type if no additional tweaking is needed
class PyNodesSocket(bpy.types.NodeSocket, NodeSocket):
    """ Generic pynodes socket """
    bl_idname = "PyNodesSocket"

    # Use all basic types by default.
    # NodeSocket subclasses can define their own set for customization.
    parameter_types = parameter_types_all


class NodeTree():
    pass


class NodeOrderedDict(dict):
    def __init__(self, *args):
        dict.__init__(self, args)
        self.node_parameters = OrderedDict()

    def __setitem__(self, key, value):
        if isinstance(value, NodeParameter):
            # use the attribute name as the parameter identifier
            value.identifier = key
            # make sure the param replacement is appended at the end
            if key in self.node_parameters:
                del self.node_parameters[key]
            self.node_parameters[key] = value
        else:
            dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        if key in self.node_parameters:
            del self.node_parameters[key]


class MetaNode(MetaIDRefContainer(RNAMetaPropGroup)):
    def __prepare__(name, bases, **kwargs):
        return NodeOrderedDict()

    def _verify_parameter(self, param):
        if param.prop:
            setattr(self, param.identifier, param.prop)

    def __setattr__(self, key, value):
        if isinstance(value, NodeParameter):
            # use the attribute name as the parameter identifier
            value.identifier = key
            # make sure the param replacement is appended at the end
            if key in self._node_type_parameters:
                del self._node_type_parameters[key]
            self._node_type_parameters[key] = value

            self._verify_parameter(value)
        else:
            super().__setattr__(key, value)

    def __new__(cls, name, bases, classdict):
        # Wrapper for node.init, to add sockets from templates
        init_base = classdict.get('init', None)
        def init_node(self, context):
            if init_base:
                init_base(self, context)
            self._verify_sockets()
        classdict["init"] = init_node

        if classdict.__class__ is NodeOrderedDict:
            node_type_parameters = classdict.node_parameters
        else:
            node_type_parameters = OrderedDict()
        classdict["_node_type_parameters"] = node_type_parameters

        nodecls = super().__new__(cls, name, bases, classdict)

        # Add properties from node type parameters
        for param in node_type_parameters:
            nodecls._verify_parameter(param)

        return nodecls


class Node(metaclass=MetaNode):
    def _find_input(self, identifier):
        for i, socket in enumerate(self.inputs):
            if socket.identifier == identifier:
                return i, socket
        return -1, None
    def _find_output(self, identifier):
        for i, socket in enumerate(self.outputs):
            if socket.identifier == identifier:
                return i, socket
        return -1, None

    def socket_data(self):
        return self

    def node_parameters(self, output):
        for param in self._node_type_parameters.values():
            if param.is_output == output:
                yield param

    def find_node_parameter(self, output, identifier):
        for param in self.node_parameters(output):
            if param.identifier == identifier:
                return param
        raise KeyError("NodeParameter %r not found in %s" % (identifier, "outputs" if output else "inputs"))

    def _verify_sockets(self):
        for output in {False, True}:
            if output:
                sockets = self.outputs
                find_socket = self._find_output
            else:
                sockets = self.inputs
                find_socket = self._find_input

            unused = { socket for socket in sockets }

            for i, param in enumerate(self.node_parameters(output)):
                if not param.use_socket:
                    continue

                pos, socket = find_socket(param.name)
                if socket:
                    param.verify_socket(socket)
                    sockets.move(pos, i)

                    unused.remove(socket)
                else:
                    socket = param.make_socket(self, output)
                    # socket gets appended at the end, move to correct position
                    sockets.move(len(sockets)-1, i)

            # remove unused old sockets
            # XXX unset old properties here!
            for socket in unused:
                sockets.remove(socket)


def register():
    bpy.utils.register_class(PyNodesSocket)

def unregister():
    bpy.utils.unregister_class(PyNodesSocket)
