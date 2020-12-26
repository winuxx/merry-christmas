#-*- coding:utf-8 -*-#
# author: Qian | kk4201@126.com


import sys
import random
import time
import os
import unicodedata


poster = ' Merry Christmas! '
star_density = 16
snow_density = 8
min_density = 1
max_density = 32
speed = 4
min_speed = 1
max_speed = 10
is_snow_cover = False

air = ' '
woods = ['-', '|']
stars = ['☆★', '◇◆', '△▲']
snows = ['❅❆', '✲❄', '✡✱']
snow_cover = '✡✱'

char_map = {
    'placeholder': -1,
    'air': 0,
    'wood': 1,
    'star': 2,
    'snow': 3,
    'snow_cover': 4,
}

terminal_width = 0
terminal_height = 0


def get_terminal_size():
    global terminal_width, terminal_height
    terminal_width = os.get_terminal_size().columns
    terminal_height = os.get_terminal_size().lines

def is_wide_char(letter):
    # East_Asian_Width (ea)
    # ea ; A     ; Ambiguous    不确定
    # ea ; F     ; Fullwidth    全宽
    # ea ; H     ; Halfwidth    半宽
    # ea ; N     ; Neutral      中性
    # ea ; Na    ; Narrow       窄
    # ea ; W     ; Wide         宽
    return unicodedata.east_asian_width(letter) in ['F', 'W', 'A']

class Tree():
    def __init__(self):
        self.total_width = terminal_width
        self.total_height = terminal_height
        self.max_height = int(self.total_height * 0.707)
        self.step = random.choice([2, 4])
        self.density = self.set_density()
        self.frame_ = []
        self.trunk_height = 0

    def set_density(self):
        global star_density
        if star_density < min_density:
            star_density = min_density
        if star_density > max_density:
            star_density = max_density
        density = max_density - star_density + 1
        return density

    def generate_branch_part(self, start):
        tree_top = [1, 3]
        height = random.randrange(5, 9)
        if start == 1:
            part = tree_top + list(range(5, start+(height*self.step), self.step))
        else:
            part = list(range(start, start+(height*self.step), self.step))
        i = 0
        for width in part:
            if width >= self.total_width:
                part = part[0:i]
                break
            i += 1
        return part

    def generate_branch(self):
        part_number = random.randrange(5, 9)
        shrink = random.randrange(8, 12, 2)

        branch = []
        width_start = 1
        for i in range(part_number):
            if i > 0 and width_start < 5:
                width_start = 5
            part = self.generate_branch_part(width_start)
            branch += part
            width_start = part[-1] - shrink
            shrink += 4
        return branch

    def generate_trunk(self):
        # 树干居中
        # 若树顶宽度为1，树干宽度取奇数
        # 若宽度为2，树干宽度取偶数
        width = random.choice([5, 7])
        height = random.randrange(3, 5)
        self.trunk_height = height
        return [width] * height

    def generate_data(self):
        tree_data = {}
        branch = self.generate_branch()
        trunk = self.generate_trunk()

        tree_height = len(branch) + len(trunk)
        if tree_height <= self.max_height:
            sky = [char_map['air']] * (self.total_height - tree_height)
            tree_data['sky'] = sky
            tree_data['branch'] = branch
        else:
            sky = [char_map['air']] * (self.total_height - self.max_height)
            tree_data['sky'] = sky
            tree_data['branch'] = branch[0:(self.max_height-len(trunk))]

        tree_data['trunk'] = trunk

        return tree_data

    def generate_row(self, width, is_trunk=False):
        row_filled = []
        wood_0 = char_map['wood'] * 10 + 0
        wood_1 = char_map['wood'] * 10 + 1
        for i in range(width):
            filling = ''
            if is_trunk:
                col = wood_1
                filling = woods[1]
            # 防止星星连续
            elif i > 0 and str(row_filled[i-1])[0] != str(char_map['wood']):  # star or placeholder
                col = wood_0
                filling = woods[0]
            else:
                # 减少星星出现的概率
                # 若有嵌套递归, random range 过大会报错
                flag = random.randrange(self.density)
                if flag == 0:
                    star_pair = random.randrange(len(stars))
                    star = random.randrange(len(stars[star_pair]))
                    # 201: stars[0][1]
                    col = char_map['star'] * 100 + star_pair * 10 + star
                    filling = stars[star_pair][star]
                else:
                    wood = random.randrange(len(woods))
                    col = char_map['wood'] * 10 + wood
                    filling = woods[wood]

            row_filled.append(col)

            # 宽字符占2格
            if is_wide_char(filling):
                row_filled.append(char_map['placeholder'])

        # 星星为全宽字符, 故需要计算实际宽度
        actual_width = len(row_filled)
        len_side = int((self.total_width - actual_width) / 2)
        row = [char_map['air']] * len_side + row_filled + [char_map['air']] * len_side

        return row

    def generate_frame(self):
        data = self.generate_data()

        row = []
        for width in data['sky']:
            row = self.generate_row(width)
            self.frame_.append(row)
        for width in data['branch']:
            row = self.generate_row(width)
            self.frame_.append(row)
        for width in data['trunk']:
            row = self.generate_row(width, is_trunk=True)
            self.frame_.append(row)

    def bling(self):
        frame_new = []
        row_number = 0
        for row in self.frame_:
            row_new = []
            for col in row:
                # col: -1, 0, 1xx, 2xx
                # 若此处判断不包含wood, 则wood(包括trunk)填充也会随机变化
                if int(col/10) < char_map['wood']:
                    row_new.append(col)
                elif int(col/10) == char_map['wood'] \
                and row_number >= self.total_height - self.trunk_height:
                    row_new.append(col)
                else:
                    # 减少闪烁频率
                    # flag = random.randrange(2)
                    new = random.randrange(2)
                    # 若wood未被排除, 则wood也会随机变化
                    col_new = int(str(col)[0:-1]) * 10 + new
                    row_new.append(col_new)
            frame_new.append(row_new)
            row_number += 1

        self.frame_ = frame_new

    def get_frame(self):
        return self.frame_

class Snow():
    def __init__(self):
        self.total_width = terminal_width
        self.total_height = terminal_height
        self.density = self.set_density()
        self.frame_ = []

    def set_density(self):
        global snow_density
        if snow_density < min_density:
            snow_density = min_density
        if snow_density > max_density:
            snow_density = max_density
        density = max_density - snow_density + 1
        return density

    def generate_row(self):
        row = []
        for i in range(self.total_width-1):
            # 防止雪花连续
            if i > 0:
                col_last = row[i-1]
                if col_last != char_map['air']:
                    row.append(char_map['air'])
                    col_last = char_map['air']
                    continue

            col = 0
            # 减少雪花出现的概率
            # 若有嵌套递归, random范围过大会报错
            flag = random.randrange(0-self.density, self.density)
            if flag == 0:
                snow_pair = random.randrange(len(snows))
                snow = random.randrange(len(snows[snow_pair]))
                col = char_map['snow'] * 100 + snow_pair * 10 + snow
            else:
                col = char_map['air']
            row.append(col)

        return row

    def generate_frame(self):
        if len(self.frame_) == 0:
            for i in range(self.total_height):
                row = self.generate_row()
                self.frame_.append(row)
        else:
            row = self.generate_row()
            self.frame_.pop()
            self.frame_.insert(0, row)

    def bling(self):
        frame_new = []
        for row in self.frame_:
            row_new = []
            for col in row:
                if str(col)[0] != str(char_map['snow']):
                    row_new.append(col)
                else:
                    snow = random.randrange(2)
                    col_new = int(str(col)[0:-1]) * 10 + snow
                    row_new.append(col_new)
            frame_new.append(row_new)
        self.frame_ = frame_new

    def get_frame(self):
        return self.frame_

def mix_frames(tree_frame, snow_frame):
    frame = ''

    for i in range(terminal_height):
        tree_row = tree_frame[i]
        snow_row = snow_frame[i]

        line = ''
        for j in range(terminal_width):
            if j >= len(tree_row) or j >= len(snow_row):
                break

            filling = ''
            tree_col = tree_row[j]
            snow_col = snow_row[j]
            if is_snow_cover:
                # 雪覆盖树
                # star 长亮, 被雪覆盖才变暗
                mix_col = snow_col or tree_col
            else:
                # 树覆盖雪
                # 只判断tree_col, 否则若上一个col雪为宽字符而树不是, 则树会出现一位空白
                mix_col = tree_col or snow_col

            if mix_col == char_map['placeholder']:
                continue
            elif str(mix_col)[0] == str(char_map['wood']):
                filling = woods[int(str(mix_col)[1])]
            elif str(mix_col)[0] == str(char_map['star']):
                if is_snow_cover:
                    filling = stars[int(str(mix_col)[1])][1]
                else:
                    filling = stars[int(str(mix_col)[1])][int(str(mix_col)[2])]
            elif str(mix_col)[0] == str(char_map['snow']):
                if is_snow_cover:
                    if tree_col == char_map['wood']:
                        filling = snow_cover[0]
                    elif str(tree_col)[0] == str(char_map['star']):
                        filling = stars[int(str(tree_col)[1])][0]
                    else:
                        filling = snows[int(str(mix_col)[1])][int(str(mix_col)[2])]
                else:
                    filling = snows[int(str(mix_col)[1])][int(str(mix_col)[2])]
            else:
                filling = air

            line += filling

        if (i == int(terminal_height * 0.2)):
            len_side = int((terminal_width - len(poster)) / 2)
            line = line[0:len_side+1] + poster + line[terminal_width-len_side:-1]

        frame += line
        if i < terminal_height -1:
            frame += '\n'

    return frame

def print_tree():
    tree = Tree()
    tree.generate_frame()
    frame = tree.get_frame()
    sys.stdout.write(frame)
    sys.stdout.flush()

def print_snow():
    snow = Snow()
    snow.generate_frame()
    frame = snow.get_frame()
    sys.stdout.write(frame)
    sys.stdout.flush()

def run():
    global speed

    tree = Tree()
    snow = Snow()
    tree.generate_frame()
    while 1:
        tree.bling()
        tree_frame = tree.get_frame()
        snow.generate_frame()
        snow.bling()
        snow_frame = snow.get_frame()
        frame = mix_frames(tree_frame, snow_frame)

        sys.stdout.write(frame)
        sys.stdout.flush()

        if speed < min_speed:
            speed = min_speed
        if speed > max_speed:
            speed = max_speed
        delay = max_speed - speed + 1
        time.sleep(delay/10)

if __name__ == '__main__':
    get_terminal_size()
    # os.system("mode con lines=%s" % terminal_height)
    os.system('cls')

    custom = input('自定义 Custom ? (y/N)\n> : ')
    if custom.lower() == 'y':
        poster = input('祝福语 (%s)\n> : ' % poster) or poster
        star_density = int(input('星星密集度 (%s - %s) %s\n> : ' % (min_density, max_density, star_density)) or star_density)
        snow_density = int(input('雪花密集度 (%s - %s) %s\n> : ' % (min_density, max_density, snow_density)) or snow_density)
        speed = int(input('刷新速度 (%s - %s) %s\n> : ' % (min_speed, max_speed, speed)) or speed)
        choose_snow_cover = input('雪花覆盖树? (y/N)\n> : ')
        if choose_snow_cover.lower() == 'y':
            is_snow_cover = True

    # print_tree()
    # print_snow()

    run()
