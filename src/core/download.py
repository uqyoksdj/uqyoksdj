import json
import requests
import re

from PyQt5.QtCore import pyqtSignal, QThread
from pytube import YouTube


def sum_exceeds_target(nums, timescale, target):
    current_sum = 0
    count = 0
    time = 5
    for count, num in enumerate(nums, 1):
        time = num / timescale
        current_sum += time
        if current_sum > target:
            return count, 1 - (current_sum - target) / time
    return count, 1 - (current_sum - target) / time


class ProcessVideo(QThread):
    set_value = pyqtSignal(int)
    finished = pyqtSignal(int)
    start_frame = pyqtSignal(float)
    end_frame = pyqtSignal(float)
    error = pyqtSignal(int)

    def __init__(self, url: str, start_time: int, end_time: int, path: str):
        super().__init__()
        bilibili_pattern = r'(https?://)?(www\.)?bilibili\.com/.*'
        youtube_pattern = r'(https?://)?(www\.)?youtube\.com/.*'
        self.url = url
        self.start_time = start_time
        self.end_time = end_time
        self.path = path
        self.video_data = b''

        self.headers = {
            "referer": "https://www.bilibili.com/video/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
        }

        if re.match(bilibili_pattern, url):
            self.get_url_bilibili()
        elif re.match(youtube_pattern, url):
            self.get_url_youtube()
        else:
            print('不支持该链接解析')
            self.error.emit(1)
            exit(1)

    def run(self):
        try:
            self.get_head()
            self.get_mdat()
            self.merge()
            print('下载完成')
            self.finished.emit(1)
        except Exception as e:
            print('出错了:', str(e))
            self.error.emit(1)

    def get_url_bilibili(self):
        base_url = self.url
        response = requests.get(base_url, headers=self.headers)
        if response.status_code == 200:
            self.title = re.findall('"title":"(.*?)","pubdate"', response.text)[0]
            html_data = re.findall('<script>window.__playinfo__=(.*?)</script>', response.text)[0]
            json_data = json.loads(html_data)
            self.video_url = json_data['data']['dash']['video'][0]['baseUrl']
        else:
            print("请求url失败，状态码：" + str(response.status_code))
            self.error.emit(1)
            exit(1)

    def get_url_youtube(self):
        yt = YouTube(self.url)
        self.title = yt.title
        streams = yt.streams
        video_streams = streams.filter(mime_type='video/mp4', resolution='480p')
        self.video_url = video_streams.url

    def get_head(self):
        response = requests.get(self.video_url, headers=self.headers, stream=True)
        offset = 0
        self.Bytes = []
        self.Times = []
        if response.status_code == 200:
            while True:
                chunk = response.iter_content(chunk_size=8).__next__()
                size = int.from_bytes(chunk[:4], byteorder='big')
                box_type = chunk[4:].decode('utf-8')
                if box_type == 'moof':
                    break
                if size - 8 == 0:
                    offset += size
                    continue
                if box_type == 'ftyp' or box_type == 'moov':
                    self.video_data += chunk
                    chunk = response.iter_content(chunk_size=size - 8).__next__()
                    self.video_data += chunk
                else:
                    chunk = response.iter_content(chunk_size=size - 8).__next__()
                if box_type == 'sidx':
                    chunk_slice1 = chunk[8:16]
                    chunk_slice2 = chunk[24:]
                    self.timescale = int.from_bytes(chunk_slice1[0:4], byteorder='big')
                    # earliest_presentation_time = int.from_bytes(chunk_slice1[4:], byteorder='big')

                    for i in range(0, len(chunk_slice2), 12):
                        self.Bytes.append(int.from_bytes(chunk_slice2[i:i + 4], byteorder='big'))
                        self.Times.append(int.from_bytes(chunk_slice2[i + 4:i + 8], byteorder='big'))
                offset += size
        else:
            print("请求head失败，状态码：" + str(response.status_code))
            self.error.emit(1)
            exit(1)

        # earliest_presentation_time 没有计算，可能会造成0.05s（earliest_presentation_time / timescale）左右误差
        self.start_box, start_pre = sum_exceeds_target(self.Times, self.timescale, self.start_time)
        self.end_box, end_pre = sum_exceeds_target(self.Times, self.timescale, self.end_time)

        self.start_frame.emit(start_pre / (self.end_box - self.start_box + 1))
        self.end_frame.emit((end_pre + self.end_box - self.start_box) / (self.end_box - self.start_box + 1))

        self.start_byte = offset + sum(self.Bytes[:self.start_box - 1])
        self.end_byte = offset + sum(self.Bytes[:self.end_box])

        self.headers["Range"] = f"bytes={self.start_byte}-{self.end_byte}"

    def get_mdat(self):
        response = requests.get(self.video_url, headers=self.headers, stream=True)
        if response.status_code == 206:
            offest = self.start_byte
            sequence_number = 1
            baseMediaDecodeTime = 0
            while offest < self.end_byte:
                chunk = response.iter_content(chunk_size=8).__next__()
                size = int.from_bytes(chunk[:4], byteorder='big')
                box_type = chunk[4:].decode('utf-8')
                self.video_data += chunk
                chunk = response.iter_content(chunk_size=size - 8).__next__()
                if box_type == 'moof':
                    chunk = chunk[:12] + sequence_number.to_bytes(4, byteorder='big') + chunk[16:]
                    chunk = chunk[:52] + baseMediaDecodeTime.to_bytes(4, byteorder='big') + chunk[56:]
                    sequence_number += 1
                    baseMediaDecodeTime += self.Times[self.start_box - 3 + sequence_number]
                self.video_data += chunk
                offest += size
                self.set_value.emit(int((offest - self.start_byte) / (self.end_byte - self.start_byte) * 100))
                # print(int((offest - self.start_byte) / (self.end_byte - self.start_byte) * 100))
        else:
            print("请求mdat失败，状态码：" + str(response.status_code))
            self.error.emit(1)
            exit(1)

    def merge(self):
        with open(self.path, mode='wb') as f:
            f.write(self.video_data)


if __name__ == "__main__":
    url = 'https://www.bilibili.com/video/BV1vG411Y7hW/'
    ProcessVideo(url, 100, 153, 'res/output_video.mp4').run()
