from flask_restx import Namespace

from common.utils import add_endpoint_prefix
from config import GLOBAL_CONFIG
from .resource import (
    CalcJobNode,
    Computer,
    Group,
    Node,
    ProcessNode,
    QueryBuilder,
    ServerInfo,
    User,
)

NAME = "aiida"

posting = GLOBAL_CONFIG.get("CLI_DEFAULTS", {}).get("posting", False)

ns = Namespace(name=NAME, description="Aiida Default RestFul Service.")

ns.add_resource(
    ServerInfo,
    "/server/",
    "/server/endpoints/",
    endpoint=add_endpoint_prefix(NAME, "server"),
    strict_slashes=False,
)

if posting:
    ns.add_resource(
        QueryBuilder,
        "/querybuilder/",
        endpoint=add_endpoint_prefix(NAME, "querybuilder"),
        strict_slashes=False,
    )

## Add resources and endpoints to the api
ns.add_resource(
    Computer,
    # supported urls
    "/computers/",
    "/computers/page/",
    "/computers/page/<int:page>/",
    "/computers/<id>/",
    "/computers/projectable_properties/",
    endpoint=add_endpoint_prefix(NAME, "computers"),
    strict_slashes=False,
)

ns.add_resource(
    Node,
    "/nodes/",
    "/nodes/projectable_properties/",
    "/nodes/statistics/",
    "/nodes/full_types/",
    "/nodes/full_types_count/",
    "/nodes/download_formats/",
    "/nodes/page/",
    "/nodes/page/<int:page>/",
    "/nodes/<id>/",
    "/nodes/<id>/links/incoming/",
    "/nodes/<id>/links/incoming/page/",
    "/nodes/<id>/links/incoming/page/<int:page>/",
    "/nodes/<id>/links/outgoing/",
    "/nodes/<id>/links/outgoing/page/",
    "/nodes/<id>/links/outgoing/page/<int:page>/",
    "/nodes/<id>/links/tree/",
    "/nodes/<id>/contents/attributes/",
    "/nodes/<id>/contents/extras/",
    "/nodes/<id>/contents/derived_properties/",
    "/nodes/<id>/contents/comments/",
    "/nodes/<id>/repo/list/",
    "/nodes/<id>/repo/contents/",
    "/nodes/<id>/download/",
    endpoint=add_endpoint_prefix(NAME, "nodes"),
    strict_slashes=False,
)

ns.add_resource(
    ProcessNode,
    "/processes/projectable_properties/",
    "/processes/<id>/report/",
    endpoint=add_endpoint_prefix(NAME, "processes"),
    strict_slashes=False,
)

ns.add_resource(
    CalcJobNode,
    "/calcjobs/<id>/input_files/",
    "/calcjobs/<id>/output_files/",
    endpoint=add_endpoint_prefix(NAME, "calcjobs"),
    strict_slashes=False,
)

ns.add_resource(
    User,
    "/users/",
    "/users/projectable_properties/",
    "/users/page/",
    "/users/page/<int:page>/",
    "/users/<id>/",
    endpoint=add_endpoint_prefix(NAME, "users"),
    strict_slashes=False,
)

ns.add_resource(
    Group,
    "/groups/",
    "/groups/projectable_properties/",
    "/groups/page/",
    "/groups/page/<int:page>/",
    "/groups/<id>/",
    endpoint=add_endpoint_prefix(NAME, "groups"),
    strict_slashes=False,
)
