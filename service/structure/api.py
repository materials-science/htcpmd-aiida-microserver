from flask_restx import Namespace

from .resource import UploadStructure

ns = Namespace(name="structure", description="Structure Service.")

ns.add_resource(UploadStructure, "/upload", endpoint="upload")
