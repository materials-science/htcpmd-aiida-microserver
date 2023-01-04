from flask import request

from common.BaseResource import BaseResource


class UploadStructure(BaseResource):
    def post(self):
        uploaded_files = request.files.getlist("file")
        print(len(uploaded_files))
        if len(uploaded_files) > 1:
            for file in uploaded_files:
                print(file.stream.read())
# class StructureResource(BaseResource):
#     """Test UserContextHolder and RPC
#     """
#
#     def get(self, id=None):
#         """return Structure file stream"""
#         try:
#             # queryData = Structure.query
#             # queryData = Structure.objects.filter(uuid=uuid).first()
#             # db.select()
#             # Structure.query.
#             pass
#         except Exception as e:
#             return Utils.build_response(status=404, msg="No structure found.")
#
#         # aseAtoms = read(
#         #     str(settings.MEDIA_ROOT.joinpath(str(queryData.filepath)))
#         # )
#         # with NamedTemporaryFile(suffix="." + uuid + ".cif") as tf:
#         #     aseAtoms.write(tf.name, format="cif")
#         #     tf.seek(0)
#         #     stream = tf.read()
#         return Utils.build_response()
#
#     def post(self):
#         return Utils.build_response(msg="Hello [POST].")
