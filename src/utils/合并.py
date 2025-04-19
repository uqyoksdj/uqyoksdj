# 打开第一个文件进行读取
with open('res/head.txt', 'rb') as file1:
    content1 = file1.read()

# 打开第二个文件进行读取
with open('res/mdat.txt', 'rb') as file2:
    content2 = file2.read()

# 合并两个文件的内容
merged_content = content1 + content2

# 打开一个新文件进行写入合并后的内容
with open('res/merged_file.mp4', 'wb') as merged_file:
    merged_file.write(content1 + content2)