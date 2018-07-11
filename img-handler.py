from os import listdir
from PIL import Image
from math import ceil

print("图片拼接工具")
print("作者：1038761793@qq.com")
print("本程序仅支持.png、.jpg格式图片的拼接，所有图片必须为相同格式，以下用.png举例，.jpg同理")
print("将所有待拼接图片放到一个文件夹，依次命名为 '行-列.png'")
print("例如你想将6张图片拼接成3列，那么应该依次命名为 '1-1.png', '1-2.png', '1-3.png', '2-1.png', '2-2.png', '3-3.png'")
print("输出的图片保存在当前目录，文件名为'result.png'")
print("该软件的使用完全自愿，作者不对该软件的安全性做任何保证，凡是使用该软件导致的任何问题，作者一概不负责。")


def s(fn):
  li = fn[:-4].split("-")
  return (int(li[0]), int(li[1]))


filelist = [f for f in listdir() if f.endswith(".png") or f.endswith(".jpg")]

imglist = [Image.open(f) for f in sorted(filelist, key=s) if f.endswith(".png") or f.endswith(".jpg")]
cols = 1
try:
  cols = int(input("你想要拼成几列？(默认1列)"))
except ValueError as e:
  cols = 1

rows = ceil(len(imglist)/cols)

w, h = imglist[0].size

result = Image.new(imglist[0].mode, (w*cols, h*rows))

for r in range(rows):
  for c in range(cols):
    i = r * cols +c
    if(i < len(imglist)):
      # print(imglist[i], c * w, r * h)
      result.paste(imglist[i], box=(c * w, r * h))

result.save("result.png")
print("拼接完成")