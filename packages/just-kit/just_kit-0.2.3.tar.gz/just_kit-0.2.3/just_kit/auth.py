import os
import pickle
import logging
import requests
from bs4 import BeautifulSoup
from .utils import *
from typing import Optional
from .utils.rsa import encrypt

class Authenticator:
    '''
    用于登录信息门户的类
    '''
    def __init__(self, debug=False,auto_login=True,vpn:bool=True):
        '''
        初始化函数
        :param debug: 是否开启调试模式
        :param auto_login: 是否自动读取保存的cookies以快速登录
        :param vpn: 是否使用vpn,若使用则会service使用 https://vpn2.just.edu.cn/
        '''
        self.logger = logging.getLogger(__name__)
        if debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            logging.basicConfig(level=logging.INFO)

        # 基础信息
        self.vpn = vpn
        self.service = "https://ids2.just.edu.cn/cas/login?service=http%3A%2F%2Fmy.just.edu.cn%2F" if vpn else "http://my.just.edu.cn/"
        
        # 用于储存登入后的一些数据
        
        self.login_data = {}
        self.session = requests.Session()
        self.cookie_file = ".cookies_saved.pkl"  # 根据service生成唯一的cookie文件名

        self.ignore_cookies = ['Location']  # 要忽略的 cookie 名列表
        self.auto_login=auto_login
        if auto_login:
            self.load_cookies()  # 初始化时尝试加载cookie
            if not self.check():
                self.expire() # 自动登入失败

    def save_cookies(self):
        """保存cookies到文件"""
        filtered_cookies = {
            name: value for name,
            value in self.session.cookies.items() if name not in self.ignore_cookies}
        with open(self.cookie_file, 'wb') as f:
            pickle.dump(self.session.cookies, f)
            
    def load_cookies(self):
        """
        从文件加载cookies
        会自动忽略location
        """
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, 'rb') as f:
                cookies = pickle.load(f)
                for name, value in cookies.items():
                    if name not in self.ignore_cookies:
                        self.session.cookies.set(name, value)

    def jsessionid(self)->Optional[str]:
        '''
        获取JSESSIONID,如果有JSESSIONID返回,否则返回None
        '''
        d = self.session.cookies
        return d["JSESSIONID"] if 'JSESSIONID' in d else None

    @staticmethod
    def encrypt_with_js(password) -> str:

        """
        使用 与js脚本一直的方式进行加密数据
        :param password: 要加密的密码
        :return: 加密后的数据
        """
        return encrypt(password)

    def login(self, account: str, password: str):

        self.login_data = {
            "username": account,
            "password": password,
        }


        if self.check():
            self.logger.info("已登录")
            return

        """
        接受账户和密码进行登录
        :param account: 账户
        :param password: 密码
        """
        with self.session as session:
            
            # 直接访问service进行自动跳转?
            res = session.get(
                self.service,
                allow_redirects=True,
            )
            target = res.url

            # find execution
            soup = BeautifulSoup(res.text, "html.parser")
            execution_input = soup.find("input", {"name": "execution"})
            if execution_input:
                execution_value = execution_input.get("value")
            else:
                self.logger.error("未找到名为execution的input元素")

            # login data construct
            data = {
                "username": account,
                "password": self.encrypt_with_js(password),
                "_eventId": "submit",
                "submit": "登+录",
                "encrypted": "true",
                "loginType": "1",
                "execution": execution_value,
            }


            # login
            res = session.post(
                target,
                data=data,
                allow_redirects=False)

            if res.status_code == 302:
                self.logger.info("登入成功")
                self.save_cookies()
                session.get(res.headers["Location"])
            else:
                self.logger.error("登录失败")
                return -1
        return 0

    def expire(self):
        """
        强制清除Cookies信息过期
        """
        self.session.cookies.clear()
        # 删除cookie文件
        if os.path.exists(self.cookie_file):
            os.remove(self.cookie_file)

    CHECK_URL = "http://my.just.edu.cn/"
    CHECK_URL_VPN = "https://client.v.just.edu.cn/http/webvpn764a2e4853ae5e537560ba711c0f46bd/_s2/students_sy/main.psp"

    def check(self) -> bool:

        """
        检查登录是否失效
        :return: 如果登录有效返回True,否则返回False
        """
        res = self.session.get(
            self.CHECK_URL ,
            allow_redirects=False,
        )
        print(res.url)
        print(res.headers)
        return res.status_code == 200
    
    def relogin(self):
        """
        重新登录
        """
        self.expire()
        return self.login(self.login_data["username"], self.login_data["password"])