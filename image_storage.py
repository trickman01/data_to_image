import pygame as pg
from PIL import Image
import numpy as np
import math

def text_toBinary(text: str):
    bin_text = []
    for t in text:
        bin_text.append(bin(int(ord(t))))
    bin_text = list(map(lambda x: x.removeprefix('0b'), bin_text))
    bin_text = list(map(lambda x: x.zfill(8), bin_text))
    for index, b in enumerate(bin_text):
        if len(b) > 8:
            bin_text[index] = '00100000'
    bin_text = ''.join(bin_text)
    start = 0
    end = start + 2
    length = len(bin_text)
    bin_data = []
    while end <= length:
        bin_data.append(bin_text[start:end])
        start += 2
        end = start + 2
    return bin_data

def text_2_bin(text:str):
    bin_space = bin(ord(' ')).removeprefix('0b').zfill(8)
    bin_text = text.encode()
    bin_text = [bin(x).removeprefix('0b').zfill(8) for x in bin_text]
    for index, b in enumerate(bin_text):
        if b == bin_space or len(b) > 8:
            bin_text[index] = 'space'
    bin_text.append('stop')
    return bin_text

def get_text(file_path):
    with open(file_path, 'r') as r:
        text = r.read()
    return text

def make_colors():
    start = 0
    end = 255
    color_values = list(np.linspace(start, end, 4))
    color_values = list(map(lambda x: int(x), color_values))
    colors = [(x, x, x) for x in color_values]
    color_dict = dict()
    for index, color in enumerate(colors):
        color_dict[bin(index).removeprefix('0b').zfill(2)] = color
    color_dict['space'] = (0, 0, 255)
    color_dict['stop'] = (255, 0, 0)
    return color_dict

def encode_image(bin_data: list, colors: list, scale: int):
    colors = [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)]
    length = len(bin_data)
    sqroot = math.floor(math.sqrt(length))
    width = int(sqroot)
    height = width
    grow_axis = True
    while length + 2 >= (width * height):
        if grow_axis:
            height += 1
        else:
            width += 1
        grow_axis = not grow_axis
    surface = pg.Surface((width * scale, height * scale))
    index = 0
    color_dict = dict()
    for b in bin_data:
        offset_x = (index % width) * scale
        offset_y = (index // width) * scale
        color_dict[(offset_x, offset_y)] = colors[int(b, 2)]
        index += 1
    offset_x = (index % width) * scale
    offset_y = (index // width) * scale
    color_dict[(offset_x, offset_y)] = (255, 0, 0)
    for pos, color in color_dict.items():
        pg.draw.rect(surface, color, (pos[0], pos[1], scale, scale))
    pg.draw.rect(surface, (0, 255, 0), ((width * scale) - scale, (height * scale) - scale, scale, scale))
    pg.image.save(surface, 'test_save.png')

def encode_image_v2(bin_text: list, color_dict: dict, scale: int):
    bin_list = []
    b: str
    for b in bin_text:
        if b == 'space' or b == 'stop':
            bin_list.append(b)
        else:
            index = 0
            length = len(b)
            bin_vals = []
            while index + 2 < length + 1:
                bin_vals.append(b[index:index+2])
                index += 2
            bin_list += bin_vals
    list_length = len(bin_list)
    width, height = 0, 0
    change_width = True
    while (width * height) < (list_length + 1):
        if change_width:
            width += 1
        else:
            height += 1
        change_width = not change_width
    surface = pg.Surface((width * scale, height * scale))
    surface.fill((0, 0, 0))
    for dex, value in enumerate(bin_list):
        y_pos, x_pos = divmod(dex, width)
        pg.draw.rect(surface, color_dict[value], (x_pos * scale, y_pos * scale, scale, scale))
    pg.draw.rect(surface, (0, 255, 0), ((width * scale) - scale, (height * scale) - scale, scale, scale))
    pg.image.save(surface, 'test_output.png')

def decode_image(image_path: str, colors: list):
    colors = [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)]
    color_dict = dict()
    for index, value in enumerate(colors):
        color_dict[value] = index
    end_color = (255, 0, 0)
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    scale_x = width - 1
    scale_y = height - 1
    scale = 0
    scale_find = True
    data = []
    while scale_find:
        if pixels[scale_x, scale_y] == (0, 255, 0):
            scale_x -= 1
            scale += 1
        else:
            scale_find = False
    columns = width // scale
    rows = height // scale
    offset = scale / 2
    for r in range(rows):
        for c in range(columns):
            pos = (c * scale + offset, r * scale + offset)
            data.append(pixels[pos])
    end_data = data.index(end_color)
    data = data[:end_data]
    bin_data = []
    index = 1
    for d in data:
        binary = bin(color_dict[d]).removeprefix('0b').zfill(2)
        bin_data.append(binary)
        if index % 4 == 0:
            bin_data.append('-')
        index += 1
    bin_data = ''.join(bin_data)
    bin_data = bin_data.split('-')
    if '' in bin_data:
        bin_data.remove('')
    for index, b in enumerate(bin_data):
        bin_data[index] = chr(int(b, 2))
    bin_data = ''.join(bin_data)
    with open('out_text.txt', 'w') as w:
        w.write(bin_data)

def decode_image_v2(image_path: str, colors: dict):
    scale = 0
    image = Image.open(image_path)
    pixels = image.load()
    width, height = image.size
    x_pos = width - 1
    while pixels[x_pos, height - 1] == (0, 255, 0):
        scale += 1
        x_pos -= 1
    columns = width // scale
    rows = height // scale
    data = []
    for r in range(rows):
        for c in range(columns):
            x_pos = (c * scale) + (scale // 2)
            y_pos = (r * scale) + (scale // 2)
            data.append(pixels[x_pos, y_pos])
    data = data[0:data.index(colors['stop'])]
    color_lookup = dict()
    for key, value in colors.items():
        color_lookup[value] = key
    data = list(map(lambda x: color_lookup[x], data))
    letters = []
    d: str
    index = 0
    while index < len(data):
        if data[index] == 'space':
            index += 1
            letters.append('space')
        else:
            letters.append(''.join(data[index: index + 4]))
            index += 4
    for index, l in enumerate(letters):
        if l == 'space':
            letters[index] = bin(ord(' ')).removeprefix('0b').zfill(8)
    letters = list(map(lambda x: chr(int(x, 2)), letters))
    letters = ''.join(letters)
    with open('out_text.txt', 'w') as w:
        w.write(letters)
            


if __name__ == '__main__':
    text = get_text('in_text.txt')
    colors = make_colors()
    scale = 3
    # encode_image(text_toBinary(text), colors, 3)
    # decode_image('test_save.png', colors)
    bin_text = text_2_bin(text)
    encode_image_v2(bin_text, colors, scale)

    decode_image_v2('test_output.png', colors)