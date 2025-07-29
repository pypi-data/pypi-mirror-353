# just-kit

江苏科技大学信息门户工具包，用于获取和操作学校信息门户上的各种数据。

## 功能特性

- 宿舍电量查询
- 校园卡余额查询
- 校车信息查询
- 更多功能开发中...

## 安装

```bash
pip install just-kit
```

## 使用方法

### 登入
默认使用信息门户作为登入服务
```python
import os
from just_kit.auth import Authenticator

import dotenv
dotenv.load_dotenv()

auther = Authenticator(vpn=True,auto_login=False,debug=True)

auther.login(
    account=os.getenv("USER"),
    password=os.getenv("PASSWORD"))
```

### 过期与重新登入

```python
auther.expire()
if not auther.check():
    print("重新登入：",auther.relogin()==0)
else:
    print("已登录")   
```

### 服务:Epay
epay服务用于获取宿舍电费、用户校园卡余额和浴室专款
```python
from just_kit.services import EpayServiceProvider
epay = EpayServiceProvider(auther)
epay.login()
epay.query_electric_bill()
epay.query_account_bill()
```


### 服务:HealthCheck
宿舍卫生检查分数查询服务
```python
from just_kit.services import HealthCheckService
service = HealthCheckService(auther)
service.login()
# 获取最近宿舍卫生检查分数
service.get_health_check_data()
# 获取 [HealthCheckData]
# 包含socre和date属性
```

## 开发说明

本项目使用Python 3.11开发，主要依赖：
- requests：用于发送HTTP请求
- beautifulsoup4：用于解析HTML

## 许可证

本项目采用MIT许可证。