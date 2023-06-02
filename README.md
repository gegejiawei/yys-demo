# yys-demo

## Introduction

#### status: developing(完善各种 dual 模式)

#### version: 3.1.1

#### last update: 2020.11.02

## Requirement

#### python3.6.4 or later

#### pywin32

-   installation: `pip install pywin32`
-   useage: `import win32gui, import win32api`

#### PIL(pillow)

-   installation: `pip install pillow`
-   useage: `import PIL` or `from PIL import Image`

#### mss

-   installation: `pip install mss`
-   useage: `from mss import mss`

#### keyboard

-   installation: `pip install keyboard`
-   useage: `import keyboard`

#### pyautogui

-   installation: `pip install pyautogui`
-   useage: `import pyautogui`

#### pyopencv

-   installation: `pip install pyopencv(or opencv-python)`
-   useage: `import cv2`

#### numpy

-   installation: `pip install numpy`
-   useage: `import numpy` or `import numpy as np`

## Description

### 1. 主要功能

#### ① 御魂(觉醒) 单开, 双开

#### ② 双人探索

#### ③ 单人/双人 突破

#### ④ 单人/双人 业原火

#### ⑤ 单人/双人 御灵

### 2. 文件构成

#### main.py

-   主要是全部的逻辑控制

#### yys_window.py

-   UI 部分, 通过 put msg -> queue, 然后 main get msg 来进行用户交互
-   可能会拆分, UI 写多了,越来越混乱

#### yys_tool.py

-   所有的控制, 检测都在里面

#### creater.py

-   主要用来创建并测试 tools 里面的功能
