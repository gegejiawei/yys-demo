from yys_tools import yys_tools
import pyautogui
import time
from datetime import datetime


if __name__ == "__main__":

    zyp = yys_tools(None, None)
    
    hstr = '1001100000000100001100011110001000110011111000110011111111111110001111111111111100111000000011100000000000000000100000111110000101100000000000010000000011000001000000010100001000010011110000000000001101000000111000100100000111111011010011111111110111011111'

    zone = [385, 403, 30, 30]

    print(zyp.simple_compair(hstr, zone))

    # img = zyp.get_zone_img(zone)
    # img.show()

    # print(zyp.img2hash(img))

    # zyp.normal_click()
    # zyp.click_yulin_start()
    # zone = [360, 390, 26, 26]
    # num, circles = zyp.count_circles(zone, 22, 33, True)
    # print('circles num =>', num)
    # # for circle in circles:
    #     print(f'圆心 => ({circle[0]}, {circle[1]}), 半径 => {circle[2]}')
    # while zyp.click_tansuo_circles():
    #     print("has circles")
    #     time.sleep(1)
    # print('no circles')
    # img = zyp.get_zone_img(zone)
    # img.show()
    # print(zyp.check_status_has_crew2())

    # count_chked = 0
    # count_miss = 0
    # for i in range(100):
    #     if zyp.simple_compair(hstr, zone):
    #         print(f"{datetime.now().strftime('%H:%M:%S')} => checked")
    #         count_chked += 1
    #     else:
    #         print("not checked")
    #         count_miss += 1
    #     time.sleep(1)
    # print(f"checked => {count_chked}; miss => {count_miss}")
    # zyp.playsound()

    # while True:
    #     num, cs = zyp.count_circles(zone, 15, 25, False)
    #     if num == 1:
    #         print(
    #             f"found circles => {num}, center => ({int(cs[0][0])}, {int(cs[0][1])})")
    #     else:
    #         print(f"num = {num}")
    #     time.sleep(1)
    # zyp.normal_click()
    # for i in range(50):
    #     if zyp.check_status_started():
    #         print(f"{datetime.now().strftime('%H:%M:%S')} => checked")
    #     else:
    #         print('not checked')
    #     time.sleep(0.7)

