from yys_tools import yys_tools
from yys_window import yys_win
from threading import Thread
import keyboard
import time
from queue import Queue
from yys_log import LOG
import argparse

Args_Parser = argparse.ArgumentParser()
Args_Parser.add_argument(
    "-d", "--debug", default=False, help="run in debug mode", action="store_true"
)
ARGS = Args_Parser.parse_args()

# 双重点击？双开御魂？
"""
本来开始是打算写成双开版的,
后面干脆把双开单开混合在一起
在程序开始加入了窗口数目检测,自动判断单开还是双开
"""


class dualClicks(object):
    def __init__(self):
        self.logger = LOG(ARGS.debug)
        self.running = True
        self.clicking = False
        self.waiting = False
        self.SETTING = {
            "available ": True,
            "win_num": 0,
            "size": "normal",
            "wanted": False,
        }

        self.funcs_map = {
            "yuhun": {"name": "御魂"},
            "yuhun1 cap1": {"t": self.__t_yuhun1_cap1, "name": "单人御魂 队长 1队员"},
            "yuhun1 cap2": {"t": self.__t_yuhun1_cap2, "name": "单人御魂 队长 2队员"},
            "yuhun1 crew": {"t": self.__t_yuhun1_crew, "name": "单人御魂 队员"},
            "tansuo2": {"t": self.__t_tansuo_team, "name": "双开探索"},
            "tupo": {"t": self.__t_tupo, "name": "突破"},
            "yulin": {"t": self.__t_yulin, "name": "御灵"},
            "yyh": {"t": self.__t_yyh, "name": "业原火"},
        }

        self.logger.debug("main 初始化 变量 完成")

        self.win_re = Queue()
        self.win_se = Queue()

        self.window = yys_win(
            sender=self.win_re, receiver=self.win_se, logger=self.logger
        )
        self.tool = yys_tools(self.win_se, self.logger)

        self.logger.debug("main 初始化 模块 完成")

        self.__health_check()

    def __health_check(self):
        if self.tool.displayer_height < 1080:
            self.SETTING["available"] = False
            self.window.config_msgbox(text="屏幕分辨率高度小于1080", bg="error")
            self.window.available = False
            return
        win_nums = self.tool.get_wins_num()
        self.window.SETTING["win_num"] = win_nums

    def __t_receiver(self):
        while self.running:
            if not self.win_re.empty():
                msg = self.win_re.get()
                self.logger.debug(f"main get msg: {msg}")

                try:
                    mtype = msg["type"]
                except:
                    mtype = "unknow"

                if mtype == "command":
                    if msg["params"] == "wins_small_topmost":
                        num = self.tool.wins_small_topmost()
                        self.SETTING["win_num"] = num
                        self.window.SETTING["win_num"] = num
                    elif msg["params"] == "wins_normal_defloat":
                        num = self.tool.wins_normal_defloat()
                        self.SETTING["win_num"] = num
                        self.window.SETTING["win_num"] = num
                    elif msg["params"] == "switch_wins_location":
                        num = self.tool.wins_small_topmost()
                        self.SETTING["win_num"] = num
                        self.window.SETTING["win_num"] = num
                    elif msg["params"] == "stop_waiting":
                        self.waiting = False
                    elif msg["params"] == "pin window":
                        self.tool.pin_window(msg["args"])

                elif mtype == "start":
                    func = msg["func"]
                    params = None
                    if func not in self.funcs_map:
                        self.window.config_msgbox("不存在的功能", "error")
                        continue
                    if self.clicking:
                        self.window.config_msgbox("已经在运行中", "warning")
                        continue
                    if func == "yyh":
                        params = msg["args"]
                        if params["dual"]:
                            t = Thread(target=self.__t_yyh_dual, args=[None, ])
                        else:
                            t = Thread(target=self.__t_yyh, args=[None, ])
                        t.start()
                        continue
                    elif func == 'yuhun':
                        mitama = msg['args']['type']
                        if mitama == 'quadra':
                            t = Thread(target=self.__t_yuhun4)
                            t.start()
                        elif mitama == 'dual':
                            t = Thread(target=self.__t_yuhun2)
                            t.start()
                        continue

                    elif func == "yulin":
                        params = msg["args"]
                        if params["dual"]:
                            t = Thread(target=self.__t_yulin_dual)
                        else:
                            t = Thread(target=self.__t_yulin)
                        t.start()
                        continue
                    elif func == "tupo":
                        params = msg["args"]
                        if params["dual"]:
                            t = Thread(
                                target=self.__t_tupo_dual,
                                args=[{"fail": params["fail"], "win": 1}],
                            )
                            t.start()
                            self.window.config_msgbox(
                                text="开始 突破(dual) ...", bg="success"
                            )
                        else:
                            t = Thread(
                                target=self.funcs_map[func]["t"],
                                args=[{"fail": params["fail"], "win": 1}],
                            )
                            t.start()
                            self.window.config_msgbox(
                                text="开始 突破 ...", bg="success")
                        continue

                    t = Thread(target=self.funcs_map[func]["t"], args=[params])
                    t.start()
                    self.window.config_msgbox(
                        f'开始 {self.funcs_map[func]["name"]} ...')

                elif mtype == "stop":
                    self.clicking = False
                    self.window.config_msgbox("已停止, 返回主页")
                    self.window.goto_home()

                else:
                    self.logger.debug(f"main get unknow msg: {msg}")

            time.sleep(0.01)

    def __start_receiver(self):
        t = Thread(target=self.__t_receiver)
        t.start()

    def __start_watch_press(self):
        key_watcher = Thread(target=self.__watch_stop_press)
        key_watcher.start()

    def __watch_stop_press(self):
        while self.running:
            if keyboard.is_pressed("f9"):
                self.clicking = False
                self.window.config_msgbox("已停止, 返回主页")
                self.window.goto_home()
            elif keyboard.is_pressed("f8"):
                t = Thread(target=self.__t_tansuo_team, args=[None])
                t.start()
            time.sleep(0.1)

    """
    自动悬赏的部分
    """

    def __auto_wanted(self):
        t = Thread(target=self.__t_auto_wanted)
        t.start()

    def __t_auto_wanted(self):
        while self.clicking:
            """
            if self.tool.check_surface_wanted():
                if self.SETTING['wanted'] == True:
                    self.tool.click_wanted_accept()
                else:
                    self.tool.click_wanted_close()
            """
            time.sleep(0.7)

    """
    御魂的部分
    """

    def __t_yuhun4(self):
        if not self.tool.check_surface_zudui(1):
            self.window.config_msgbox(text="队长1不在组队界面", bg="warning")
            return
        if not self.tool.check_surface_zudui(3):
            self.window.config_msgbox(text="队员1不在组队界面", bg="warning")
            return
        if not self.tool.check_surface_zudui(2):
            self.window.config_msgbox(text="队长2不在组队界面", bg="warning")
            return
        if not self.tool.check_surface_zudui(4):
            self.window.config_msgbox(text="队员2不在组队界面", bg="warning")
            return

        self.window.remove_place_all()
        self.window.pane_stop.place()
        self.window.config_msgbox(text="开始四开御魂(小心肝爆)...", bg="success")

        progress = 1
        count = 1
        self.clicking = True
        '''
        +------------+------------+
        |            |            |
        |     3      |      1     |
        |            |            |
        +------------+------------+
        |            |            |
        |     4      |      2     |
        |            |            |
        +------------+------------+
        '''

        while self.clicking:
            if progress == 1:
                if self.tool.check_surface_zudui(1) and self.tool.check_surface_zudui(3):
                    self.logger.debug("main yuhun4 p1 in if")
                    self.tool.click_yuhun_start(1)
                    progress = 2
            elif progress == 2:
                if self.tool.check_surface_zudui(2) and self.tool.check_surface_zudui(4):
                    self.logger.debug("main yuhun4 p2 in if")
                    self.tool.click_yuhun_start(2)
                    progress = 3
            elif progress == 3:
                if self.tool.check_status_started(1) and self.tool.check_status_started(2):
                    self.logger.debug("main yuhun4 p3 in if")
                    time.sleep(5)
                    progress = 4
            elif progress == 4:
                if self.tool.check_status_fightEnd(1) and self.tool.check_status_fightEnd(2):
                    self.logger.debug("main yuhun4 p4 in if")
                    progress = 5
            elif progress == 5:
                if self.tool.check_surface_zudui(1) and self.tool.check_surface_zudui(2) and self.tool.check_surface_zudui(3) and self.tool.check_surface_zudui(4):
                    self.logger.debug("main yuhun4 p5 in if")
                    progress = 1
                    self.window.config_msgbox(
                        text=f'完成 <御魂quadra> {count} 次', bg='success')
                    count += 1
                else:
                    self.logger.debug("main yuhun4 p5 in else(quadra click)")
                    self.tool.quadra_click()

            time.sleep(0.8)

    def __t_yuhun2(self):
        progress = 1
        count = 1
        if not self.tool.check_surface_zudui():
            self.window.config_msgbox("不在组队界面", bg="warning")
            return

        self.window.remove_place_all()
        self.window.pane_stop.place()

        self.clicking = True
        self.window.config_msgbox("开始组队御魂...", bg="success")

        while self.clicking:
            if progress == 1:
                if self.tool.check_surface_zudui():
                    progress = 2
            elif progress == 2:
                if self.tool.check_status_has_crew1():
                    self.tool.click_yuhun_start()
                    progress = 3
            elif progress == 3:
                if self.tool.check_status_started():
                    self.window.config_msgbox(f"已完成 {count} 次", bg="success")
                    count += 1
                    progress = 4
                else:
                    time.sleep(0.7)
                    continue
            elif progress == 4:
                if self.tool.check_status_fightEnd():
                    progress = 1
                else:
                    time.sleep(0.7)
                    continue

            self.tool.normal_click(0)
            time.sleep(0.7)

    def __t_yuhun1_cap1(self, _):
        progress = 1
        count = 1

        if not self.tool.check_surface_zudui():
            self.window.config_msgbox(text="不在组队界面", bg="warning")
            return
        self.window.remove_place_all()
        self.window.pane_stop.place()

        self.clicking = True
        self.window.config_msgbox(text="开始组队御魂(队长 1队员)...", bg="success")

        while self.clicking:
            if progress == 1:
                if self.tool.check_surface_zudui():
                    progress = 2
            elif progress == 2:
                if self.tool.check_status_has_crew1():
                    self.tool.click_yuhun_start()
                    progress = 3

            elif progress == 3:
                if self.tool.check_status_started():
                    self.window.config_msgbox(f"已完成 {count} 次", bg="success")
                    count += 1
                    progress = 4
                else:
                    time.sleep(0.7)
                    continue
            elif progress == 4:
                if self.tool.check_status_fightEnd():
                    progress = 1
                else:
                    time.sleep(0.7)
                    continue

            self.tool.normal_click(1)
            time.sleep(0.7)

    def __t_yuhun1_cap2(self, _):
        progress = 1
        count = 1

        if not self.tool.check_surface_zudui():
            self.window.config_msgbox(text="不在组队界面", bg="warning")
            return
        self.window.remove_place_all()
        self.window.pane_stop.place()

        self.clicking = True
        self.window.config_msgbox(text="开始组队御魂(队长 2队员)...", bg="success")

        while self.clicking:
            if progress == 1:
                if self.tool.check_surface_zudui():
                    progress = 2
            elif progress == 2:
                if self.tool.check_status_has_crew2():
                    self.tool.click_yuhun_start()
                    progress = 3
            elif progress == 3:
                if self.tool.check_status_started():
                    self.window.config_msgbox(f"已完成 {count} 次", bg="success")
                    count += 1
                    progress = 4
                else:
                    time.sleep(0.7)
                    continue
            elif progress == 4:
                if self.tool.check_status_fightEnd():
                    progress = 1
                else:
                    time.sleep(0.7)
                    continue

            self.tool.normal_click(1)
            time.sleep(0.7)

    def __t_yuhun1_crew(self, _):
        count = 1

        self.window.remove_place_all()
        self.window.pane_stop.place()
        self.clicking = True
        self.window.config_msgbox(text="开始御魂 队员 ...", bg="success")

        while self.clicking:
            if self.tool.check_status_started():
                time.sleep(0.7)
                continue
            elif self.tool.check_surface_zudui():
                self.window.config_msgbox(f"已完成 {count} 次", bg="success")
                count += 1
                time.sleep(0.7)
                continue

            self.tool.normal_click(1)
            time.sleep(0.7)

    # 双开探索
    def __t_tansuo_team(self, _):
        count = 1
        progress = 1

        if not self.tool.check_surface_zudui():
            self.window.config_msgbox(text="不在组队界面", bg="warning")
            return

        self.window.config_msgbox(text="开始组队探索", bg="success")
        self.window.remove_place_all()
        self.window.pane_stop.place()

        self.clicking = True

        while self.clicking:
            # 进度1: 组队界面
            if progress == 1:
                # 如果在组队界面 -> 进入进度2
                if self.tool.check_surface_zudui():
                    progress = 2

            # 进度2: 组队界面, 验证队员
            elif progress == 2:
                # 如果队员已加入, 点击开始, 进入进度3
                if self.tool.check_status_has_crew2():
                    self.tool.click_yuhun_start()
                    progress = 3

            # 进度3: 探索界面
            elif progress == 3:
                # 如果在探索界面, 将界面移动到中间, 进入进度4
                if self.tool.check_surface_tansuo():
                    self.tool.drag_tansuo_center()
                    time.sleep(0.5)
                    progress = 4

            # 进度4: 开始探测 带圆的探索怪物
            elif progress == 4:
                # 如果有圆被检测到, 点击圆
                if self.tool.click_tansuo_circles():
                    time.sleep(1)
                    self.tool.normal_click(1)

                    # 点击圆后检测是否还在探索界面
                    # 如果还在探索界面, 继续点击圆, 直到没有
                    if self.tool.check_surface_tansuo():
                        continue
                    # 没有检测到探索界面, 则进入探索战斗界面
                    else:
                        progress = 5

                else:
                    # 没有圆圈了,  直接到进度 8
                    progress = 8

            # 进度5: 进入了战斗界面
            elif progress == 5:
                # 检测确认是否在战斗界面
                if self.tool.check_surface_fight():
                    # 添加了延时, 更有效能检测到满级
                    time.sleep(0.7)
                    # 检测是否满级
                    if self.tool.check_tansuo_level20():
                        self.tool.playsound()
                        self.window.config_msgbox(
                            text="狗粮满级, 请更换", bg="warning")
                        # 为了更换狗粮设置的变量
                        self.waiting = True
                        self.window.remove_place_all()
                        self.window.pane_waiting.place()
                        # 开始等待换狗粮
                        count_down = 30
                        while self.waiting and count_down > 0:
                            count_down -= 1
                            time.sleep(1)
                        self.waiting = False
                        self.window.remove_place_all()
                        self.window.pane_stop.place()
                        self.window.config_msgbox(text="探索中...", bg="success")
                    # 在战斗界面, 则点击开始 -> 进入下一进度
                    while self.tool.check_surface_fight():
                        self.tool.click_fight_start()
                    progress = 6

            # 进度6: 战斗中...
            elif progress == 6:
                # 检测 战斗是否开始
                if self.tool.check_status_started():
                    # 战斗中, 直到战斗没被检测到
                    while self.tool.check_status_started():
                        time.sleep(1)
                    # 则进入 进度7
                    progress = 7
                # 尝试再次点击 开始战斗

            # 进度7: 回到探索界面
            elif progress == 7:
                # 如果回到了探索界面, 则返回进度4, 继续
                if self.tool.check_surface_tansuo():
                    progress = 4
                self.tool.normal_click(0)

            # 没有圆圈了, 表示没有怪了, 开始队长的退出探索
            elif progress == 8:
                time.sleep(1)
                # 直到退出到组队界面
                while self.clicking:
                    if self.tool.check_surface_tansuo():
                        self.tool.click_tansuo_exit()
                    if self.tool.check_surface_confirmExit():
                        self.tool.click_tansuo_comfirmExit()
                    if not self.tool.check_surface_tansuo():
                        progress = 9
                        break
                    time.sleep(0.7)
                self.logger.debug("main 探索 队长 退出组队界面 完成")

            # 队长退出探索, 出现是否继续的框 -> 点击继续 -> 回到组队界面 -> next
            elif progress == 9:
                self.logger.debug("main 探索 队长退出探索 进入p9: 检测邀请;组队界面")
                if self.tool.check_surface_continue():
                    self.tool.click_tansuo_continue()
                time.sleep(1)
                if self.tool.check_surface_zudui():
                    self.logger.debug("main 探索 队长 检测到 组队界面")
                    self.window.config_msgbox(
                        text=f"已完成 探索 {count}次", bg="success")
                    count += 1
                    progress = 10

            # 队员退出探索
            # 如果在探索 -> 点击退出 -> 点击确认退出 -> 被邀请弹窗 -> 点击继续 -> 回到组队界面 -> next
            # 如果是打完boss可能直接自动退出探索 -> 被邀请弹窗 -> 点击继续 -> 回到组队界面 -> next
            elif progress == 10:
                time.sleep(1)
                self.logger.debug("main 探索 队员 开始 退出")
                while self.clicking:
                    if self.tool.check_surface_tansuo(2):
                        self.tool.click_tansuo_exit(2)
                    if self.tool.check_surface_confirmExit(2):
                        self.tool.click_tansuo_comfirmExit(2)
                    num_cs, cs = self.tool.check_continue_crew(2)
                    if num_cs > 0:
                        click_x = (
                            self.tool.displayer_width
                            - self.tool.re_size[0]
                            + cs[0][0]
                            + 66
                        )
                        click_y = cs[0][1] + 166
                        self.tool.click_pos(click_x, click_y, which_win=2)
                    if self.tool.check_surface_zudui(2):
                        progress = 1
                        break
                    time.sleep(0.7)

            time.sleep(0.7)

    def __t_tupo(self, args):
        if not self.tool.check_surface_tupo():
            self.window.config_msgbox(text="不在突破界面", bg="warning")
            return
        if args["win"] == 2:
            if not self.tool.check_surface_tupo(2):
                self.window.config_msgbox(text="窗口2不在突破界面", bg="warning")
                return

        progress = 1
        try:
            order = args["order"]
        except:
            order = 1
        count = 1
        if not args["fail"]:
            progress = 4

        self.window.remove_place_all()
        self.window.pane_stop.place()
        self.clicking = True
        while self.clicking:
            if progress == 1:
                if self.tool.check_surface_tupo(args["win"]):
                    progress = 2
            # 进度2 -> 点击 1-9 点击 战斗(1-9) -> 离开突破界面
            elif progress == 2:
                self.tool.click_tupo_fight(order, args["win"])
                time.sleep(0.7)
                self.tool.normal_click(args["win"])
                if not self.tool.check_surface_tupo(args["win"]):
                    progress = 3
            # 进度3 -> 突破界面全部加载 -> 点击退出 -> 确认退出 ->
            # 如果没有退够5个 -> 进度1(order+1);
            # 如果退够了5个 -> 进度4
            elif progress == 3:
                num, cs = self.tool.check_tupo_ready(args["win"])
                if num == 1:
                    cx = cs[0][0]
                    cy = cs[0][1]
                    px = cx + 10
                    py = cy + 30
                    if args["win"] == 2:
                        py += 500
                    time.sleep(0.5)
                    self.tool.click_pos(
                        self.tool.displayer_width -
                        self.tool.re_size[0] + px, py
                    )
                if self.tool.check_tupo_exit(args["win"]):
                    self.tool.click_tupo_exit(args["win"])
                if self.tool.check_surface_tupo(args["win"]):
                    if args["fail"] and order < 6:
                        order += 1
                        progress = 1
                    else:
                        order = 1
                        progress = 4

                self.tool.normal_click(args["win"])

            elif progress == 4:
                if self.tool.check_surface_tupo(args["win"]):
                    progress = 5
            elif progress == 5:
                self.tool.click_tupo_fight(order, args["win"])
                time.sleep(0.7)
                self.tool.normal_click(args["win"])
                if not self.tool.check_surface_tupo(args["win"]):
                    progress = 6
            elif progress == 6:
                if self.tool.check_status_ready(args["win"]):
                    time.sleep(0.5)
                    self.tool.click_fight_start(args["win"])
                    while self.clicking:
                        if self.tool.check_status_ready(args["win"]):
                            time.sleep(1)
                            self.tool.click_fight_start(args["win"])
                        else:
                            break
                    progress = 7

            elif progress == 7:
                if args["win"] == 2:
                    time.sleep(1.5)
                else:
                    time.sleep(1)
                while self.clicking:
                    if self.tool.check_status_started(args["win"]):
                        time.sleep(1)
                    else:
                        break
                progress = 8
            elif progress == 8:
                self.logger.debug(f"main tupo<{args['win']} p{progress}>")
                if self.tool.check_surface_tupo(args["win"]):
                    if order >= 9:
                        progress = 9
                    else:
                        order += 1
                        progress = 4
                else:
                    self.tool.normal_click(args["win"])
            elif progress == 9:
                self.logger.debug(f"main tupo<{args['win']} p{progress}>")
                while self.clicking:
                    if self.tool.check_tupo_reward_done(args["win"]):
                        progress = 10
                        break
                    else:
                        self.tool.normal_click(args["win"])
                    time.sleep(0.7)

            elif progress == 10:
                self.logger.debug(f"main tupo<{args['win']} p{progress}>")
                self.window.config_msgbox(text=f"完成 突破 {count} 轮")
                if count == 3:
                    self.clicking = False
                    self.window.config_msgbox(
                        text=f"已完成 3*9 次突破", bg="success")
                    self.tool.playsound()

                else:
                    if args["fail"]:
                        progress = 1
                    else:
                        progress = 4
                    order = 1
                    count += 1

            time.sleep(0.7)

        self.clicking = False

    def __t_yulin(self):
        if not self.tool.check_surface_yulin():
            self.window.config_msgbox(text="不在御林界面", bg="warning")
            return
        if not self.tool.check_locked_yulin():
            self.window.config_msgbox(text="阵容未锁定", bg="warning")
            return

        count = 1
        progress = 1
        self.window.remove_place_all()
        self.window.pane_stop.place()
        self.clicking = True
        self.window.config_msgbox(text="开始自动 <御灵>", bg="success")

        while self.clicking:
            if progress == 1:
                if self.tool.check_surface_yulin():
                    self.tool.click_yulin_start()
                    progress = 2

            elif progress == 2:
                if self.tool.check_status_started():
                    time.sleep(5)
                    progress = 3

            elif progress == 3:
                if self.tool.check_status_fightEnd():
                    progress = 4
                else:
                    time.sleep(1)
                    continue

            elif progress == 4:
                if self.tool.check_surface_yulin():
                    progress = 1
                    self.window.config_msgbox(
                        text=f"已完成 <御灵> {count}次", bg="success")
                    count += 1
                else:
                    self.tool.normal_click()
                    time.sleep(0.5)
                    continue

            time.sleep(0.7)

    def __t_yulin_dual(self):
        if not self.tool.check_surface_yulin(1):
            self.window.config_msgbox(text="窗口1不在御灵界面", bg="warning")
            return
        if not self.tool.check_surface_yulin(2):
            self.window.config_msgbox(text="窗口2不在御灵界面", bg="warning")
            return

        if not self.tool.check_locked_yulin(1):
            self.window.config_msgbox(text="窗口1 阵容未锁定", bg="warning")
            return
        if not self.tool.check_locked_yulin(2):
            self.window.config_msgbox(text="窗口2 阵容未锁定", bg="warning")
            return

        progress = 1
        count = 1

        while self.clicking:
            if progress == 1:
                if self.tool.check_surface_yulin(1) and self.tool.check_surface_yulin(
                    2
                ):
                    progress = 2
            elif progress == 2:
                self.tool.click_yulin_start(1)
                time.sleep(0.5)
                if not self.tool.check_surface_yulin(1):
                    progress = 3
            elif progress == 3:
                self.tool.click_yulin_start(2)
                time.sleep(0.5)
                if not self.tool.check_surface_yulin(2):
                    progress = 4
            elif progress == 4:
                if self.tool.check_status_started(1) and self.tool.check_status_started(
                    2
                ):
                    progress = 5
                    time.sleep(5)
            elif progress == 5:
                if self.tool.check_status_fightEnd(
                    1
                ) and self.tool.check_status_fightEnd(2):
                    progress = 6
            elif progress == 6:
                if self.tool.check_surface_yulin(1) and self.tool.check_surface_yulin(
                    2
                ):
                    self.window.config_msgbox(
                        f"完成<御灵dual> {count} 次", bg="success")
                    count += 1
                    progress = 2
                else:
                    self.tool.normal_click(0)
                    time.sleep(0.5)
                    continue
            time.sleep(0.8)

    def __t_tupo_dual(self, args):
        if not self.tool.check_surface_tupo(1):
            self.window.config_msgbox(text="窗口1不在突破界面", bg="warning")
            return
        if not self.tool.check_surface_tupo(2):
            self.window.config_msgbox(text="窗口2不在突破界面", bg="warning")
            return

        progress = 1
        count = 1
        order = 1
        rand = 1
        self.clicking = True

        if not args["fail"]:
            progress = 5

        self.window.config_msgbox(text="开始突破<dual>...", bg="success")
        self.window.remove_place_all()
        self.window.pane_stop.place()

        while self.clicking:
            # 开始 => 检测开始界面 -> p2
            if progress == 1:
                if self.tool.check_surface_tupo(1) and self.tool.check_surface_tupo(2):
                    progress = 2
            #
            elif progress == 2:
                while self.clicking:
                    self.tool.click_tupo_fight(order, 1)
                    time.sleep(0.5)
                    if not self.tool.check_surface_tupo(1):
                        break
                while self.clicking:
                    self.tool.click_tupo_fight(order, 2)
                    time.sleep(0.5)
                    if not self.tool.check_surface_tupo(2):
                        break
                progress = 3
            elif progress == 3:
                num1, cs1 = self.tool.check_tupo_ready(1)
                num2, cs2 = self.tool.check_tupo_ready(2)
                if num1 == 1 and num2 == 1:
                    cx = cs1[0][0] + 10
                    cy = cs1[0][1] + 30
                    self.tool.click_pos(
                        self.tool.displayer_width -
                        self.tool.re_size[0] + cx, cy
                    )
                    self.tool.click_pos(
                        self.tool.displayer_width - self.tool.re_size[0] + cx,
                        cy + self.tool.re_size[1],
                    )
                    progress = 4
                else:
                    time.sleep(0.8)
                    continue

            elif progress == 4:
                if self.tool.check_tupo_exit(1) and self.tool.check_tupo_exit(2):
                    self.tool.click_tupo_exit(1)
                    self.tool.click_tupo_exit(2)
                else:
                    time.sleep(0.5)
                    continue
                while self.clicking:
                    if self.tool.check_surface_tupo(1) and self.tool.check_surface_tupo(
                        2
                    ):
                        if order >= 6:
                            progress = 5
                            order = 1
                        else:
                            progress = 1
                            order += 1
                        break
                    else:
                        self.tool.normal_click(0)
                    time.sleep(0.8)

            elif progress == 5:
                if self.tool.check_surface_tupo(1) and self.tool.check_surface_tupo(2):
                    while self.clicking:
                        self.tool.click_tupo_fight(order, 1)
                        time.sleep(0.5)
                        if not self.tool.check_surface_tupo(1):
                            break
                    while self.clicking:
                        self.tool.click_tupo_fight(order, 2)
                        time.sleep(0.5)
                        if not self.tool.check_surface_tupo(2):
                            break
                    progress = 6
                else:
                    time.sleep(0.5)
                    continue
            elif progress == 6:
                if self.tool.check_status_ready(1) and self.tool.check_status_ready(2):
                    self.tool.click_fight_start(1)
                    self.tool.click_fight_start(2)
                    progress = 7
                else:
                    time.sleep(0.5)
                    continue
            elif progress == 7:
                if self.tool.check_status_started(1) and self.tool.check_status_started(
                    2
                ):
                    time.sleep(2)
                    self.tool.click_fight_start(1)
                    self.tool.click_fight_start(2)
                    progress = 8
                else:
                    time.sleep(1)
                    continue
            elif progress == 8:
                self.logger.debug("main tupo p8")
                if self.tool.check_status_started(1) and self.tool.check_status_started(
                    2
                ):
                    time.sleep(1)
                    continue
                else:
                    progress = 9
            elif progress == 9:
                self.logger.debug("main tupo p9")
                if self.tool.check_surface_tupo(1) and self.tool.check_surface_tupo(2):
                    self.logger.debug("main tupo p9 in if: 两个窗口都完成")
                    # 如果 order >= 9 表示完成了 一轮
                    if order >= 9:
                        order = 1
                        self.window.config_msgbox(
                            text=f"已完成{rand}轮突破", bg="success")
                        if rand >= 3:
                            self.clicking = False
                            self.tool.playsound()
                        else:
                            rand += 1
                            # 需要点击normal, 9胜有个红达摩奖励
                            progress = 10
                    # 否则 没有完成 一轮
                    else:
                        if order % 3 == 0:
                            progress = 10
                        else:
                            progress = 5
                        order += 1

                else:
                    self.tool.normal_click(0)
                    time.sleep(0.5)
                    continue
            # 目前的问题就是6次失败后, 打完第一个,从第二个开始就又开始去退出来失败了
            elif progress == 10:
                if self.tool.check_tupo_reward_done(
                    1
                ) and self.tool.check_tupo_reward_done(2):
                    progress = 5
                    if args["fail"] and order == 1:
                        progress = 1
                else:
                    self.tool.normal_click(0)
                    time.sleep(0.5)
                    continue

            time.sleep(0.8)

    def __t_yyh(self, args):
        if not self.tool.check_surface_yyh():
            self.window.config_msgbox(text="不在业原火界面", bg="warning")
            return
        if not self.tool.check_locked_yyh():
            self.window.config_msgbox(text="阵容未锁定", bg="warning")
            return

        count = 1
        progress = 1
        self.clicking = True

        self.window.remove_place_all()
        self.window.pane_stop.place()
        self.window.config_msgbox(text="开始挂机<业原火>...", bg="success")

        while self.clicking:
            if progress == 1:
                if self.tool.check_surface_yyh():
                    progress = 2
            elif progress == 2:
                self.tool.click_yyh_start()
                time.sleep(0.5)
                if not self.tool.check_surface_yyh():
                    progress = 3
            elif progress == 3:
                if self.tool.check_status_started():
                    time.sleep(2)
                    progress = 4
            elif progress == 4:
                if self.tool.check_status_fightEnd():
                    progress = 5
            elif progress == 5:
                if self.tool.check_surface_yyh():
                    self.window.config_msgbox(
                        text=f"已完成<业原火> {count}次", bg="success")
                    count += 1
                    progress = 1
                else:
                    self.tool.normal_click(1)

            time.sleep(0.7)

    def __t_yyh_dual(self, args):
        if not self.tool.check_surface_yyh(1):
            self.window.config_msgbox(text="窗口1 不在业原火界面", bg="warning")
            return
        if not self.tool.check_surface_yyh(2):
            self.window.config_msgbox(text="窗口2 不在业原火界面", bg="warning")
            return
        if not self.tool.check_locked_yyh(1):
            self.window.config_msgbox(text="窗口1 阵容未锁定", bg="warning")
            return
        if not self.tool.check_locked_yyh(2):
            self.window.config_msgbox(text="窗口2 阵容未锁定", bg="warning")
            return

        count = 1
        progress = 1
        self.window.config_msgbox(text="开始挂机 <业原火dual> ...", bg="success")
        while self.clicking:
            if progress == 1:
                if self.tool.check_surface_yyh(1) and self.tool.check_surface_yyh(2):
                    progress = 2
            elif progress == 2:
                self.tool.click_yyh_start(1)
                time.sleep(0.1)
                self.tool.click_yyh_start(2)
                time.sleep(0.7)
                if not self.tool.check_surface_yyh(
                    1
                ) and not self.tool.check_surface_yyh(2):
                    progress = 3
            elif progress == 3:
                if self.tool.check_status_started(1) and self.tool.check_status_started(
                    2
                ):
                    progress = 4
            elif progress == 4:
                if self.tool.check_status_fightEnd(
                    1
                ) and self.tool.check_status_fightEnd(2):
                    progress = 5
            elif progress == 5:
                if self.tool.check_surface_yyh(1) and self.tool.check_surface_yyh(2):
                    progress = 1
                    self.window.config_msgbox(
                        text=f"完成 <业原火dual> {count} 次", bg="success"
                    )
                    count += 1
                else:
                    self.tool.normal_click(0)
            time.sleep(0.7)

    def run(self):
        self.__start_receiver()
        self.__start_watch_press()
        self.window.run()
        self.waiting = False
        self.clicking = False
        self.running = False
        self.logger.debug("main 运行结束")


if __name__ == "__main__":
    zyp = dualClicks()
    zyp.run()
