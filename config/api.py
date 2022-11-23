from flask_restx import Api as Restful_Api
from .config import INSTANCE, GLOBAL_CONFIG


class Api(Restful_Api):
    def __init__(self, app=None, **kwargs):
        super().__init__(
            app=app, prefix=kwargs.get("PREFIX", ""), catch_all_404s=True
        )


def get_api_instance():
    api = INSTANCE.get("api")

    if api is None:
        api = Api(**GLOBAL_CONFIG.get("API_CONFIG", {}))
        INSTANCE.setdefault("api", api)

    return api
