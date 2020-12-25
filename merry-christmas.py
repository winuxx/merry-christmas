#-*- coding:utf-8 -*-#
# author: Qian | kk4201@126.com


import sys
import random
import time
import os
import unicodedata


poster = ' Merry Christmas! '
star_density = 16
snow_density = 12  # 数字越小雪越密集
min_density = 1
max_density = 32

gap = ' '
snows = ['❄❆', '❅✲']
wood = '#'
stars = ['☆★', '◆◇', '△▲']

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
        self.lines_ = []
        self.trunk_height = 0

    def set_density(self):
        density = max_density - star_density
        if density < min_density:
            self.density = min_density
        if density > max_density:
            density = max_density
        return density

    def generate_branch_part(self, start):
        height = random.randrange(5, 9)
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
        branch = []
        width_start = 1
        for i in range(part_number):
            if i > 0 and width_start < 5:
                width_start = 5
            part = self.generate_branch_part(width_start)
            branch += part
            shrink = random.randrange(8, 12, 2)
            width_start = part[-1] - shrink
        return branch

    def generate_trunk(self):
        width = random.randrange(5, 7)
        height = random.randrange(3, 5)
        self.trunk_height = height
        return [width] * height

    def generate_data(self):
        tree_data = {}
        branch = self.generate_branch()
        trunk = self.generate_trunk()

        tree_height = len(branch) + len(trunk)
        if tree_height <= self.max_height:
            sky = [0] * (self.total_height - tree_height)
            tree_data['branch'] = sky + branch
        else:
            sky = [0] * (self.total_height - self.max_height)
            tree_data['branch'] = sky + branch[0:(self.max_height-len(trunk))]

        tree_data['trunk'] = trunk

        return tree_data

    def generate_line(self, width, is_branch=True):
        actual_width = 0
        line_filled = ''
        filling_last = ''
        for i in range(width):
            star_pair = random.choice(stars)
            star = random.choice(star_pair)

            # 防止星星连续
            if filling_last != wood:
                filling = wood
            else:
                # 减少星星出现的概率
                # 若有嵌套递归, random range 过大会报错
                flag = random.randrange(0, self.density)
                if flag == 0 and is_branch:
                    filling = star
                else:
                    filling = wood

            line_filled += filling
            filling_last = filling

            # 宽字符占2格
            if is_wide_char(filling):
                actual_width += 2
            else:
                actual_width += 1

        len_side = int((self.total_width - actual_width) / 2)
        line = gap * len_side + line_filled + gap * len_side

        return line

    def generate_frame(self):
        data = self.generate_data()

        # 顶上预留一行空白, 以突出树尖
        line = gap * self.total_width
        self.lines_.append(line)
        for width in data['branch']:
            line = self.generate_line(width)
            self.lines_.append(line)
        for width in data['trunk']:
            line = self.generate_line(width, False)
            self.lines_.append(line)

    def star_bling(self):
        lines = []
        for row in self.lines_:
            line = ''
            for col in row:
                for star in stars:
                    if col in star:
                        flag = random.randrange(0, 2)
                        if flag == 0:
                            col_new = star.split(col)
                            col_new.remove('')
                            col = col_new[0]
                        break
                line += col
            lines.append(line)

        self.lines_ = lines

    def get_frame(self):
        return '\n'.join(self.lines_)

class Snow():
    def __init__(self):
        self.total_width = terminal_width
        self.total_height = terminal_height
        self.density = self.set_density()
        self.lines_ = []

    def set_density(self):
        density = max_density - snow_density
        if density < min_density:
            self.density = min_density
        if density > max_density:
            density = max_density
        return density

    def generate_line(self):
        line = ''
        filling_last = ''
        for i in range(self.total_width-1):
            snow_pair = random.choice(snows)
            snow = random.choice(snow_pair)

            # 防止雪花连续
            if filling_last != gap:
                line += gap
                filling_last = gap
                continue

            # filling = random.choice([snow, gap])

            # 减少雪花出现的概率
            # 若有嵌套递归, random范围过大会报错
            flag = random.randrange(0, self.density)
            if flag == 0:
                filling = snow
            else:
                filling = gap

            filling_last = filling
            line += filling

        # 舍弃雪花过少的行
        # 递归, 会与random嵌套
        # if line.count(snow) < (self.total_width / 8):
            # line = self.snow_line()

        return line

    def generate_frame(self):
        if len(self.lines_) == 0:
            for i in range(self.total_height):
                line = self.generate_line()
                self.lines_.append(line)
        else:
            line = self.generate_line()
            self.lines_.pop()
            self.lines_.insert(0, line)

    def snow_bling(self):
        lines = []
        for row in self.lines_:
            line = ''
            for col in row:
                for snow in snows:
                    if col in snow:
                        flag = random.randrange(0, 2)
                        if flag == 0:
                            col_new = snow.split(col)
                            col_new.remove('')
                            col = col_new[0]
                        break
                line += col
            lines.append(line)
        self.lines_ = lines

    def get_frame(self):
        return '\n'.join(self.lines_)

def mix_frames(tree, snow):
    tree_lines = tree.split('\n')
    snow_lines = snow.split('\n')

    frame = ''

    for i in range(terminal_height):
        tree_line = tree_lines[i]
        snow_line = snow_lines[i]

        line = ''
        j = 0
        actual_width = 0
        while actual_width < terminal_width:
            filling = ''
            if j < len(tree_line) and tree_line[j] != gap:
                filling = tree_line[j]
            elif j < len(snow_line):
                filling = snow_line[j]
            else:
                filling = gap

            j += 1

            # 宽字符占2格
            if is_wide_char(filling):
                actual_width += 2
            else:
                actual_width += 1

            if actual_width < terminal_width:
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
    tree = Tree()
    snow = Snow()
    tree.generate_frame()
    while 1:
        tree.star_bling()
        tree_frame = tree.get_frame()
        snow.generate_frame()
        snow.snow_bling()
        snow_frame = snow.get_frame()
        frame = mix_frames(tree_frame, snow_frame)

        sys.stdout.write(frame)
        sys.stdout.flush()

        time.sleep(0.4)

if __name__ == '__main__':
    get_terminal_size()
    # os.system("mode con lines=%s" % terminal_height)

    # poster = input('祝福语 (%s)\n> : ' % poster) or poster
    # star_density = int(input('星星密集度 (%s - %s) %s\n> : ' % (min_density, max_density, star_density)) or star_density)
    # snow_density = int(input('雪花密集度 (%s - %s) %s\n> : ' % (min_density, max_density, snow_density)) or snow_density)

    # print_tree()
    # print_snow()

    run()
