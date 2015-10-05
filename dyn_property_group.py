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

from bpy.props import PointerProperty
from bpy.types import PropertyGroup


### Dynamic PointerProperty ###

def bpy_register_dynpointer(cls, attr, dynptr_prop):
    def ptr_attr(t):
        return "%s__T%s" % (attr, t.__name__)
    types_attr = "%s__types" % attr

    for t in dynptr_prop.types:
        prop = PointerProperty(name=dynptr_prop.name, description=dynptr_prop.description, type=t)
        setattr(cls, ptr_attr(t), prop)
    setattr(cls, types_attr, dynptr_prop.types)

    def pointer_get(self):
        return getattr(self, ptr_attr(dynptr_prop.refine(self)))
    setattr(cls, attr, property(fget=pointer_get))

def bpy_unregister_dynpointer(cls, attr):
    def ptr_attr(t):
        return "%s__T%s" % (attr, t.__name__)
    types_attr = "%s__types" % attr

    types = getattr(cls, types_attr)
    for t in types:
        delattr(cls, ptr_attr(t))
    delattr(cls, types_attr)
    delattr(cls, attr)

def DynPointerContainer(cls):
    dynptr_items = [(attr, item) for attr, item in cls.__dict__.items() if isinstance(item, DynPointerProperty)]
    for attr, item in dynptr_items:
        bpy_register_dynpointer(cls, attr, item)
    return cls

class DynPointerProperty():
    def __init__(self, name="", description="", types=set(), refine=lambda self: None, options={'ANIMATABLE'}):
        self.name = name
        self.description = description
        self.types = types
        self.refine = refine
        self.options = options


"""
### Dynamic PropertyGroup ###

def dyn_property_group(types=[], type_get=lambda self: None):
    def wrap(cls):
        if not issubclass(cls, PropertyGroup):
            raise Exception("dyn_property_group decorator can only be used on PropertyGroup subtypes")
            return cls

        base_getattr = PropertyGroup.__getattribute__
        base_setattr = PropertyGroup.__setattr__

        def impl_prop(t):
            return "impl__%s" % t.__name__

        # property groups for dynamic attributes
        for t in types:
            setattr(cls, impl_prop(t), PointerProperty(type=t, options={'HIDDEN'}))

        def impl_get(self):
            impl_type = type_get(self)
            return base_getattr(self, impl_prop(impl_type))

        # get/set methods for automatic deferring to impl property groups
        def type_getattr(self, name):
            try:
                return base_getattr(self, name)
            except:
                impl = impl_get(self)
                return getattr(impl, name)
        def type_setattr(self, name, value):
            try:
                # XXX ugly: __getattribute__ raises exception if attribute is undefined
                # using this to switch to impl attribute
                base_getattr(self, name)
                base_setattr(self, name, value)
            except:
                print("setting %r = %r" % (name, value))
                impl = impl_get(self)
                setattr(impl, name, value)
        cls.__getattr__ = type_getattr
        cls.__setattr__ = type_setattr

        return cls

    return wrap
"""
