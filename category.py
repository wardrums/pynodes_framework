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

import nodeitems_utils

class NodeCategorizer():
    """ Decorator class to simplify node category definition """

    def __init__(self, nodetree_cls):
        self.nodetree_cls = nodetree_cls
        # stores a temporary category:classes map for registering categories
        # actual categories are created in register
        self.node_items = {}

    def __call__(self, category):
        def node_item_deco(cls):
            cat = self.node_items.get(category, None)
            if cat is None:
                cat = []
                self.node_items[category] = cat
            cat.append(cls)
            return cls
        return node_item_deco

    def register(self):
        class PyNodesCategory(nodeitems_utils.NodeCategory):
            @classmethod
            def poll(cls, context):
                space = context.space_data
                if not (space.type == 'NODE_EDITOR' and space.tree_type == self.nodetree_cls.bl_idname):
                    return False
                return True

        node_category_items = lambda node_classes : [ nodeitems_utils.NodeItem(getattr(cls, "bl_idname", cls.__name__)) for cls in node_classes ]
        node_categories = [ PyNodesCategory(name, name, items=node_category_items(node_classes)) for name, node_classes in self.node_items.items() ]
        nodeitems_utils.register_node_categories(self.nodetree_cls.bl_idname, node_categories)

    def unregister(self):
        nodeitems_utils.unregister_node_categories(self.nodetree_cls.bl_idname)
