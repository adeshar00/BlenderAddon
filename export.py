
import bpy

#printverts
#{{{

def appendInt(n, ba):
	'''
	Appends an int between 0 and 65,532 to a byte array as two bytes.
	The first byte is the low (1's place) byte
	The second byte is the high (256's place) byte
	'''
	if n<0 or n>= 1<<16:
		raise Exception("Invalid int passed to 'appendInt' function:\
								has to be between 0 and 65,532.")
	ba.append(n&0xff)
	ba.append((n&0xff00)>>8)


def appendFloat(f, ba):
	'''
	Appends a floating point number between -128 and 128
	 to a byte array as two bytes.
	The low byte is the fractional portion of the float.
	The high byte is the whole portion of the float
	'''
	rf = f + 128 + 1/512 # Adjusts for rounding (so .5 and .9999 round to 1 instead of 0)
	if rf<0 or rf>= 256:
		raise Exception("Invalid float passed to 'appendFloat' function:\
								has to be between -128 and 128.")
	lowByte = int(rf*256.0)&255
	highByte = int(rf)&255
	ba.append(lowByte)
	ba.append(highByte)


def setInt(n, ba, i):
	'''
	Sets indices i and i+1 of passed bytearray to represent an int between 0 and 65,532.
	The first byte is the low (1's place) byte
	The second byte is the high (256's place) byte
	'''
	if n<0 or n>=1<<16:
		raise Exception("Invalid int passed to 'appendInt' function:\
								has to be between 0 and 65,532.")
	ba[i] = (n&0xff)
	ba[i+1] = (n&0xff00)>>8


def setFloat(f, ba, i):
	'''
	Sets indices i and i+1 of passed bytearray to represent a floating point
	 number between -128 and 128.
	The low byte is the fractional portion of the float.
	The high byte is the whole portion of the float
	'''
	rf = f + 128 + 1/512 # Adjusts for rounding (so .5 and .9999 round to 1 instead of 0)
	if rf<0 or rf>=256:
		raise Exception("Invalid float passed to 'appendFloat' function:\
								has to be between -128 and 128.")
	ba[i] = int(rf*256.0)&255
	ba[i+1] = int(rf)&255


# current format: 2 bytes ob count "Supports only 65k vert objects, 65k objects(?)"
#                 per ob: 2 bytes vert count
#						  2 bytes tri count
#						  6 bytes: x y z offsets
#						  6 bytes: x y z euler angles (pi = 2<<15)
#						  6 bytes: x y z scale
#						  verts (6 bytes per vert), 
#						  tris (6 bytes per tri)



def generateByteArray():
	# create byte array
	b = bytearray()

	# append file header (these values are modified after object count is determined)
	b.append(0)
	b.append(0)

	# append data for each object
	objectCount = 0
	for o in bpy.data.objects:

		if o.type == 'MESH':

			objectCount+= 1

			# make sure bpy data is up to date
			o.data.update()

			# first index of object header
			objectHeaderPointer = len(b)
			objectVertexCountPointer = objectHeaderPointer
			objectTriCountPointer = objectHeaderPointer + 2 #rename as index to byte array

			# create space for vert count (modified after vert count determined)
			b.append(0)
			b.append(0)

			# create space for tri count (modified after tri count determined)
			b.append(0)
			b.append(0)

			# append translation offsets
			appendFloat(o.location.x,b)
			appendFloat(o.location.y,b)
			appendFloat(o.location.z,b)

			# append rotations
			appendFloat(o.rotation_euler.x,b)
			appendFloat(o.rotation_euler.y,b)
			appendFloat(o.rotation_euler.z,b)
			if o.rotation_mode != 'XYZ':
				# TODO figure out if there's some easy way to auto-convert, rather than reject
				# or maybe account for rotatation mode in import
				raise Exception("Object's rotation_mode must be 'XYZ'")
				

			# append scales
			appendFloat(o.scale.x,b)
			appendFloat(o.scale.y,b)
			appendFloat(o.scale.z,b)

			# cycle through vertices and append
			vertCount = 0
			for v in o.data.vertices:
				appendFloat(v.co.x, b)
				appendFloat(v.co.y, b)
				appendFloat(v.co.z, b)
				vertCount+=1
			setInt(vertCount, b, objectVertexCountPointer) # set vertex count

			# cycle through tris and append
			triCount = 0
			for p in o.data.polygons:
				# TODO better or more elegant way to do this? cutting polys into tris
				pv = p.vertices
				i = 2
				while i < len(pv):
					appendInt(pv[0],b)
					appendInt(pv[i-1],b)
					appendInt(pv[i],b)
					triCount+= 1
					i+= 1
			setInt(triCount, b, objectTriCountPointer)
			

	# adjust object count in header
	setInt(objectCount, b, 0)

	# quickly check if bytearray size accurate??

	return b

#}}}


# NOTE: Most of the code below is from a blender add-on template

bl_info = \
    {
        "name" : "CSMF Exporter",
        "author" : "",
        "version" : (1, 0, 0),
        "blender" : (2, 7, 4),
        "location" : "",
        "description" :
            "Export model as .csmf",
        "warning" : "",
        "wiki_url" : "",
        "tracker_url" : "",
        "category" : "Import-Export",
    }

def write_some_data(context, filepath, use_some_setting):
    print("running write_some_data...")
    f = open(filepath, 'wb')
    #f.write("Hello World %s" % use_some_setting)
    ba = generateByteArray()
    f.write(ba)
    f.close()

    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportSomeData(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export!"

    # ExportHelper mixin class uses this
    filename_ext = ".csmf"

    filter_glob = StringProperty(
            default="*.csmf",
            options={'HIDDEN'},
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = BoolProperty(
            name="Example Boolean",
            description="Example Tooltip",
            default=True,
            )

    type = EnumProperty(
            name="Example Enum",
            description="Choose between two items",
            items=(('OPT_A', "First Option", "Description one"),
                   ('OPT_B', "Second Option", "Description two")),
            default='OPT_A',
            )

    def execute(self, context):
        return write_some_data(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeData.bl_idname, text="Compact Simple Model File (.csmf)")


def register():
    bpy.utils.register_class(ExportSomeData)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSomeData)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

