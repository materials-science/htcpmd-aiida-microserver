from flask_restx import Namespace

from .resource import EndPointsResource, System

ns = Namespace(name="system", description="System Info Service.")

ns.add_resource(System, "/", endpoint="system")

ns.add_resource(EndPointsResource, "/endpoint", endpoint="endpoint")
