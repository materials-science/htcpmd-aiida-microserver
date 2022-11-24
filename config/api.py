from flask import url_for
from flask_restx import Api as Restful_Api

from .config import GLOBAL_CONFIG, INSTANCE


class Api(Restful_Api):
    def __init__(self, app=None, **kwargs):
        super().__init__(
            app=app, catch_all_404s=True, **kwargs
        )

    @property
    def base_path(self):
        """override default base path of Swagger for gateway

        :return:
        """
        base_path = GLOBAL_CONFIG.get("API_CONFIG", {}).get("swagger_base_path",
                                                            None)
        return base_path if base_path is not None else url_for(
            self.endpoint("root"), _external=False)


def get_api_instance():
    api = INSTANCE.get("api")

    if api is None:
        api = Api(authorizations={
            "Authorization": {
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "in": "header"
            }
        }, **GLOBAL_CONFIG.get("API_CONFIG", {}))
        INSTANCE.setdefault("api", api)

    return api
