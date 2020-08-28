import json
import requests
from pymongo import MongoClient

app_id: str = "wxb64994a3ed0e1ac7"
secret: str = "3d3d18b203ffb191c4e90c657a0ab9cd"


def get_access_token(app_ids, secrets):
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(app_ids,secrets)
    r = requests.get(url)
    parse_json = json.loads(r.content.decode())
    token = parse_json['access_token']
    return token


def img_upload(name, media_Type='image'):
    token = get_access_token(app_id, secret)
    #url = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (token, media_Type)
    url = "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=%s&type=%s" % (token, media_Type)
    files = {'media': open('{}'.format(name), 'rb')}
    r = requests.post(url, files=files)
    parse_json = json.loads(r.content.decode())
    return parse_json['media_id']


def img_del(MEDIA_ID):
    token = get_access_token(app_id, secret)
    url = "https://api.weixin.qq.com/cgi-bin/material/del_material?access_token=%s" % token
    MEDIA_ID = 'omyRAFZpL5UKiar0aiBHoXV-KD1zLiIm-sS_KMHxTb8'
    Data = {"media_id": MEDIA_ID}
    r = requests.post(url, json=Data)
    parse_json = json.loads(r.content.decode())
    return parse_json['errcode']


if __name__ == "__main__":
    connect = MongoClient('localhost')
    db = connect["chatterbot-database"]
    collection = db.image
    ima = collection.find_one({'name': '校历'})
    #img_del(ima['media_id'])
    name = './Calendar.png'
    ima['media_id'] = img_upload(name)
    collection.update({'name': '校历'}, ima)
    ima = collection.find_one({'name': '校车'})
    #img_del(ima['media_id'])
    name = './Bus.jpg'
    ima['media_id'] = img_upload(name)
    collection.update({'name': '校车'}, ima)
