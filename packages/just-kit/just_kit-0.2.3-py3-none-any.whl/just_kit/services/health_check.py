import json
import re
from dataclasses import dataclass

from .service import ServieProvider
from just_kit.auth import Authenticator


@dataclass
class HealthCheckData:
    score: float
    date: str


class HealthCheckService(ServieProvider):
    DATA_URL_VPN2 = 'http://hqgy.just.edu.cn/sg/wechat/healthCheck.jsp'

    SERVICE_URL_VPN2 = 'http://hqgy.just.edu.cn/CASLogin'

    def __init__(self, auth: Authenticator):
        super().__init__(auth)

    def get_health_check_data(self) -> list[HealthCheckData]:
        """
        获取卫生检查分数数据
        :return: 解析后的JSON数据
        """
        res = self.session.get(self.data_url())
        if res.status_code != 200:
            self.logger.error(f"请求失败: {res.status_code}")
            return []

        # 从jsp文件中提取JSON数据
        match = re.search(r'var allData = (\[\{[\s\S]*}\]);', res.text, re.MULTILINE)
        if not match:
            self.logger.error("未找到loadData函数")
            return []

        # 提取JSON部分
        data = json.loads(match.group(1))

        for item in data:
            item["private_info"] = json.loads(item["private_info"])
            item["public_info"] = json.loads(item["public_info"])

        return [HealthCheckData(score=float(item['score']), date=item['day']) for item in data]

    def login(self):
        resp = self.auth.session.get(self.service_url())
        if resp.url.endswith("welcome.do"):
            self.logger.info("登录成功")

    def service_url(self) -> str:
        return self.SERVICE_URL_VPN2

    def data_url(self) -> str:
        return self.DATA_URL_VPN2

    def check(self):
        return self.check_url(self.service_url())