import json
from datetime import datetime

from flask import current_app

from common import UserContextHolder
from common.BaseResource import BaseResource
from common.utils import Utils
from proxy.UserPorxy import get_user_info


class Hello(BaseResource):
    """Test UserContextHolder and RPC
    """

    def get(self, id=None):
        if id:
            return Utils.build_response(
                data={
                    "id": id,
                    "username": UserContextHolder.get_username(),
                    "datetime": datetime.now().isoformat()
                }
            )
        else:
            resp = json.loads(get_user_info())
            current_app.logger.debug(resp)

            return Utils.build_response(data=resp)

    def post(self):
        return Utils.build_response(msg="Hello [POST].")
