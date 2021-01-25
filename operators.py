import bpy
import re
#import logging

class RemoveDublicateMaterials_Operator(bpy.types.Operator):
    bl_idname = "object.remove_dublicate_materials"
    bl_label = "Remove Dublicate Materials"
    bl_description = "Remove dublicate materials from the object."

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(sel, context):
        matlist = bpy.data.materials
        for obj in bpy.context.selected_objects:
            for mat_slt in obj.material_slots:
                if (mat_slt.material != None and bool(re.search(r'\.(\d){3}', mat_slt.material.name))):
                    replaced = False
                    for mat in matlist:
                        if ((mat.name == mat_slt.material.name.rsplit(".", 1)[0]) and (not bool(re.search(r'\.(\d){3}', mat.name)))):
                            mat_slt.material = mat
                            replaced = True
                    if replaced == False:
                        mat_slt.material.name = mat_slt.material.name.rsplit(".", 1)[0]
        return {'FINISHED'}

class RemoveAllMaterials_Operator(bpy.types.Operator):
    bl_idname = "object.remove_all_materials"
    bl_label = "RemoveAllMaterials"
    bl_description = "Removes all materials from selected objects"

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            obj.active_material_index = 0
            for i in range(len(obj.material_slots)):
                bpy.ops.object.material_slot_remove({'object': obj})
        return {'FINISHED'}


class AddTriangulateModifier_Operator(bpy.types.Operator):
    bl_idname = "object.add_triangulate_modifier"
    bl_label = "AddTriangulateModifier"
    bl_description = "Add Triangulate Modifier to selection objects."
 
    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):

        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                countTriangulateModifiers = 0
                for mod in obj.modifiers:
                    if (mod.type == "TRIANGULATE"):
                        countTriangulateModifiers += 1
                        obj.modifiers.remove(mod)
                        modTriangulate = obj.modifiers.new("Triangulate", type = "TRIANGULATE")
                        modTriangulate.keep_custom_normals = True
                        

                if (countTriangulateModifiers == 0):
                    modTriangulate = obj.modifiers.new("Triangulate", type = "TRIANGULATE")
                    modTriangulate.keep_custom_normals = True
        
        self.report({'INFO'}, "Added triangulate modifier to selected objects")
        bpy.context.view_layer.update()
        return {'FINISHED'}

class RemoveAllUnusedMaterials_Operator(bpy.types.Operator):
    bl_idname = "object.remove_unused_materials"
    bl_label = "RemoveUnusedMaterials"
    bl_description = "Removes unused materials from all selected objects"

    @classmethod
    def poll(cls, context):
        return context.selected_objects is not None

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                mesh = obj.data
                faces = mesh.polygons
                slots = obj.material_slots

                # get material index per face
                face_len = len(faces)
                used_material_indices = [0 for n in range(face_len)]
                faces.foreach_get('material_index', used_material_indices)

                # one index should only be once in the list
                used_material_indices = set(used_material_indices)

                # list unused material slots
                slot_len = len(slots)
                all_material_slot_indices = set(n for n in range(slot_len))
                unused_slot_indices = all_material_slot_indices - used_material_indices

                # override context's object to obj
                ctx = bpy.context.copy()
                ctx['object'] = obj

                # delete unused slots
                unused_slot_indices = list(unused_slot_indices)
                unused_slot_indices.sort(reverse=True)
                for slot_index in unused_slot_indices:
                    obj.active_material_index = slot_index
                    bpy.ops.object.material_slot_remove(ctx)

        self.report({'INFO'}, "Removed unused unslots from selection")
        bpy.context.view_layer.update()
        return {'FINISHED'}

