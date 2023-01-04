from common.handler import after_request_handler, pre_request_handler
from config import GLOBAL_CONFIG, api, app, db, mq
from event import event_services
from service import aiida, hello, structure, system

_loaded_module = (
    pre_request_handler,
    after_request_handler,
    db,
    event_services
)

api.init_app(app=app)
api.add_namespace(system, "/system")
api.add_namespace(aiida, "/aiida")
api.add_namespace(hello, "/hello")
api.add_namespace(structure, "/structure")

mq.run_consumer()

if __name__ == "__main__":
    APP_CONFIG = GLOBAL_CONFIG.get("APP_CONFIG")
    app.config.update(**APP_CONFIG)
    app.run()
    mq.run_consumer()
