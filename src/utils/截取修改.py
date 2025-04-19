def read_head(file):
    new_file_path = 'res/head.txt'
    with open(new_file_path, 'wb') as new_file:
        num = 0
        while True:
            # 读取box的大小
            size_bytes = file.read(4)
            if len(size_bytes) < 4:
                break
            size = int.from_bytes(size_bytes, byteorder='big')

            # 读取box的类型
            type_bytes = file.read(4)
            if len(type_bytes) < 4:
                break
            box_type = type_bytes.decode('utf-8')

            # 保存原始的box内容
            box_content = file.read(size - 8)

            if box_type == 'moof':  # 掐头
                break
            elif box_type == 'ftyp' or box_type == 'moov':
                new_file.write(size_bytes + type_bytes + box_content)
            else:
                continue


def read_fragmented(file):
    index = 1
    while True:
        size_bytes = file.read(4)
        if len(size_bytes) < 4:
            break
        size = int.from_bytes(size_bytes, byteorder='big')

        # 读取box的类型
        type_bytes = file.read(4)
        if len(type_bytes) < 4:
            break
        box_type = type_bytes.decode('utf-8')

        # 保存原始的box内容
        box_content = file.read(size - 8)

        if box_type == 'moof':  # moof 和 mdat 选取
            with open(f'res/fragmented/{index}.txt', 'wb') as f:
                f.write(size_bytes + type_bytes + box_content)
        elif box_type == 'mdat':
            with open(f'res/fragmented/{index}.txt', 'ab') as f:
                f.write(size_bytes + type_bytes + box_content)
            index += 1


def modify_moof(file, new_file, sequence_number):
    with open(file, 'rb') as f:
        original_data = f.read()

    # 将第20到24个字节替换为新的字节序列
    x = 0
    new_data = original_data[:20] + sequence_number.to_bytes(4, byteorder='big') + original_data[24:]
    new_data = new_data[:60] + x.to_bytes(4, byteorder='big') + new_data[64:]

    # 将修改后的数据写入新文件
    with open(new_file, 'wb') as f:
        f.write(new_data)


# with open('res/老板的私货1.mp4', 'rb') as f:
#     read_head(f)
#     f.seek(0)
#     read_fragmented(f)

modify_moof('res/fragmented/3.txt', 'res/mdat.txt', 1)
