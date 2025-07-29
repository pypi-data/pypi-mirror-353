#!python3
# -*- coding:utf-8 -*-
import zlib
import logging
import threading
import websocket
import requests

"""
module: Local WebSocket Client For Community User.
support:help@jvQuant.com
"""


class Construct:
    __market = ""
    __token = ""
    __ws_ser_addr = ""
    __ws_conn = ""

    def __init__(self, market: str, token: str, logHandle, data_handle, log_level=logging.INFO):
        """
            websocket实时行情client实例化方法入口。参考 http://jvquant.com/wiki

            Args:
                market: 市场标志，沪深:ab；港股:hk；美股:us;
                token: 平台授权Token,前往 https://jvQuant.com 查看账户Token
                logHandle:自定义服务器返回日志信处理函数，例：def logHandle(log)
                data_handle: 自定义服务器返回行情数据处理函数，例：def dataHandle(data)
                log_level: 打印日志级别，例： logging.DEBUG，logging.INFO，logging.WARNING，logging.ERROR 等。
            Returns:
                websocke_client: websocke_client对象。

            Raises:
                ValueError: 获取服务器或连接服务器失败。

            Examples:
                >>>
                ws=jvQuant.websocket_client
                wsclient=ws.Construct(market,token,logHandle,dataHandle,logging.DEBUG)
                wsclient.addLv2(["600519","000001","i000001"])
                wsclient.addLv1(["600519","000001","i000001"])
                wsclient.cmd("list")
            """

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger("websocket_client")
        self.logger.setLevel(log_level)
        msg = ""

        if msg == "" and market not in {"ab", "hk", 'us'}:
            msg = "市场标志参数(market)无效。请选择有效的市场标志映射：沪深(ab)；港股(hk)；美股(us)。"

        if msg == "" and token == "":
            msg = "请输入正确的授权Token。Token获取地址:https://jvQuant.com。"

        if msg == "" and not callable(logHandle):
            msg = """logHandle日志处理函数无效，参考示例:
def logHandle(log):
    print(log)
    # 自定义日志处理逻辑

# 初始化类对象
wsclient=ws.Construct("ab","token",logHandle,dataHandle)

            """
        if msg == "" and not callable(data_handle):
            msg = """data_handle日志处理函数无效，参考示例:
def data_handle(data):
    print(data)
    # 自定义数据处理逻辑

# 初始化类对象
wsclient=ws.Construct("ab","token",logHandle,dataHandle)
                        """
        if msg != "":
            raise ValueError(msg)

        self.__log = logHandle
        self.__market = market
        self.__token = token
        self.__data_handle = data_handle

        self.__ask_for_server()
        if self.__ws_ser_addr:
            self.__conn_event = threading.Event()
            self.th_handle = threading.Thread(target=self.__conn)
            self.th_handle.start()
            self.__conn_event.wait()

    def __ask_for_server(self):
        url = "http://jvquant.com/query/server?type=websocket&token=" + self.__token + "&market=" + self.__market
        try:
            res = requests.get(url=url)
        except Exception as e:
            self.logger.error("请求行情服务器地址失败")
            return
        if (res.json()["code"] == "0"):
            self.__ws_ser_addr = res.json()["server"]
            self.logger.info("获取行情服务器地址成功，服务器地址:" + self.__ws_ser_addr)
        else:
            msg = "分配行情服务器地址失败,服务器响应:" + res.text
            self.logger.error(msg)

    def __conn(self):
        wsUrl = self.__ws_ser_addr + "?token=" + self.__token
        self.__ws_conn = websocket.WebSocketApp(wsUrl,
                                                on_open=self.__on_open,
                                                on_data=self.__on_message,
                                                on_error=self.__on_error,
                                                on_close=self.__on_close)
        self.__ws_conn.run_forever()
        self.logger.info("websocket_client线程结束")

    def cmd(self, cmd):
        """
            发送自定义指令，命令参考 http://jvquant.com/wiki

            Args:
                cmd: 命令代码
                        例：add=lv10_600519,lv2_600519;
                        all=lv1_600519
        """
        if self.__ws_conn:
            self.__ws_conn.send(cmd)
            self.logger.debug("发送指令:" + cmd)

    def addLv1(self, codeArr):
        """
            批量新增level1订阅。参考 http://jvquant.com/wiki

            Args:
                codeArr: 证券代码数组，
                        例：沪深["600519","000001","i000001"];
                        港股["00700","09888","09618"];
                        美股["aapl","nvda","msft"];
        """
        cmd = "add="
        lvCodes = []
        for code in codeArr:
            lvCodes.append("lv1_" + code)

        cmd = cmd + ",".join(lvCodes)
        self.cmd(cmd)

    def delLv1(self, codeArr):
        """
            批量取消level1订阅。参考 http://jvquant.com/wiki

            Args:
                codeArr: 证券代码数组，
                        例：沪深["600519","000001","i000001"];
                        港股["00700","09888","09618"];
                        美股["aapl","nvda","msft"];
        """
        cmd = "del="
        lvCodes = []
        for code in codeArr:
            lvCodes.append("lv1_" + code)

        cmd = cmd + ",".join(lvCodes)
        self.cmd(cmd)

    def addLv2(self, codeArr):
        """
            批量新增level2订阅。参考 http://jvquant.com/wiki

            Args:
                codeArr: 证券代码数组，
                        例：沪深["600519","000001","i000001"];
                        港股["00700","09888","09618"];
                        美股["aapl","nvda","msft"];
        """
        cmd = "add="
        lvCodes = []
        for code in codeArr:
            lvCodes.append("lv2_" + code)

        cmd = cmd + ",".join(lvCodes)
        self.cmd(cmd)

    def delLv2(self, codeArr):
        """
            批量取消level2订阅。参考 http://jvquant.com/wiki

            Args:
                codeArr: 证券代码数组，
                        例：沪深["600519","000001","i000001"];
                        港股["00700","09888","09618"];
                        美股["aapl","nvda","msft"];
        """
        cmd = "del="
        lvCodes = []
        for code in codeArr:
            lvCodes.append("lv2_" + code)

        cmd = cmd + ",".join(lvCodes)
        self.cmd(cmd)

    def __on_open(self, ws):
        self.__conn_event.set()
        self.logger.info("行情连接已创建")

    def __on_error(self, ws, error):
        self.logger.error(error)

    def __on_close(self, ws, code, msg):
        self.logger.info("websocket_client连接已断开")

    def close(self):
        self.__ws_conn.close()

    def __on_message(self, ws, message, type, flag):
        # 命令返回文本消息
        if type == websocket.ABNF.OPCODE_TEXT:
            # 发送至用户自定义日志处理
            self.__log(message)
            self.logger.debug("Text响应:" + message)

        # 行情推送压缩二进制消息，在此解压缩
        if type == websocket.ABNF.OPCODE_BINARY:
            rb = zlib.decompress(message, -zlib.MAX_WBITS)
            text = rb.decode("utf-8")
            self.__data_handle(text)
            self.logger.debug("Binary响应:" + text)
