from flask import request

from common.BaseResource import BaseResource
from common.utils import Utils, list_routes
from config import GLOBAL_CONFIG


class System(BaseResource):
    def get(self):
        print(self.path)

        return Utils.build_response(data=GLOBAL_CONFIG)


class EndPointsResource(BaseResource):
    def get(self):
        data = dict(
            method=request.method,
            url=self.url,
            url_root=self.url_root,
            path=self.path,
            query_string=self.query_string,
            resource_type="Info",
            available_endpoints=list_routes(),
        )

        return Utils.build_response(data=data)
