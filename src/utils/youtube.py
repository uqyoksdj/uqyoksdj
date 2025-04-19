from pytube import YouTube

# 创建YouTube对象
youtube = YouTube('https://www.youtube.com/watch?v=MjGdJ4Mpox4')

# 获取视频的所有可用流
streams = youtube.streams

# 遍历每个流对象并打印信息
for stream in streams:
    print("Resolution:", stream.resolution)
    print("File Type:", stream.type)
    print("MIME Type:", stream.mime_type)
    print("Video Codec:", stream.video_codec)
    print("Audio Codec:", stream.audio_codec)
    print("File Size:", stream.filesize)
    print("----------")

video_streams = streams.filter(mime_type='video/mp4', resolution='480p')
stream = video_streams.first()
print(stream.url)
stream.download()