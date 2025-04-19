from moviepy.editor import *


def sum_exceeds_target(nums, target):
    current_sum = 0
    for count, num in enumerate(nums, 1):
        current_sum += num
        if current_sum > target:
            return count
    return count

def read_head(file, param):
    global timescale
    with open(param, 'wb') as new_file:
        offest = 0
        while True:
            print(offest)
            size_bytes = file.read(4)
            if len(size_bytes) < 4:
                break
            size = int.from_bytes(size_bytes, byteorder='big')

            type_bytes = file.read(4)
            if len(type_bytes) < 4:
                break
            box_type = type_bytes.decode('utf-8')

            box_content = file.read(size - 8)

            if box_type == 'ftyp' or box_type == 'moov':
                new_file.write(size_bytes + type_bytes + box_content)
            elif box_type == 'sidx':
                chunk_slice1 = box_content[8:16]
                chunk_slice2 = box_content[24:]
                timescale = int.from_bytes(chunk_slice1[0:4], byteorder='big')
                earliest_presentation_time = int.from_bytes(chunk_slice1[4:], byteorder='big')
                print(timescale, earliest_presentation_time)
                for i in range(0, len(chunk_slice2), 12):
                    Bytes.append(int.from_bytes(chunk_slice2[i:i + 4], byteorder='big'))
                    Times.append(int.from_bytes(chunk_slice2[i + 4:i + 8], byteorder='big') // timescale)
            elif box_type == 'moof':
                break
            offest += size
    return offest


def read_mdat(file, param):
    with open(param, 'wb') as new_file:
        file.seek(start_byte)
        offest = start_byte
        sequence_number = 1
        baseMediaDecodeTime = 0
        while offest < end_byte:
            size_bytes = file.read(4)
            if len(size_bytes) < 4:
                break
            size = int.from_bytes(size_bytes, byteorder='big')

            type_bytes = file.read(4)
            if len(type_bytes) < 4:
                break
            box_type = type_bytes.decode('utf-8')

            if box_type == 'moof':
                box_content = file.read(12)

                file.read(4)
                box_content += sequence_number.to_bytes(4, byteorder='big')
                sequence_number += 1

                box_content += file.read(36)

                file.read(4)
                box_content += baseMediaDecodeTime.to_bytes(4, byteorder='big')
                baseMediaDecodeTime += Times[start_box - 3 + sequence_number] * timescale

                box_content += file.read(size - 64)
            elif box_type == 'mdat':
                box_content = file.read(size - 8)
            else:
                continue
            new_file.write(size_bytes + type_bytes + box_content)
            offest += size
        print('结束位置：', offest)

def modify_time(file, times):
    with open(file, 'r+b') as f:
        size = int.from_bytes(f.read(4), byteorder='big')
        print(size + 136)
        f.seek(size + 136)
        f.write(times.to_bytes(4, byteorder='big'))


Times = []
Bytes = []
timescale = 0
start_time = 53
end_time = 96
file = 'res/1.mp4'

with open(file, 'rb') as f:
    offset = read_head(f, 'res/head.txt')
    f.seek(0)

    start_box = sum_exceeds_target(Times, start_time)
    end_box = sum_exceeds_target(Times, end_time)
    start_byte = offset + sum(Bytes[:start_box - 1])
    end_byte = offset + sum(Bytes[:end_box])
    print(start_box, end_box)
    print(start_byte, end_byte)

    read_mdat(f, 'res/mdat.txt')


with open('res/head.txt', 'rb') as file1:
    content1 = file1.read()

with open('res/mdat.txt', 'rb') as file2:
    content2 = file2.read()

with open('res/merged_file1.mp4', 'wb') as merged_file:
    merged_file.write(content1 + content2)

# times = sum(Times[start_box - 1:end_box]) * 1000
# print(times)
#
# offset_time = sum(Times[:start_box - 1])
# video = CompositeVideoClip([VideoFileClip("res/merged_file1.mp4").subclip(start_time - offset_time,
#                                                                           end_time - offset_time)])
#
# video.write_videofile("res/output_video1.mp4")
