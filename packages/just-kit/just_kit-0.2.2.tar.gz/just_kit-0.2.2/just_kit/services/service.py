from just_kit.auth import Authenticator
import logging
from just_kit.utils import *

class ServieProvider:
    def __init__(self,auth:Authenticator):
        self.auth = auth
        self.session = auth.session
        self.logger = logging.getLogger(__name__)
    
    def check(self):
        pass

    def check_url(self,service):
        """
        检查登录是否失效
        :return: 如果登录有效返回True,否则返回False
        """
        res = self.session.get(
            service,
            allow_redirects=False,
        )
        if res.status_code == 302:
            return False
        else:
            return True

    def service_url(self)->str:
        """
        获取服务地址
        """
        pass