from common.handler import after_request_handler, pre_request_handler
from config import GLOBAL_CONFIG, api, app
from service import aiida, hello, system

_loaded_module = (
    pre_request_handler,
    after_request_handler,
)
api.init_app(app=app)

api.add_namespace(system, "/system")
api.add_namespace(aiida, "/aiida")
api.add_namespace(hello, "/hello")

if __name__ == "__main__":
    APP_CONFIG = GLOBAL_CONFIG.get("APP_CONFIG")
    app.run(host=APP_CONFIG.get("HOST"), port=APP_CONFIG.get("PORT"))
