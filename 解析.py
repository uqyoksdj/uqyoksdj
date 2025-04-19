def modify_sidx_box(file, new_file_path):
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

            if box_type == 'sidx':
                new_sidx = box_content[:24]
                box_content = box_content[24:]
                timescale = int.from_bytes(new_sidx[8:12], byteorder='big')
                earliest_presentation_time = int.from_bytes(new_sidx[12:16], byteorder='big')
                number = int.from_bytes(new_sidx[16:], byteorder='big')
                print(timescale, earliest_presentation_time, number)
                new_sidx = new_sidx[:16] + sub(new_sidx[16:], number // 2)
                for i in range(0, len(box_content), 12):
                    chunk = box_content[i:i + 12]
                    if i // 12 < number - number // 2:
                        new_sidx += chunk
                        print(' '.join(hex(byte)[2:] for byte in chunk))
                    else:
                        break
                new_file.write(sub(size_bytes, number // 2 * 12) + type_bytes + new_sidx)
                num = number - number // 2

            elif box_type == 'moof':
                num -= 1
                if num >= 0:
                    new_file.write(size_bytes + type_bytes + box_content)
                else:
                    break
            else:
                new_file.write(size_bytes + type_bytes + box_content)


def sub(byte_str, subtract_value):
    num = int.from_bytes(byte_str, byteorder='big') - subtract_value
    result = num.to_bytes(len(byte_str), byteorder='big')
    return result


# 打开MP4文件
with open('res/老板的私货.mp4', 'rb') as f:
    modify_sidx_box(f, 'res/new_file1.mp4')
