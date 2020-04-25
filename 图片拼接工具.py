from typing import List, Tuple, TypeVar, Any
from PIL import Image
from tangUtils.main import Base, question, questionInt, Cmd, runCmdList, getInputFiles
import math, time, random

Size = Tuple[int, int]
Box = Tuple[int, int, int, int]

def geneJpg(size: Size):
  return Image.new("RGB", size, (255, 255, 255))

# Box: (left, upper, right, lower)
def paste(_from, _to, box: Box):
  toBeExtend = _to.size[0] < box[2] or _to.size[1] < box[3]
  if toBeExtend:
    newSize = (max(_to.size[0], box[2]), max(_to.size[1], box[3]))
    result = geneJpg(newSize)
    result.paste(_to, box=(0, 0))
    result.paste(_from, box=box)
    return result
  else:
    _to.paste(_from, box=box)
    return _to

def withinSize(origin: Size, target: Size) -> Size:
  if (target[0] <= 0) or (origin[0] / origin[1] < target[0] / target[1]): # 瘦高
    return (int(origin[0] * target[1] / origin[1]), target[1])
  return (target[0], int(origin[1] * target[0] / origin[0]))

# 瀑布流
def mergeFallingHorizon(paths: List[str], rows: int = 1, height: int = 512):
  imgs = [Image.open(p) for p in paths]
  base = geneJpg((1, 1))
  sides = [n - n for n in range(rows)]
  for im in imgs:
    newSize = withinSize(im.size, (-1, height))
    minSide = min(sides)
    col = sides.index(minSide)
    box = (minSide, col * height, minSide + newSize[0], col * height + newSize[1])
    base = paste(im.resize(newSize, Image.LANCZOS), base, box)
    sides[col] += newSize[0]
  return base

def mergeFallingVertical(paths: List[str], cols: int = 1, width: int = 512):
  imgs = [Image.open(p) for p in paths]
  base = geneJpg((1, 1))
  sides = [n - n for n in range(cols)]
  for im in imgs:
    newSize = withinSize(im.size, (width, -1))
    minSide = min(sides)
    row = sides.index(minSide)
    box = (row * width, minSide, row * width + newSize[0], minSide + newSize[1])
    base = paste(im.resize(newSize, Image.LANCZOS), base, box)
    sides[row] += newSize[1]
  return base

def mergeHorizon(paths: List[str], rows: int = 1, height: int = 512):
  imgs = [Image.open(p) for p in paths]
  total = len(imgs)
  cols = math.ceil(total / rows)
  base = geneJpg((1, 1))
  corner = [0, 0]
  for row in range(rows):
    corner[0] = 0
    corner[1] = height * row
    for col in range(cols):
      i = row * cols + col
      if i >= total:
        return base
      im = imgs[i]
      w, h = im.size
      newSize = (math.ceil(w * height / h), height)
      resizedIm = im.resize(newSize, Image.LANCZOS)
      newBox = (corner[0], corner[1], corner[0] + newSize[0], corner[1] + newSize[1])
      base = paste(resizedIm, base, newBox)
      corner[0] += newSize[0]
  return base

def mergeVertical(paths: List[str], cols: int = 1, width: int = 512):
  imgs = [Image.open(p) for p in paths]
  total = len(imgs)
  rows = math.ceil(total / cols)
  base = geneJpg((1, 1))
  corner = [0, 0]
  for col in range(cols):
    corner[0] = width * col
    corner[1] = 0
    for row in range(rows):
      i = col * rows + row
      if i >= total:
        return base
      im = imgs[i]
      w, h = im.size
      newSize = (width, math.ceil(h * width / w))
      resizedIm = im.resize(newSize, Image.LANCZOS)
      newBox = (corner[0], corner[1], corner[0] + newSize[0], corner[1] + newSize[1])
      base = paste(resizedIm, base, newBox)
      corner[1] += newSize[1]
  return base

if __name__ == "__main__":
  availableSuffix = [".png", ".jpg", ".jpeg", ".bmp", ".ico", ".tga", ".tiff"]
  print("""
  --- 一个图片拼接工具 ---
  直接将多个图片或文件夹拖拽到.exe文件上就可以了
  支持【%s】后缀的文件
  如果图片尺寸较大/较多, 可能会有些慢, 请耐心等候
  【ctrl + C】可终止程序
  """ % " ".join(availableSuffix))
  allFiles = getInputFiles()
  paths = []
  for f in allFiles:
    if f.suffix.lower() in availableSuffix:
      paths.append(f.path)
    else:
      print("【图片不合格, 已跳过】%s" % f.path)
  if len(paths) == 0:
    print("输入图片为空")
  else:
    try:
      resultName = "图片拼接--%s--%s" % (time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()), random.randint(1, 10000))
      result = Base(paths[0]).parent.childOf("%s.jpg" % resultName)
      result.parent.createAsDir()
      firIm = Image.open(paths[0])
      size = firIm.size
      runCmdList([
        Cmd("按图片尺寸智能(并不)排序", next=[
          Cmd("水平排列", callback=lambda: mergeFallingHorizon(paths, questionInt("排几行(请输入正整数)", 1), questionInt("单张图片高度(请输入正整数)", size[1])).save(result.path, optimize=True, quality=92, progressive=True, subsampling=1)),
          Cmd("竖直排列", callback=lambda: mergeFallingVertical(paths, questionInt("排几列(请输入正整数)", 1), questionInt("单张图片宽度(请输入正整数)", size[0])).save(result.path, optimize=True, quality=92, progressive=True, subsampling=1)),
        ]),
        Cmd("按文件名一张一张排", next=[
          Cmd("水平排列", callback=lambda: mergeHorizon(paths, questionInt("排几行(请输入正整数)", 1), questionInt("单张图片高度(请输入正整数)", size[1])).save(result.path, optimize=True, quality=92, progressive=True, subsampling=1)),
          Cmd("竖直排列", callback=lambda: mergeVertical(paths, questionInt("排几列(请输入正整数)", 1), questionInt("单张图片宽度(请输入正整数)", size[0])).save(result.path, optimize=True, quality=92, progressive=True, subsampling=1)),
        ]),
      ])
      print("图片已保存到 %s" % result.path)
    except Exception as e:
      print(e)
  question("程序已结束, 按Enter键关闭程序", "Y")
