# !/user/bin/env python
# -*- coding:utf-8 -*- 

import os
import argparse
from PIL import Image,ImageFont,ImageDraw
  
# 根据文本生成图片
def save_chars_image(text, image_path, font, is_debug = False):
    chars_x, chars_y = 0, 0
    chars_w, chars_h = font.getsize(text)
  
    if is_debug == True:
        chars_w = chars_w + 2
        chars_h = chars_h + 2
  
    im = Image.new("RGB", (chars_w, chars_h), (255, 255, 255))
    dr = ImageDraw.Draw(im)
  
    # 绘制文字边框
    if is_debug == True:
        coords = [(chars_x+1, chars_y+1), (chars_x+1, chars_y+chars_h-1),
                (chars_x+chars_w-1, chars_y+chars_h-1), (chars_x+chars_w-1,chars_y+1)]
        dr.polygon(coords, outline=(255, 0, 10))
  
    # 居中绘制文字
    dr.text((chars_x, chars_y), text, font=font, fill=(0,0,0), align='center')
    im.save(image_path)
 
def indexing(standards, new_chars, text):
    res = []
    for i in range(len(text)):
        try:
            res.append(standards.index(text[i])+1)
        except:
            new_chars.append(text[i])
            res.append(len(standards)+len(new_chars)+1)
    return res
  
def clear_invalid_chars(char_array):
    for i in range(len(char_array)):
        char_array[i] = char_array[i].strip('\n')

def main():
    parser = argparse.ArgumentParser(description='生成用于CnOcr训练的数据集')

    parser.add_argument("-root", "--root_dir",
        default="data",
        type=str,
        help="预训练配置目录",
	)

    parser.add_argument("-examples", "--examples_dir",
        default="examples",
        type=str,
        help="图片样本所在目录",
	)

    parser.add_argument("-font", "--font_path",
        default="fonts/卷卷桃心中文字体.ttf",
        type=str,
        help="待训练的字体路径",
	)

    parser.add_argument("-font_size", "--font_size",
        default=20,
        type=int,
        help="待训练的字体大小",
	)

    parser.add_argument("-label", "--label_path",
        default="label_cn.txt",
        type=str,
        help="文本原料",
	)

    parser.add_argument("-train", "--train_name",
        default="train.txt",
        type=str,
        help="训练样本名",
	)

    parser.add_argument("-test", "--test_name",
        default="test.txt",
        help="测试样本名",
	)

    parser.add_argument("-is_test", "--is_test",
        action="store_true",
        help="是否生成测试图片",
	)

    parser.add_argument("-test_text", "--test_text",
        default="",
        help="测试文本",
	)

    args = parser.parse_args()

    root_dir = args.root_dir
    images_dir = args.examples_dir
  
    label_path = args.label_path
    train_path = args.train_name
    test_path = args.test_name
  
    font = ImageFont.truetype(args.font_path, args.font_size)
 
    label_file = open(label_path, 'r', encoding='utf-8')
 
    train_file = open(os.path.join(root_dir, train_path), 'w', encoding='utf-8')
    test_file = open(os.path.join(root_dir, test_path), 'w', encoding='utf-8')
 
    standards = label_file.readlines()
    clear_invalid_chars(standards)
  
    new_chars = []
 
    label_file.close()

    if args.is_test and len(args.test_text) > 0:
        image_path = "test.png"
        save_chars_image(args.test_text, image_path, font=font)
        return
  
    # 生成用于训练的图片集
    for i in range(len(standards)):
        text = standards[i]
        idxes = indexing(standards, new_chars, text)
 
        cnt = "train_%06d.jpg" % (i+1)
        image_path = os.path.join(images_dir, cnt)
        save_chars_image(text, image_path, font=font)
  
        for idx in idxes:
            cnt = cnt + " {}".format(idx)
        train_file.write(cnt+'\n')
    train_file.close()
 
    # 生成用于测试的图片集
    for i in range(len(standards)):
        if (i+1) % 30 == 0:
            text = standards[i]
            idxes = indexing(standards, new_chars, text)
 
            cnt = "test_%06d.jpg" % (i+1)
            image_path = os.path.join(images_dir, cnt)
            save_chars_image(text, image_path, font=font)
  
            for idx in idxes:
                cnt = cnt + " {}".format(idx)
            test_file.write(cnt+'\n') 
    test_file.close()
 
    # 追加新增字符
    label_file = open(label_path, 'a', encoding='utf-8')
    for new_char in new_chars:
        label_file.write(new_char+'\n')
    label_file.close()

if __name__ == '__main__':
    main()