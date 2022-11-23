from common.utils import DotDict
from .config import GLOBAL_CONFIG
import KcangNacos.nacos as nacos

NACOS = DotDict(GLOBAL_CONFIG.get("NACOS"))
APP_CONFIG = DotDict(GLOBAL_CONFIG.get("APP_CONFIG"))

nacosServer = nacos.nacos(ip=NACOS.host, port=NACOS.port)

nacosServer.config(
    dataId=NACOS.data_id,
    myConfig=GLOBAL_CONFIG,
    group=NACOS.group,
    tenant=NACOS.namespace,
)

nacosServer.registerService(
    serviceIp=APP_CONFIG.HOST,
    servicePort=APP_CONFIG.PORT,
    serviceName=NACOS.server_name,
    namespaceId=NACOS.namespace,
    groupName=NACOS.group,
)

nacosServer.healthyCheck()
