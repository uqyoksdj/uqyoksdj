import json
import requests
import re  # 导入正则
import pprint

BV = 'BV1bb421J7Qi'
base_url = 'https://www.bilibili.com/video/' + BV

headers = {
    "referer": "https://www.bilibili.com/video/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
}
# 发送请求
response = requests.get(base_url, headers=headers)
# 获取数据，获取服务器返回响应数据 --文本数据
# print(response.text)
# 解析数据，提取我们想要数据内容
# 正则表达式   对于字符串数据类型进行提取、解析
# 从response.text里面去找 "title":"(.*？)"，”pubdata“
title = re.findall('"title":"(.*?)","pubdate"', response.text)[0]
# 获取视频数据信息  前端标签两个两个一起
html_data = re.findall('<script>window.__playinfo__=(.*?)</script>', response.text)[0]
# 转换数据类型 字符串数据转成json字典数据类型
json_data = json.loads(html_data)  # 导入import json
pprint.pprint(json_data)
# print(title)
# print(json_data)
# pprint(json_data)
# 字典数据 B站数据 音频和视频分开的
video_url = json_data['data']['dash']['video'][0]['baseUrl']
print(title)
print(video_url)
# 链接没有访问权限
# 保存视频

video_data = requests.get(video_url, headers=headers).content

with open(f'res/{title}.mp4', mode='wb') as f:
    f.write(video_data)
