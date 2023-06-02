import tkinter
import time
import win32api
from tkinter import messagebox
from threading import Thread
import pyautogui

# 颜色常量设置区域
COLOR_PRIMARY = "#409EFF"
COLOR_SUCCESS = "#67C23A"
COLOR_WARNING = "#E6A23C"
COLOR_ERROR = "#F56C6C"
COLOR_INFO = "#909399"

# yys 窗口界面


class yys_win(object):
    def __init__(self, sender, receiver, logger):
        self.logger = logger
        self.running = True

        '''
        暂时用数字表示开了几个阴阳师, 后面可能加上正常大小窗口和缩小的大小 mode
        '''
        self.SETTING = {"win_num": 0, "available": True, "wanted": False}

        self.window = tkinter.Tk()

        '''
        load window left-top icon, can't run with pyinstaller single file package
        '''
        # self.window.iconbitmap("./myIcon.ico")

        self.window.title("yys-3.0")
        self.window.geometry("300x180")
        self.window.resizable(0, 0)

        self.msgbox = tkinter.Label(
            self.window, text="连点器(单)双开版(记得管理员运行)", bg=COLOR_SUCCESS
        )
        self.msgbox.place(x=10, y=153)

        self.__init_menu()

        # init msg queue
        self.sender = sender
        self.receiver = receiver

        # init menu pages
        self.pane_home = pane_home(
            self.window, self.sender, self.config_msgbox)
        self.pane_yuhun1 = pane_yuhun1(
            self.window, self.sender, self.config_msgbox)
        self.pane_yuhun2 = pane_yuhun2(
            self.window, self.sender, self.config_msgbox)
        self.pane_yuhun4 = pane_yuhun4(
            self.window, self.sender, self.config_msgbox)
        self.pane_tansuo2 = pane_tansuo2(
            self.window, self.sender, self.config_msgbox)
        self.pane_stop = pane_stop(
            self.window, self.sender, self.config_msgbox)
        self.pane_tupo = pane_tupo(
            self.window, self.sender, self.config_msgbox)
        self.pane_tupo2 = pane_tupo2(
            self.window, self.sender, self.config_msgbox)
        self.pane_yulin = pane_yulin(
            self.window, self.sender, self.config_msgbox)
        self.pane_yulin2 = pane_yulin2(
            self.window, self.sender, self.config_msgbox)
        self.pane_yyh = pane_yyh(
            self.window, self.sender, self.config_msgbox)
        self.pane_yyh2 = pane_yyh2(
            self.window, self.sender, self.config_msgbox)
        self.pane_waiting = pane_waiting(
            self.window, self.sender, self.config_msgbox)

        # collect menu pages
        self.pages = (
            self.pane_home,
            self.pane_yuhun1,
            self.pane_yuhun2,
            self.pane_yuhun4,
            self.pane_tansuo2,
            self.pane_stop,
            self.pane_tupo,
            self.pane_tupo2,
            self.pane_yulin,
            self.pane_yulin2,
            self.pane_yyh,
            self.pane_yyh2,
            self.pane_waiting,
        )

        self.pane_home.place()
        # self.pane_yuhun4.place()

    def __t_receiver(self):
        while self.running:
            if not self.receiver.empty():
                msg = self.receiver.get()
                print("win get msg =>", msg)
                try:
                    mtype = msg["type"]
                except:
                    mtype = "unknow"

                if mtype == "msg":
                    self.config_msgbox(msg["msg"]["text"], msg["msg"]["bg"])
                elif mtype == 'error':
                    self.SETTING['available '] = False
                    self.config_msgbox(msg['msg'])

            time.sleep(0.1)

    def __start_receiver(self):
        t = Thread(target=self.__t_receiver)
        t.start()

    def config_msgbox(self, text: str, bg: str = "info") -> None:
        bgmap = {
            "success": COLOR_SUCCESS,
            "warning": COLOR_WARNING,
            "error": COLOR_ERROR,
            "info": COLOR_INFO,
            "primary": COLOR_PRIMARY,
        }
        try:
            bgcolor = bgmap[bg]
        except:
            bgcolor = COLOR_INFO
        self.msgbox.config(text=text, bg=bgcolor)

    def __init_menu(self):
        # main menu
        self.menu_bar = tkinter.Menu(self.window)
        # menu - home
        self.home_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.home_menu.add_command(label="主页", command=self.goto_home)
        self.home_menu.add_command(label="使用说明", command=self.guide)
        self.home_menu.add_command(
            label="初始化窗口", command=self.wins_small_topmost)
        self.home_menu.add_command(
            label="还原窗口", command=self.wins_normal_defloat)
        self.home_menu.add_separator()
        self.home_menu.add_command(label="退出", command=self.exit)
        # menu - functions
        self.func_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.func_menu.add_command(label="魂土", command=self.goto_yuhun)
        self.func_menu.add_command(label="探索", command=self.goto_tansuo)
        self.func_menu.add_command(label="突破", command=self.goto_tupo)
        self.func_menu.add_command(label="御灵", command=self.goto_yulin)
        self.func_menu.add_command(label="业原火", command=self.goto_yyh)
        # menu - other functions
        self.other_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.other_menu.add_command(label="抢车", command=self.feature_funcs)
        # menu - settings
        self.setting_menu = tkinter.Menu(self.menu_bar, tearoff=0)
        self.setting_menu.add_command(
            label="交换窗口", command=self.switch_wins_location)

        self.setting_menu.add_command(
            label="✘ 自动悬赏", command=self.switch_auto_wanted)

        self.setting_menu.add_command(label="识图频率", command=self.feature_funcs)

        # add child lists to menu
        self.menu_bar.add_cascade(menu=self.home_menu, label="主页")
        self.menu_bar.add_cascade(menu=self.func_menu, label="功能")
        self.menu_bar.add_cascade(menu=self.other_menu, label="其他")
        self.menu_bar.add_cascade(menu=self.setting_menu, label="设置")

        self.window.config(menu=self.menu_bar)

    def pop_msgbox(self, title, msg):
        messagebox.showwarning(title=title, message=msg)

    def guide(self):
        pyautogui.alert(
            title="使用说明",
            text="""
                1. win10
                2. 显示与缩放只能选择100%缩放
                3. 必须先初始化窗口,再选择相应的功能
                4. 请先阅读各功能的使用说明
                5. 有问题可以联系我
                6. 自动悬赏暂时不能用(设置了也无效)
                0. 造成损失, 我也负不了责...
            """, button="OK")

    def remove_place_all(self):
        for p in self.pages:
            p.remove_place()

    def goto_home(self):
        self.remove_place_all()
        self.pane_home.place()

    def goto_yuhun(self):
        self.remove_place_all()
        if self.SETTING['win_num'] == 2:
            self.pane_yuhun2.place()
            self.config_msgbox("请确认队长在上方窗口, 队员在下方窗口", bg="warning")
        elif self.SETTING['win_num'] == 1:
            self.pane_yuhun1.place()
            self.config_msgbox("进入单人御魂选项", bg="success")
        elif self.SETTING['win_num'] == 4:
            self.config_msgbox(text='on it', bg='warning')
        else:
            self.config_msgbox(text='御魂仅支持单双和四开', bg='error')

    def goto_tansuo(self):
        if self.SETTING['win_num'] != 2:
            self.config_msgbox(text='探索只支持双开', bg='error')
            return
        self.remove_place_all()
        self.pane_tansuo2.place()

    def goto_tupo(self):
        if self.SETTING['win_num'] == 1:
            self.remove_place_all()
            self.pane_tupo.place()
        elif self.SETTING['win_num'] == 2:
            self.remove_place_all()
            self.pane_tupo2.place()
        else:
            self.config_msgbox('yys窗口太多', bg='error')

    def goto_yulin(self):
        if self.setting['win_num'] == 1:
            self.remove_place_all()
            self.pane_yulin.place()
        elif self.SETTING['win_num'] == 2:
            self.remove_place_all()
            self.pane_yulin2.place()
        else:
            self.config_msgbox('yys窗口太多', bg='error')

    def goto_yyh(self):
        if self.SETTING['win_num'] == 1:
            self.remove_place_all()
            self.pane_yyh.place()
        elif self.SETTING['win_num'] == 2:
            self.remove_place_all()
            self.pane_yyh2.place()
        else:
            self.config_msgbox('yys窗口太多', bg='error')

    # 双开模式 - 交换上下两个窗口位置
    def switch_wins_location(self):
        self.sender.put({"type": "command", "params": "switch_wins_location"})
        self.config_msgbox("交换上下窗口若不成功, 请再次尝试", bg="warning")

    def chg_wins_orgsize(self):
        self.sender.put({"type": "command", "params": "chg_wins_orgsize"})
        self.config_msgbox("还原窗口大小成功", bg="success")

    def wins_small_topmost(self):
        self.sender.put({'type': 'command', 'params': 'wins_small_topmost'})
        self.config_msgbox("初始化窗口成功", bg="success")

    def wins_normal_defloat(self):
        self.sender.put({'type': 'command', 'params': 'wins_normal_defloat'})
        self.config_msgbox("还原窗口成功", bg="success")

    def switch_auto_wanted(self):
        self.SETTING['wanted'] = not self.SETTING['wanted']
        if self.SETTING['wanted']:
            self.setting_menu.entryconfig(1, label='✔ 自动悬赏')
            self.sender.put(
                {'type': 'command', 'params': 'switch_auto_wanted_on'})
            self.config_msgbox(text='自动接受悬赏 打开', bg='success')
        else:
            self.setting_menu.entryconfig(1, label='✘ 自动悬赏')
            self.sender.put(
                {'type': 'command', 'params': 'switch_auto_wanted_off'})
            self.config_msgbox(text='自动接受悬赏 关闭', bg='success')

    def feature_funcs(self):
        self.config_msgbox(text='功能开发中...', bg='warning')

    def exit(self):
        self.window.quit()
        self.running = False

    def run(self):
        self.__start_receiver()
        self.window.mainloop()
        self.running = False


class child_pane(object):
    def __init__(self, win, root_sender, msgbox) -> None:
        self.root = win
        self.sender = root_sender
        self.config_msgbox = msgbox
        self.pane = tkinter.PanedWindow(
            self.root, height=150, width=300, relief=tkinter.RIDGE, bg="#EEEEEE",
        )
        self.init_extensions()

    def init_extensions(self):
        pass

    def place(self):
        self.pane.place(x=0, y=0)

    def remove_place(self):
        self.pane.place_forget()

    def do_start(self):
        pyautogui.alert(title='提示', text='Sorry, 功能开发中...', button='确定')

# 子界面 => 主界面信息展示


class pane_home(child_pane):
    def init_extensions(self):
        self.title1 = tkinter.Label(
            self.pane, text="欢迎使用鸡哥连点器", font="Consola 14", foreground="#888888"
        )
        self.title2 = tkinter.Label(
            self.pane, text="e（￣︶￣）↗", font="Consola 14", foreground="#eea2a4"
        )
        self.button1 = tkinter.Button(
            self.pane, text="初始化窗口", command=self.wins_small_topmost
        )
        self.button2 = tkinter.Button(
            self.pane, text="还原　窗口", command=self.wins_normal_defloat
        )

    def place(self):
        super(pane_home, self).place()
        self.title1.place(x=58, y=5)
        self.title2.place(x=85, y=35)
        self.button1.place(x=10, y=110)
        self.button2.place(x=215, y=110)

    def wins_small_topmost(self):
        self.sender.put({"type": "command", "params": "wins_small_topmost"})
        self.config_msgbox("初始化窗口成功", bg="success")

    def wins_normal_defloat(self):
        self.sender.put({"type": "command", "params": "wins_normal_defloat"})
        self.config_msgbox("还原窗口成功", bg="success")


# 子界面 => 运行中的退出界面展示

class pane_stop(child_pane):
    def init_extensions(self):
        self.exit_btn = tkinter.Button(
            self.pane,
            text="退出(F9)",
            foreground=COLOR_ERROR,
            height=5,
            width=23,
            font="Consola 18",
            command=self.do_stop,
        )

    def place(self):
        super(pane_stop, self).place()
        self.exit_btn.place(x=5, y=5)

    def remove_place(self):
        self.pane.place_forget()

    def do_stop(self):
        self.sender.put({"type": "stop"})

# 御魂选项 菜单界面


class pane_yuhun1(child_pane):
    def init_extensions(self):
        self.label1 = tkinter.Label(self.pane, text="魂土(= V =)")
        self.cap_or_crew_value = tkinter.IntVar()
        self.radio1 = tkinter.Radiobutton(
            self.pane, variable=self.cap_or_crew_value, value=1, text="队长"
        )
        self.radio2 = tkinter.Radiobutton(
            self.pane, variable=self.cap_or_crew_value, value=2, text="队员"
        )
        self.crew1_or_crew2_value = tkinter.IntVar()
        self.radio3 = tkinter.Radiobutton(
            self.pane, variable=self.crew1_or_crew2_value, value=1, text="1队员"
        )
        self.radio4 = tkinter.Radiobutton(
            self.pane, variable=self.crew1_or_crew2_value, value=2, text="2队员"
        )
        self.start_btn = tkinter.Button(
            self.pane,
            text="开始",
            foreground=COLOR_SUCCESS,
            font="Consola 16",
            command=self.do_start,
            height=2,
            width=25,
        )

    def place(self):
        super(pane_yuhun1, self).place()
        self.label1.place(x=120, y=10)
        self.radio1.place(x=10, y=50)
        self.radio2.place(x=60, y=50)
        self.radio3.place(x=170, y=50)
        self.radio4.place(x=230, y=50)
        self.start_btn.place(x=7, y=85)

    def remove_place(self):
        self.pane.place_forget()

    def do_start(self):
        if_cap = self.cap_or_crew_value.get()
        if if_cap == 1:
            crew_num = self.crew1_or_crew2_value.get()
            if crew_num == 1:
                self.sender.put({"type": "start", "func": "yuhun1 cap1"})
            elif crew_num == 2:
                self.sender.put({"type": "start", "func": "yuhun1 cap2"})
            else:
                self.config_msgbox(text="队员人数错误", bg="error")
        elif if_cap == 2:
            self.sender.put({"type": "start", "func": "yuhun1 crew"})
        else:
            self.config_msgbox(text="请选择队员或队长", bg="warning")


class pane_yuhun2(child_pane):
    def init_extensions(self):
        self.label1 = tkinter.Label(self.pane, text="魂土(= V =)")
        self.start_btn = tkinter.Button(
            self.pane,
            text="开始",
            # relief=tkinter.RIDGE,
            foreground=COLOR_SUCCESS,
            height=4,
            width=25,
            font="Consola 16",
            command=self.do_start,
        )

    def place(self):
        super(pane_yuhun2, self).place()
        self.label1.place(x=120, y=10)
        self.start_btn.place(x=7, y=35)

    def remove_place(self):
        self.pane.place_forget()

    def do_start(self):
        self.sender.put({"type": "start", "func": "yuhun2"})


class pane_yuhun4(child_pane):
    def init_extensions(self):
        self.label1 = tkinter.Label(
            self.pane, text="Quadra Mitama", foreground=COLOR_PRIMARY)
        self.start_btn = tkinter.Button(
            self.pane,
            text="开始",
            foreground=COLOR_SUCCESS,
            height=3,
            width=25,
            font="Consola 16",
            command=self.do_start,
        )
        self.btn1 = tkinter.Button(self.pane, text="固定窗口1", command=lambda:self.pin_win(1))
        self.btn2 = tkinter.Button(self.pane, text="固定窗口2", command=lambda:self.pin_win(2))
        self.btn3 = tkinter.Button(self.pane, text="固定窗口3", command=lambda:self.pin_win(3))
        self.btn4 = tkinter.Button(self.pane, text="固定窗口4", command=lambda:self.pin_win(4))

    def place(self):
        super(pane_yuhun4, self).place()
        self.label1.place(x=100, y=10)
        self.start_btn.place(x=7, y=65)
        self.btn1.place(x=12, y=35)
        self.btn2.place(x=82, y=35)
        self.btn3.place(x=152, y=35)
        self.btn4.place(x=222, y=35)

    def remove_place(self):
        self.pane.place_forget()

    def pin_win(self, num:int):
        self.sender.put({"type":"command", "params":"pin window", "args": num})

    def do_start(self):
        self.sender.put({"type": "start", "func": "yuhun", "args":{"type":"quadra"}})


class pane_yulin(child_pane):
    def init_extensions(self):
        self.label1 = tkinter.Label(
            self.pane, text=":) 挂机御灵 (:", foreground=COLOR_PRIMARY)
        self.start_btn = tkinter.Button(self.pane, text="开始", foreground=COLOR_SUCCESS,
                                        height=3, width=25, font="Consola 16", command=self.do_start)
        self.guide_btn = tkinter.Button(
            self.pane, text='使用说明', foreground=COLOR_WARNING, command=self.show_guide)

    def show_guide(self):
        pyautogui.alert(title='御灵 使用说明', button='OK',
                        text="1. 几乎和以前一样\n2. 记得锁定阵容")

    def do_start(self):
        self.sender.put(
            {"type": "start", "func": "yulin", "args": {"dual": False}})

    def place(self):
        super(pane_yulin, self).place()
        self.label1.place(x=110, y=10)
        self.start_btn.place(x=7, y=68)
        self.guide_btn.place(x=233, y=35)


class pane_yulin2(child_pane):
    def init_extensions(self):
        self.label1 = tkinter.Label(
            self.pane, text=":) 挂机御灵 (:", foreground=COLOR_PRIMARY)
        self.start_btn = tkinter.Button(self.pane, text="开始", foreground=COLOR_SUCCESS,
                                        height=3, width=25, font="Consola 16", command=self.do_start)
        self.ifDualVar = tkinter.BooleanVar(False)
        self.check1 = tkinter.Checkbutton(
            self.pane, text='检测到两个窗口,是否同时进行', variable=self.ifDualVar)
        self.guide_btn = tkinter.Button(
            self.pane, text='使用说明', foreground=COLOR_WARNING, command=self.show_guide)

    def show_guide(self):
        pyautogui.alert(title='御灵 使用说明', button='OK',
                        text="1. 几乎和以前一样\n2. 记得锁定阵容")

    def do_start(self):
        self.sender.put({"type": "start", "func": "yulin",
                         "args": {"dual": self.ifDualVar.get()}})

    def place(self):
        super(pane_yulin2, self).place()
        self.label1.place(x=110, y=10)
        self.start_btn.place(x=7, y=68)
        self.guide_btn.place(x=233, y=35)
        self.check1.place(x=10, y=35)


class pane_yyh(child_pane):
    def init_extensions(self):
        self.label1 = tkinter.Label(
            self.pane, text="^-^ 挂机业原火 ^-^", foreground=COLOR_PRIMARY)
        self.start_btn = tkinter.Button(self.pane, text="开始", foreground=COLOR_SUCCESS,
                                        height=3, width=25, font="Consola 16", command=self.do_start)
        self.guide_btn = tkinter.Button(
            self.pane, text='使用说明', foreground=COLOR_WARNING, command=self.show_guide)

    def show_guide(self):
        pyautogui.alert(title='业原火 使用说明', button='OK',
                        text="1. 几乎和以前一样\n2. 记得锁定阵容")

    def do_start(self):
        self.sender.put(
            {"type": "start", "func": "yyh", "args": {"dual": False}})

    def place(self):
        super(pane_yyh, self).place()
        self.label1.place(x=90, y=10)
        self.start_btn.place(x=7, y=68)
        self.guide_btn.place(x=233, y=35)


class pane_yyh2(child_pane):
    def init_extensions(self):
        self.label1 = tkinter.Label(
            self.pane, text="^-^ 挂机业原火(dual) ^-^", foreground=COLOR_PRIMARY)
        self.start_btn = tkinter.Button(self.pane, text="开始", foreground=COLOR_SUCCESS,
                                        height=3, width=25, font="Consola 16", command=self.do_start)
        self.ifDualVar = tkinter.BooleanVar(False)
        self.check1 = tkinter.Checkbutton(
            self.pane, text="检测到两个窗口,是否同时运行", variable=self.ifDualVar)
        self.guide_btn = tkinter.Button(
            self.pane, text='使用说明', foreground=COLOR_WARNING, command=self.show_guide)

    def show_guide(self):
        pyautogui.alert(title='业原火 使用说明', button='OK',
                        text="1. 几乎和以前一样\n2. 记得锁定阵容")

    def do_start(self):
        self.sender.put(
            {"type": "start", "func": "yyh", "args": {"dual": self.ifDualVar.get()}})

    def place(self):
        super(pane_yyh2, self).place()
        self.label1.place(x=70, y=10)
        self.start_btn.place(x=7, y=68)
        self.guide_btn.place(x=233, y=35)
        self.check1.place(x=10, y=35)


class pane_tansuo2(child_pane):
    def init_extensions(self):
        self.label1 = tkinter.Label(
            self.pane, text="> 双开探索 <", foreground=COLOR_PRIMARY)
        self.start_btn = tkinter.Button(
            self.pane,
            text="开始",
            foreground=COLOR_SUCCESS,
            height=3,
            width=25,
            font="Consola 16",
            command=self.do_start,
        )
        self.guide_text = '''1. 队长必须在上方\n2. 队长不锁定阵容, 队员锁定阵容\n3. 暂时不能换狗粮, 不能捡探索完成的宝箱\n4. 狗粮满级会停止(仅支持天邪鬼黄, 红蛋), 并发声提醒(声音较小)\n5. 偶尔会卡邀请队友, 这个貌似是游戏问题'''
        self.guide_btn = tkinter.Button(
            self.pane, text='使用说明', foreground=COLOR_WARNING, command=self.show_guide)

    def show_guide(self):
        pyautogui.alert(title='使用说明', button='OK', text=self.guide_text)

    def place(self):
        super(pane_tansuo2, self).place()
        self.label1.place(x=110, y=10)
        self.start_btn.place(x=7, y=68)
        self.guide_btn.place(x=233, y=35)

    def remove_place(self):
        self.pane.place_forget()

    def do_start(self):
        self.sender.put({"type": "start", "func": "tansuo2"})


class pane_tupo(child_pane):
    def init_extensions(self):
        self.label1 = tkinter.Label(
            self.pane, text="(= 突破 =)", foreground=COLOR_PRIMARY)
        self.modeVar = tkinter.BooleanVar(False)
        self.check1 = tkinter.Checkbutton(
            self.pane, text='是否自动失败6次', variable=self.modeVar)
        self.guide_btn = tkinter.Button(
            self.pane, text='使用说明', foreground=COLOR_WARNING, command=self.show_guide)
        self.start_btn = tkinter.Button(
            self.pane,
            text="开始",
            foreground=COLOR_SUCCESS,
            height=3,
            width=25,
            font="Consola 16",
            command=self.do_start,
        )

    def place(self):
        super(pane_tupo, self).place()
        self.label1.place(x=120, y=10)
        self.start_btn.place(x=7, y=68)
        self.guide_btn.place(x=233, y=35)
        self.check1.place(x=10, y=37)

    def show_guide(self):
        pyautogui.alert(text="1. 不用锁定阵容(为后续增加换阵容做考虑);\n2. 目前会自动标记一下最右, 自行调整队伍",
                        button='OK', title='使用说明')

    def do_start(self):
        args = {"fail": self.modeVar.get(), "dual": False}
        self.sender.put(
            {"type": "start", "func": "tupo", "args": args})


class pane_tupo2(child_pane):
    def init_extensions(self):
        self.label1 = tkinter.Label(
            self.pane, text="(= 突破 =)", foreground=COLOR_PRIMARY)
        self.modeVar = tkinter.BooleanVar(False)
        self.ifDualVar = tkinter.BooleanVar(False)
        self.check1 = tkinter.Checkbutton(
            self.pane, text='是否自动失败6次', variable=self.modeVar)
        self.check2 = tkinter.Checkbutton(
            self.pane, text='检测到两个yys, 是否一起开始突破', variable=self.ifDualVar)
        self.guide_btn = tkinter.Button(
            self.pane, text='使用说明', foreground=COLOR_WARNING, command=self.show_guide)
        self.start_btn = tkinter.Button(
            self.pane,
            text="开始",
            foreground=COLOR_SUCCESS,
            height=2,
            width=25,
            font="Consola 16",
            command=self.do_start,
        )

    def place(self):
        super(pane_tupo2, self).place()
        self.label1.place(x=120, y=10)
        self.start_btn.place(x=7, y=88)
        self.guide_btn.place(x=233, y=35)
        self.check1.place(x=10, y=37)
        self.check2.place(x=10, y=57)

    def show_guide(self):
        pyautogui.alert(text="1. 不用锁定阵容(为后续增加换阵容做考虑);\n2. 目前会自动标记一下最右, 自行调整队伍",
                        button='OK', title='使用说明')

    def do_start(self):
        args = {"fail": self.modeVar.get(), "dual": self.ifDualVar.get()}
        self.sender.put(
            {"type": "start", "func": "tupo", "args": args})


class pane_waiting(child_pane):
    def init_extensions(self):
        self.label1 = tkinter.Label(
            self.pane, text="等待 更换狗粮 ...", foreground=COLOR_PRIMARY)
        self.continue_btn = tkinter.Button(self.pane, text="狗粮更换完毕, 请继续", foreground=COLOR_SUCCESS,
                                           height=4, width=25, font="Consola 16", command=self.do_continue)

    def place(self):
        super(pane_waiting, self).place()
        self.label1.place(x=120, y=10)
        self.continue_btn.place(x=7, y=48)

    def do_continue(self):
        self.sender.put({"type": "command", "params": "stop_waiting"})


if __name__ == "__main__":
    pass
    # zyp = yys_win()
    # zyp.run()
