import win32gui
import win32con
import win32api
import time
from mss import mss
from PIL import Image
# import cv2
# import numpy as np
from cv2 import cvtColor, COLOR_RGB2BGR, COLOR_BGR2GRAY, HoughCircles, HOUGH_GRADIENT, circle, waitKey, imshow
from numpy import array, any
import pyautogui
import winsound
from threading import Thread
# yys 工具类


class yys_tools(object):
    # 初始化函数
    def __init__(self, sender, logger):
        self.logger = logger
        self.game_name = u"阴阳师-网易游戏"
        self.org_size = (1152, 679)
        self.re_size = (834, 500)
        self.now_width = 834
        self.sender = sender

        self.win_num = 0
        self.SETTINGS = {"normal_size": False, "pin_num": 0,
                         "just_count": False, "defloat": True}

        self.displayer_width = win32api.GetSystemMetrics(0)
        self.displayer_height = win32api.GetSystemMetrics(1)

    # 仅仅返回打开的 阴阳师 窗口数, 不对窗口进行位置和大小变动
    # 同时将 游戏模式 计算入内

    def get_wins_num(self):
        self.num = 0
        self.SETTINGS["normal_size"] = False
        self.SETTINGS["just_count"] = True
        self.SETTINGS["defloat"] = False
        win32gui.EnumWindows(self.__map_windows, None)
        return self.win_num

    '''
    控制窗口的函数
    1. the window size small or default(normal)
    2. if pin the window to the top most
    3. all func can only run in small size (for now)
    '''

    def wins_small_topmost(self):
        self.win_num = 0
        self.SETTINGS["normal_size"] = False
        self.SETTINGS["just_count"] = False
        self.SETTINGS["defloat"] = False
        win32gui.EnumWindows(self.__map_windows, None)
        return self.win_num

    def wins_small_defloat(self):
        self.win_num = 0
        self.SETTINGS["normal_size"] = False
        self.SETTINGS["just_count"] = False
        self.SETTINGS["defloat"] = True
        win32gui.EnumWindows(self.__map_windows, None)
        return self.win_num

    def wins_normal_topmost(self):
        self.win_num = 0
        self.SETTINGS["normal_size"] = True
        self.SETTINGS["just_count"] = False
        self.SETTINGS["defloat"] = False
        win32gui.EnumWindows(self.__map_windows, None)
        return self.win_num

    def wins_normal_defloat(self):
        self.win_num = 0
        self.SETTINGS["normal_size"] = True
        self.SETTINGS["just_count"] = False
        self.SETTINGS["defloat"] = True
        win32gui.EnumWindows(self.__map_windows, None)
        return self.win_num

    def pin_window(self, num: int):
        self.logger.debug(f"tool received pin window command, num => {num}")
        self.SETTINGS["pin_num"] = num
        win32gui.EnumWindows(self.__pin_window, None)

    def __pin_window(self, win_handler, _):
        if self.SETTINGS['pin_num'] == 1:
            x1 = self.displayer_width-self.re_size[0]
            y1 = 0
            x2 = self.re_size[0]
            y2 = self.re_size[1]
        elif self.SETTINGS['pin_num'] == 2:
            x1 = self.displayer_width-self.re_size[0]
            y1 = self.re_size[1]
            x2 = self.re_size[0]
            y2 = self.re_size[1]
        elif self.SETTINGS['pin_num'] == 3:
            x1 = self.displayer_width-2*self.re_size[0]
            y1 = 0
            x2 = self.re_size[0]
            y2 = self.re_size[1]
        elif self.SETTINGS['pin_num'] == 4:
            x1 = self.displayer_width-2*self.re_size[0]
            y1 = self.re_size[1]
            x2 = self.re_size[0]
            y2 = self.re_size[1]
        if win32gui.GetWindowText(win_handler) == self.game_name:
            self.__float_win(win_handler, x1, y1, x2, y2, defloat=False)

    def __map_windows(self, win_handler, _):
        if_normal = self.SETTINGS["normal_size"]
        just_count = self.SETTINGS["just_count"]
        if_float = self.SETTINGS["defloat"]
        if win32gui.GetWindowText(win_handler) == self.game_name:
            self.win_num += 1
            if just_count:
                return

            if if_normal:
                w = self.org_size[0]
                h = self.org_size[1]
            else:
                w = self.re_size[0]
                h = self.re_size[1]

            if self.win_num == 1:
                self.__float_win(
                    win_handler,self.displayer_width - w,0,w,h,defloat=if_float
                )
            elif self.win_num == 2:
                self.__float_win(
                    win_handler,self.displayer_width - w,h,w,h,defloat=if_float
                )
            elif self.win_num == 3:
                self.__float_win(
                    win_handler,self.displayer_width - 2*w,0,w,h,defloat=if_float
                )
            elif self.win_num == 4:
                self.__float_win(
                    win_handler,self.displayer_width - 2*w,h,w,h,defloat=if_float
                )


    def __float_win(self, handler, x1, y1, x2, y2, defloat=False):
        if defloat:
            win32gui.SetWindowPos(
                handler, win32con.HWND_NOTOPMOST, x1, y1, x2, y2, 1)
        else:
            win32gui.SetWindowPos(
                handler, win32con.HWND_TOPMOST, x1, y1, x2, y2, 1)
        win32gui.MoveWindow(handler, x1, y1, x2, y2, True)

    def playsound(self):
        t = Thread(target=self.__t_playsound)
        t.start()

    def __t_playsound(self):
        winsound.PlaySound(
            "SystemQuestion", winsound.MB_ICONHAND | winsound.SND_LOOP)


    def quadra_click(self):
        posx = 100
        posy = 129
        abs1x = self.displayer_width - self.re_size[0] + posx
        abs1y = posy
        abs2x = abs1x
        abs2y = abs1y + self.re_size[1]
        abs3x = self.displayer_width - 2*self.re_size[0] + posx
        abs3y = posy
        abs4x = abs3x
        abs4y = abs2y
        self.click_pos(abs1x, abs1y)
        time.sleep(0.01)
        self.click_pos(abs2x, abs2y)
        time.sleep(0.01)
        self.click_pos(abs3x, abs3y)
        time.sleep(0.01)
        self.click_pos(abs4x, abs4y)

    # num: 1 => 只点击窗口 1
    # num: 2 => 只点击窗口 2
    # num: 0 => 点击窗口 1 和 2
    def normal_click(self, num: int = 1):
        # re_x = 111
        re_x = 100
        re_y = 129
        abs_x1 = self.displayer_width - (self.re_size[0] - re_x)
        abs_y1 = re_y
        if num == 2:
            abs_y1 += self.re_size[1]
        self.click_pos(abs_x1, abs_y1)
        if num == 0:
            abs_x2 = abs_x1
            abs_y2 = abs_y1 + 500
            self.click_pos(abs_x2, abs_y2)

    '''
    控制鼠标 点击(x ,y)
    '''

    def click_pos(self, x, y, which_win=1):
        px = int(x)
        py = int(y)
        if which_win == 2:
            py += self.re_size[1]
        win32api.SetCursorPos((px, py))
        win32api.mouse_event(
            win32con.MOUSEEVENTF_LEFTDOWN | win32con.MOUSEEVENTF_LEFTUP, px, py, 0, 0
        )

    def get_cursor_pos(self):
        cx, cy = win32api.GetCursorPos()
        return [self.now_width - (self.displayer_width - cx), cy]

    def get_zone_img(self, zone, if_top=True):
        x = self.displayer_width - self.now_width + zone[0]
        y = zone[1]
        w = zone[2]
        l = zone[3]
        if not if_top:
            y += y + 500
        monitor = (x, y, x + w, y + l)
        with mss() as sct:
            sct_img = sct.grab(monitor)
            return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    def img2hash(self, img):
        img = img.resize((16, 16), Image.ANTIALIAS).convert("L")
        avg = sum(list(img.getdata())) // 256
        hashStr = "".join(
            map(lambda i: "0" if i < avg else "1", img.getdata()))
        return hashStr

    def get_zone_hash(self, zone, if_top=True):
        img = self.get_zone_img(zone, if_top)
        hash = self.img2hash(img)
        return hash

    def compair_str(self, base_str, chk_str):
        if base_str and chk_str:
            count = 0
            for i in range(len(base_str)):
                if base_str[i] != chk_str[i]:
                    count += 1
            if count <= 12:
                return True
            else:
                return False
        return False

    def simple_compair(self, hstr, zone, if_top=True):
        img = self.get_zone_img(zone, if_top)
        chk_str = self.img2hash(img)
        return self.compair_str(hstr, chk_str)

    def count_circles(self, zone, min, max, show=False) -> int:
        img = self.get_zone_img(zone)
        cimg = cvtColor(array(img), COLOR_RGB2BGR)
        opencvSrc = cvtColor(cimg, COLOR_BGR2GRAY)
        count = 0
        org_cs = HoughCircles(
            opencvSrc,
            HOUGH_GRADIENT,
            1,
            40,
            param1=50,
            param2=25,
            minRadius=min,
            maxRadius=max,
        )

        if any(org_cs) == None:
            return [0, None]
        circles = org_cs[0, :]
        for c in circles:
            count += 1
            if show:
                circle(opencvSrc, (c[0], c[1]), int(c[2]), (255, 0, 0), 2)
        if show:
            print("circle count =>", count)
            imshow("show circles", opencvSrc)
            waitKey(0)
        return [count, circles]

    # 在组队界面 -> True
    def check_surface_zudui(self, which_win=1):
        zone = [67, 45, 80, 25]
        if which_win == 2:
            zone[1] += self.re_size[1]
        elif which_win == 3:
            zone[0] -= self.re_size[0]
        elif which_win == 4:
            zone[0] -= self.re_size[0]
            zone[1] += self.re_size[1]
        hstr = "0000000000000000000000000000000000000000000000000100011110001010010001101110111001110110111011100111011111101010111101101100111001111111110011100111111111101110011111111110111001111111011011100111111111111111011111011001111000000000000000000000000000000000"
        return self.simple_compair(hstr, zone)

    # 组队界面 队员数量 == 1 -> True
    def check_status_has_crew1(self):
        zone = (385, 160, 70, 70)
        if self.count_circles(zone, 20, 33)[0] == 0:
            return True
        return False

    # 组队界面 队员数量 == 2 -> True
    def check_status_has_crew2(self):
        zone = (360, 135, 400, 150)
        if self.count_circles(zone, 20, 33)[0] == 0:
            return True
        return False

    # 点击操作 点击组队界面的开始
    # 多数组队界面通用
    def click_yuhun_start(self, which_win=1):
        abs_x = self.displayer_width - (self.re_size[0] - 786)
        abs_y = 443
        if which_win == 2:
            abs_y += self.re_size[1]
        self.click_pos(abs_x, abs_y)

    def check_status_ready(self, which_win=1):
        zone = [720, 420, 70, 50]
        if which_win == 2:
            zone[1] += self.re_size[1]
        hstr = '1011111111111110100111111111110100001111111100110011000100000110000011010001100011100000000001111111111100001111011111111111100000011111111111111100011111111111111100011111111111111100011111111111000000001111110000000000001100000000000000000000000000000000'
        return self.simple_compair(hstr, zone)

    # 状态检测 战斗中 -> True
    def check_status_started(self, which_win=1):
        zone = [10, 420, 70, 70]
        if which_win == 2:
            zone[1] += self.re_size[1]
        if self.count_circles(zone, 20, 33)[0] == 1:
            return True
        return False
    # 状态检测 战斗是否结束
    # 两次检测, 更好的准确性保证

    def check_status_fightEnd(self, which_win=1) -> bool:
        zone = [10, 420, 70, 70]
        if which_win == 2:
            zone[1] += self.re_size[1]
        num1, _ = self.count_circles(zone, 20, 33)
        num2, _ = self.count_circles(zone, 20, 33)
        if num1 == 0 and num2 == 0:
            return True
        return False

    # 界面检测, 是否在探索界面里
    def check_surface_tansuo(self, which_win=1):
        zone = [441, 40, 20, 20]
        if which_win == 2:
            zone[1] += self.re_size[1]
        hstr = '0000111111110000000001111111100000000111111000000000011111100000000100000100100000000111111110010000011111111111000011111111111100000011101111110000000011111111000000001111111100000001111111110000011111111111000001111111111100000000000110000000000000000000'
        return self.simple_compair(hstr, zone)

    # 探索界面 drag move 到中间
    def drag_tansuo_center(self):
        psy = 100
        pyautogui.moveTo(self.displayer_width-self.re_size[0]+800, psy)
        pyautogui.dragTo(self.displayer_width -
                         self.re_size[0]+100, psy, 2, button="left")
        pyautogui.moveTo(self.displayer_width-self.re_size[0]+500, psy)
        pyautogui.dragTo(self.displayer_width -
                         self.re_size[0]+100, psy, 2, button="left")

    # 寻找探索妖怪头上的圆 优先攻击boss
    # 打完boss后 探索宝物的圆圈也会被检测到, 所以click后, 用normal click
    def click_tansuo_circles(self):
        zone = (0, 80, 800, 300)
        c_num, cs = self.count_circles(zone, 25, 33, False)
        if c_num == 0:
            return False
        for c in cs:
            if 124.5 <= c[1] <= 125.5:
                pyautogui.click(self.displayer_width -
                                self.re_size[0]+c[0], c[1]+80)
                return True
        pyautogui.click(self.displayer_width -
                        self.re_size[0]+cs[0][0], cs[0][1]+80)
        return True

    # 界面检测, 是否在战斗(未准备界面)
    # ! 注意, 仅实用双人(组队)模式
    def check_surface_fight(self):
        zone = (395, 40, 40, 40)
        hstr = '0000000000000000000000000000000000000010000000000000011011111000000011111111100000001111111110000001111111111000000011111111100000001111111110000001111111111000000011111111110000011111111111000000100111111100000000000000000000000000000000000000000000000000'
        return self.simple_compair(hstr, zone)

    def check_tansuo_level20(self):
        zone = (482, 790, 12, 12)
        # 天邪鬼黄
        hstr1 = '1000001100111000110000111111100011000111111100000000001111110000000000111111110000001111111111000000111111110000100001110011000000000111111111110001111101110111000111110111011110011111111111111001110011011111100111000000011110011000000001111101100000011111'
        # 红蛋
        hstr2 = '0000000001100011000000000110000100001111111100011000111111110001100011111110000100000111111110000000111111111000000111111110000000011110011000000001111111111100001111111111110000111110110011100111111111111110011110111111111001110001000111100011000000001100'
        return self.simple_compair(hstr1, zone) or self.simple_compair(hstr2, zone)

    def click_fight_start(self, which_win=1):
        x = 726
        y = 354
        self.click_pos(self.displayer_width-self.re_size[0]+x, y, which_win)

    def click_tansuo_exit(self, which_win=1):
        x1 = self.displayer_width - self.re_size[0] + 40
        y1 = 70
        self.click_pos(x1, y1, which_win)

    def click_tansuo_comfirmExit(self, which_win=1):
        x = 505
        y = 289
        self.click_pos(self.displayer_width-self.re_size[0]+x, y, which_win)

    # 界面检测, 确认退出探索吗?
    def check_surface_confirmExit(self, which_win=1):
        zone = [270, 220, 300, 100]
        if which_win == 2:
            zone[1] += self.re_size[1]
        hstr = '1111111111111111111111111111111111110000000111111111000000011111111111001111111111111111111111111111111111111111111111111111111100000011100000000100101110010100010011111010011001001111101000100111101110110110000000111000000010000011110000011111111111111111'
        return self.simple_compair(hstr, zone)

    # 界面检测, 是否邀请队友继续战斗
    def check_surface_continue(self):
        zone = (274, 211, 280, 130)
        hstr = '1111111111111111111111111111111111000000000000111100000000010111111111111111111111111111111111111111111111111111111111111111111111111111111111110000000110000000000000001011111000000001111001110000000111100111000000001011111000000001100000001111111111111111'
        return self.simple_compair(hstr, zone)

    def click_tansuo_continue(self):
        x = 493
        y = 306
        pyautogui.click(self.displayer_width-self.re_size[0]+x, y)

    def check_continue_crew(self, which_win):
        zone = [66, 166, 60, 60]
        if which_win == 2:
            zone[1] += self.re_size[1]
        return self.count_circles(zone, 22, 33, False)

    def check_surface_tupo(self, which_win=1):
        # update 2021-07-30
        hstr = '0001111111111000000111111111100000111111111111000011111111111100001111111111110000111111111110000001111111111000000011111111000000001111111000000000000111000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
        zone = [10, 355, 30, 30]
        if which_win == 2:
            zone[1] += self.re_size[1]
        return self.simple_compair(hstr, zone)

    def click_tupo_fight(self, order=1, which_win=1):
        order -= 1
        base_pos = (215, 150)
        fight_pos = (254, 277)
        dx = 214
        dy = 88
        row = order // 3
        col = order % 3
        one_x = base_pos[0] + col * dx
        one_y = base_pos[1] + row * dy
        two_x = fight_pos[0] + col * dx
        two_y = fight_pos[1] + row * dy
        if which_win == 2:
            one_y += self.re_size[1]
            two_y += self.re_size[1]
        self.click_pos(self.displayer_width-self.re_size[0]+one_x, one_y)
        time.sleep(0.7)
        self.click_pos(self.displayer_width-self.re_size[0]+two_x, two_y)

    def check_tupo_ready(self, which_win=1):
        zone = [10, 30, 45, 45]
        if which_win == 2:
            zone[1] += self.re_size[1]
        return self.count_circles(zone, 15, 25, False)

    def check_tupo_exit(self, which_win=1):
        zone = [300, 210, 240, 120]
        if which_win == 2:
            zone[1] += self.re_size[1]
        hstr = '1111111111111111111111111111111111100000000011111110000000001111111111111111111111111111111111111111111111111111111111111111111111111111111111110000001110000001000000011011110100000001111011110000000111100111000000011011110100000001100000011000001111000001'
        return self.simple_compair(hstr, zone)

    def check_tupo_reward_done(self, which_win=1):
        # update 2021-07-31
        hstr = '1001100000000100001100011110001000110011111000110011111111111110001111111111111100111000000011100000000000000000100000111110000101100000000000010000000011000001000000010100001000010011110000000000001101000000111000100100000111111011010011111111110111011111'
        zone = [385, 403, 30, 30]

        if which_win == 2:
            zone[1] += self.re_size[1]
        return self.simple_compair(hstr, zone)

    def click_tupo_exit(self, which_win=1):
        x = 480
        y = 300
        if which_win == 2:
            y += self.re_size[1]
        self.click_pos(self.displayer_width-self.re_size[0]+x, y)

    def check_surface_yulin(self, which_win=1):
        zone = [69, 44, 60, 30]
        if which_win == 2:
            zone[1] += self.re_size[1]
        hstr = '0000000000000000000000000000000000001100001110000000111000111000000111111011100000001111101100000001111110110000000111111011100000011111111100000000111100110000000011110011100000001011011011000000000001001100111111111111111100000000000000000000000000000000'
        return self.simple_compair(hstr, zone)

    def check_locked_yulin(self, which_win=1):
        zone = [360, 390, 24, 24]
        if which_win == 2:
            zone[1] += self.re_size[1]
        hstr = '0000000000000000000000011100000000000111111000000000011001110000000011100011100000011110011111000011111111111110011001111111011101101111111101110011111001111110000111100111100000001110011110000000011111110000000000111100000000000000100000000000000000000000'
        return self.simple_compair(hstr, zone)

    def click_yulin_start(self):
        x = 740
        y = 400
        self.click_pos(self.displayer_width-self.re_size[0]+x, y)

    def check_surface_yyh(self, which_win=1):
        zone = [120, 320, 50, 50]
        hstr = '1111111111111111111001111111111101110011111111110000000111111111100000000111111110000010001111111000000000011111000000000000111100000000000001111000000000000111000000000000011100000000111001111000001111100011100000011110001111000000111100011100000001111100'
        if which_win == 2:
            zone[1] += self.re_size[1]
        return self.simple_compair(hstr, zone)

    def check_locked_yyh(self, which_win=1):
        zone = [360, 390, 26, 26]
        hstr = '0000000000000000000000011100000000000011111000000000011000110000000011100011100000011111111111000011011111110110001101111111011100111111011111100001111001111000000011100111100000000111111100000000000111000000000000001000000000000000000000001000000000000000'
        if which_win == 2:
            zone[1] += self.re_size[1]
        return self.simple_compair(hstr, zone)

    def click_yyh_start(self, which_win=1):
        pos_x = 746
        pos_y = 406
        if which_win == 2:
            pos_y += self.re_size[1]
        self.click_pos(self.displayer_width-self.re_size[0]+pos_x, pos_y)

    def check_surface_wanted(self):
        pass

    def click_wanted_accept(self):
        pass

    def click_wanted_close(self):
        pass


if __name__ == "__main__":
    zyp = yys_tools(None)
