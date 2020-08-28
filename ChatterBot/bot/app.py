from flask import Flask, render_template, request, jsonify
import chatterbot.comparisons
from chatterbot import ChatBot, filters, response_selection
from chatterbot.trainers import ChatterBotCorpusTrainer
from flask import request
import hashlib
import time
import xmltodict
from pymongo import MongoClient
import string
import logging

connect = MongoClient('localhost')
db = connect['chatterbot-database']
collection = db.image

app = Flask(__name__)
# 机器人配置
logging.basicConfig(level=logging.INFO)  # 启动日志模式
bot = ChatBot("Chatterbot",
              storage_adapter='chatterbot.storage.MongoDatabaseAdapter',  # 采用mongodb数据库
              logic_adapters=[  # 设置逻辑适配器
                  {
                      'import_path': 'chatterbot.logic.BestMatch',
                      'maximum_similarity_threshold': 0.90,  # 最高置信度
                  }
              ],
              database='chatterbot-database',  # 数据库名称
              filters=[filters.get_recent_repeated_responses],  # 过滤器。 过滤空白符
              read_only=1
              )
# 训练
trainer = ChatterBotCorpusTrainer(bot)
trainer.train('./lan1.json')
trainer.train('./lan2.json')


# 默认进入的网页页面
@app.route("/")
def home():
    return render_template("index.html")


# 微信的连接
@app.route("/weixin", methods=["GET", "POST"])
def weixin():
    def responsetext():  # 函数用于回复文本的格式
        resp = {
            "xml": {
                "ToUserName": xml_dict.get("FromUserName"),
                "FromUserName": xml_dict.get("ToUserName"),
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": str(bot.get_response(content))
            }
        }
        return xmltodict.unparse(resp)

    def responseimage(name):   # 用于回复图片的格式
        ima = collection.find_one({'name': name})
        resp = {
            "xml": {
                "ToUserName": xml_dict.get("FromUserName"),
                "FromUserName": xml_dict.get("ToUserName"),
                "CreateTime": int(time.time()),
                "MsgType": "image",
                "Image": {
                    "MediaId": ima['media_id']
                }
            }
        }
        return xmltodict.unparse(resp)

    if request.method == "GET":  # 判断请求方式是GET请求
        my_signature = request.args.get('signature')  # 获取携带的signature参数
        my_timestamp = request.args.get('timestamp')  # 获取携带的timestamp参数
        my_nonce = request.args.get('nonce')  # 获取携带的nonce参数
        my_echostr = request.args.get('echostr')  # 获取携带的echostr参数

        token = 'zjh1998'  # 一定要跟刚刚填写的token一致

        # 进行字典排序
        data = [token, my_timestamp, my_nonce]
        data.sort()

        # 拼接成字符串
        temp = ''.join(data).encode('utf-8')
        # 进行sha1加密
        mysignature = hashlib.sha1(temp).hexdigest()

        # 加密后的字符串可signature对比，标识该请求来源于微信
        if my_signature == mysignature:
            return my_echostr
    else:
        # 解析xml
        xml_str = request.data
        # 对xml字符串进行解析
        xml_dict = xmltodict.parse(xml_str)
        xml_dict = xml_dict.get("xml")
        # 提取消息类型
        # 判断类型并回复
        msg_type = xml_dict.get("MsgType")
        content = None
        if msg_type == 'text':
            content = xml_dict.get("Content")
        elif msg_type == 'voice':
            content = xml_dict.get("Recognition")
        if str.find(content, '校历') + 1:
            resp_xml_str = responseimage('校历')
            return resp_xml_str
        elif str.find(content, '校车') + 1:
            resp_xml_str = responseimage('校车')
            return resp_xml_str
        else:
            resp_xml_str = responsetext()
            return resp_xml_str


# flask网页查询
@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return str(bot.get_response(userText))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
