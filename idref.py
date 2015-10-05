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
from bpy_types import RNAMetaPropGroup

def get_idtype_list_prop(idtype):
    typemap = {
        'ACTION'            : 'actions',
        'ARMATURE'          : 'armatures',
        'BRUSH'             : 'brushes',
        'CAMERA'            : 'cameras',
        'CURVE'             : 'curves',
        'FONT'              : 'fonts',
        'GREASE_PENCIL'     : 'grease_pencil',
        'GROUP'             : 'groups',
        'IMAGE'             : 'images',
        'LAMP'              : 'lamps',
        'LATTICE'           : 'lattices',
        'LIBRARY'           : 'libraries',
        'MASK'              : 'masks',
        'MATERIAL'          : 'materials',
        'MESH'              : 'meshes',
        'METABALL'          : 'metaballs',
        'MOVIECLIP'         : 'movieclips',
        'NODE_GROUP'        : 'node_groups',
        'OBJECT'            : 'objects',
        'PARTICLES'         : 'particles',
        'SCENE'             : 'scenes',
        'SCREEN'            : 'screens',
        'SCRIPT'            : 'scripts',
        'SHAPE_KEY'         : 'shape_keys',
        'SOUND'             : 'sounds',
        'SPEAKER'           : 'speakers',
        'TEXT'              : 'texts',
        'TEXTURE'           : 'textures',
        'WINDOW_MANAGER'    : 'window_managers',
        'WORLD'             : 'worlds',
        }
    return typemap[idtype]

def get_id_path(p):
    pid = p.id_data
    return(repr(pid))

def get_full_path(p):
    path = get_id_path(p)
    if p != p.id_data:
        path = "%s.%s" % (path, p.path_from_id())
    return path

def get_idtype_list(idtype):
    prop = get_idtype_list_prop(idtype)
    return lambda: getattr(bpy.data, prop, [])

def bpy_register_idref(cls, attr, idrefprop):
    idlist = get_idtype_list(idrefprop.idtype)
    name_attr = "%s__name__" % attr
    idtype_attr = "%s__idtype__" % attr

    setattr(cls, idtype_attr, idrefprop.idtype)

    def prop_get_name(self):
        return self.get(name_attr, "")

    def prop_set_name(self, value):
        idvalue = idlist().get(value, None)
        if idvalue is not None:
            if idrefprop.poll and not idrefprop.poll(self, idvalue):
                return
        if idvalue is not None or (not value and 'NEVER_NULL' not in idrefprop.options):
            self[name_attr] = value
        if idvalue is not None and 'FAKE_USER' in idrefprop.options:
            idvalue.use_fake_user = True

    setattr(cls, name_attr, bpy.props.StringProperty(
        name="%s ID Name" % idrefprop.name,
        description="ID data block name for pseudo IDRef pointer",
        options={'HIDDEN'} | (idrefprop.options & {'ANIMATABLE', 'SKIP_SAVE', 'LIBRARY_EDITABLE'}),
        update=idrefprop.update,
        get=prop_get_name,
        set=prop_set_name,
        ))

    def prop_get(self):
        name = self.get(name_attr, "")
        value = idlist().get(name, None)
        # Reset the name idproperty if invalid
        # XXX this is not 100% reliable, but better than keeping invalid names around
        if value is None:
            self[name_attr] = ""
        return value

    def prop_set(self, value):
        if value is None:
            if 'NEVER_NULL' in idrefprop.options:
                return
            del self[name_attr]
        else:
            if idrefprop.poll and not idrefprop.poll(self, value):
                return
            if value.name not in idlist():
                return
            if 'FAKE_USER' in idrefprop.options:
                value.use_fake_user = True
            self[name_attr] = value.name

    def prop_del(self):
        delattr(self, name_attr)
        delattr(self, collection_attr)

    prop = property(prop_get, prop_set, prop_del, idrefprop.description)
    # Note: replaces the temporary IDRefProperty item!            
    setattr(cls, attr, prop)

def bpy_unregister_idref(cls, attr):
    delattr(cls, attr)


def MetaIDRefContainer(base=type):
    class MetaWrap(base):
        # setattr wrapper to register new IDRefProperty
        def __setattr__(self, key, value):
            if isinstance(value, IDRefProperty):
                bpy_register_idref(self, key, value)
            else:
                super().__setattr__(key, value)

        def __new__(cls, name, bases, classdict):
            container_cls = base.__new__(cls, name, bases, classdict)

            idref_items = [(attr, item) for attr, item in container_cls.__dict__.items() if isinstance(item, IDRefProperty)]
            for attr, item in idref_items:
                bpy_register_idref(container_cls, attr, item)

            return container_cls
    return MetaWrap


class IDRefProperty():
    def __init__(self, name="", description="", idtype='OBJECT', options={'ANIMATABLE', 'FAKE_USER'}, update=None, poll=None):
        self.name = name
        self.description = description
        self.idtype = idtype
        self.options = options
        self.update = update
        self.poll = poll

# XXX could be injected into UILayout as a template
def draw_idref(layout, data, prop, text=""):
    row = layout.row(align=True)
    idtype = getattr(data, "%s__idtype__" % prop)
    row.prop_search(data, "%s__name__" % prop, bpy.data, get_idtype_list_prop(idtype), text=text)

