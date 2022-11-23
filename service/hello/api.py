from flask_restx import Namespace

from .resource import Hello

ns = Namespace(name="hello", description="Demo Service.")

ns.add_resource(Hello, "/", "/<string:id>")
