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
#
# Leo L. Schwab                             2020.09.26
#

"""
This script imports a VideoScape-3D geometry (object) file to Blender.

Usage:
Run this script from the "File->Import" menu and then load the desired OBJ
file.  Note: Polygon colors and surface attributes are not yet supported.

WARNING:
Files containing "detail" polygons may cause this plugin to crash Blender.
"""

import bpy
import os.path
import struct


def ffp_to_float (val):
    """Convert Motorola Fast Floating Point value to native float.

    val -- Integer containing 32-bit FFP value.

    Returns: Native float value.

    """
    m = val >> 8                # Bits 31:8: Mantissa
    e = (val & 0x7f) - 0x40     # Bits 6:0: Excess-64 exponent
    if val & 0x80 != 0:         # Bit 7: Sign
        m = -m

    return pow (2, e) * m / (1 << 24)


def read_vs3d_data (context, filepath, use_some_setting):
    """Import VideoScape-3D object file"""
    verts = []
    faces = []

    with open (filepath, 'rb', encoding=None) as f:
        header = f.read (4)

        if header.lower() == b'3dg1':
            # Text format.
            f.readline()        # Eat leftover newline.

            # Read vertices.
            nverts = int (f.readline())
            for i in range (nverts):
                vstr = f.readline()
                x, y, z = [float (v) for v in vstr.split()]
                verts.append ((x, y, z))

            # Read polygons/faces.
            for line in f:
                vals = [int (i) for i in line.split()]
                vtxcnt = vals[0]
                if not all ((x >= 0  and  x < nverts) for x in vals[1:vtxcnt + 1]):
                    print ("Polygon indices out of range; object not loaded.")
                    return {'FINISHED'}

                faces.append (vals[1:vtxcnt + 1])
                if vals[vtxcnt + 1] < 0:
                    # If the color code is negative, there are detail polygons
                    # present.  In such a case, the immediately succeeding line
                    # contains a single value describing the count of detail
                    # polygons present, followed by that many lines of
                    # normally-formatted polygons.
                    #
                    # As a workaround, we just eat the detail count; the
                    # subsequent detail polygons are treated as regular
                    # polygons.  This is *not* the correct way to handle this,
                    # but doing this will prevent the plugin from crashing
                    # Blender.
                    #
                    f.readline()

        elif header == b'3DB1':
            # Binary format
            buf = f.read (2)
            nverts = struct.unpack (">H", buf)[0]

            # Read vertices.
            for i in range (nverts):
                buf = f.read (3 * 4)
                x, y, z = struct.unpack (">3I", buf)
                verts.append ((ffp_to_float (x), ffp_to_float (y), ffp_to_float (z)))

            # Read polygons/faces.
            while True:
                buf = f.read (2)
                if not buf:
                    break
                vtxcnt = struct.unpack (">H", buf)[0]
                buf = f.read ((vtxcnt + 1) * 2)
                fmt = ">" + str (vtxcnt) + "Hh"     # Color code is signed.
                indices = list (struct.unpack (fmt, buf))
                if not all ((x >= 0  and  x < nverts) for x in indices[0:vtxcnt]):
                    print ("Polygon indices out of range; object not loaded.")
                    return {'FINISHED'}

                faces.append (indices[0:vtxcnt])
                if indices[vtxcnt] < 0:
                    # Detail polygons present (see above comment for text
                    # format).  Workaround by eating the detail count.
                    #
                    f.read (2)

        else:
            printf ("Unrecognized header.")
            return {'FINISHED'}


    mesh = bpy.data.meshes.new (os.path.basename (filepath))
    obj = bpy.data.objects.new (mesh.name, mesh)
    col = bpy.data.collections.get ("Collection")
    col.objects.link (obj)
    bpy.context.view_layer.objects.active = obj

    mesh.from_pydata (verts, [], faces)

    return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportVS3DFileSelector (Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "org_ewhac.import_vs3d_file_selector"
    bl_label = "Import VS3D Object"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: BoolProperty (
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type: EnumProperty (
        name="Example Enum",
        description="Choose between two items",
        items=(
            ('OPT_A', "First Option", "Description one"),
            ('OPT_B', "Second Option", "Description two"),
        ),
        default='OPT_A',
    )

    def execute (self, context):
        return read_vs3d_data (context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu
def menu_func_import (self, context):
    self.layout.operator (ImportVS3DFileSelector.bl_idname, text="Text Import Operator")


def register():
    bpy.utils.register_class (ImportVS3DFileSelector)
    bpy.types.TOPBAR_MT_file_import.append (menu_func_import)


def unregister():
    bpy.utils.unregister_class (ImportVS3DFileSelector)
    bpy.types.TOPBAR_MT_file_import.remove (menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.org_ewhac.import_vs3d_data ('INVOKE_DEFAULT')
