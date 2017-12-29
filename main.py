import sys
import contextlib
import pyautogui
import time
import math
from subprocess import call
from ctypes import windll


# compare gbr
def color_similar(c1, c2, threshold=10):
    try:
        c1_hex = format(c1, 'x')
        c2_hex = format(c2, 'x')

        c1_g = int(c1_hex[0:2], 16)
        c1_b = int(c1_hex[2:4], 16)
        c1_r = int(c1_hex[4:6], 16)

        c2_g = int(c2_hex[0:2], 16)
        c2_b = int(c2_hex[2:4], 16)
        c2_r = int(c2_hex[4:6], 16)

        # def within_range(v1, v2):
        #     return abs(v2-v1) <= threshold

        return abs(c1_g - c2_g) + abs(c1_b - c2_b) + abs(c1_r - c2_r) < threshold
        # return within_range(c1_g, c2_g) and within_range(c1_b, c2_b) and within_range(c1_r, c2_r)
    except Exception as e:
        # print "error comparing color %s and %s" % (str(c1), str(c2))
        # print str(e)
        return False


def find_person(tl, width, height, getpixel, heads, threshold=10):
    top_color = 3945780
    btm_color = 6699832
    btm_color_bak = 6700086
    top_btm_range = 118 - 56
    print "finding person ..."
    found_person = False
    person_pos = (0, 0)
    for x in range(tl[0] + int(0.1 * width), tl[0] + int(0.9 * width)):
        for y in range(tl[1] + int(0.3 * height), tl[1] + int(0.7 * height)):
            if color_similar(int(getpixel(x, y)), top_color, threshold):
                print 'found person head @ (%d, %d)' % (x, y)
                print 'person foot is %d' % int(getpixel(x, y + top_btm_range))
                heads.append((x, y))
                if color_similar(int(getpixel(x, y + top_btm_range)), btm_color, threshold) or color_similar(
                        int(getpixel(x, y + top_btm_range)), btm_color_bak):
                    print 'found person'
                    found_person = True
                    person_pos = (x, y + top_btm_range - 8)
                break
        if found_person:
            break
    if found_person:
        pyautogui.moveTo(person_pos[0], person_pos[1])
        return person_pos
    else:
        return None


def main():
    dc = windll.user32.GetDC(0)

    def getpixel(x, y):
        return windll.gdi32.GetPixel(dc, x, y)

    adb_path = r"C:\\platform-tools\adb.exe"
    base_adb_shell = adb_path + " shell input swipe 400 400 500 500 "
    adb_cmds = [adb_path, "shell", "input", "swipe", "400", "400", "500", "500"]

    tl = (1373, 73)
    br = (1869, 954)
    height = -1
    width = -1

    option_prompt = "select an option:\n"

    sel = raw_input(option_prompt)
    heads = []
    while sel != 'stop':
        if sel == 'start':
            print "starting"
            center = ((tl[0] + br[0])/2, (tl[1] + br[1])/2)
            height = br[1] - tl[1]
            width = br[0] - tl[0]
            print "center is %s" % str(center)
            print "height is %d, width is %d" % (height, width)
            print "center color is %s" % str(getpixel(center[0], center[1]))

            person_pos = find_person(tl=tl, width=width, height=height, getpixel=getpixel, heads=heads)

            base_distance = math.sqrt((person_pos[0]-center[0])**2 + (person_pos[1]-center[1])**2)

            print "jumping ..."
            base_jump_time = 720
            call(base_adb_shell + str(base_jump_time))
            print "wait 2s"
            time.sleep(2)

            while True:
                threshold = 15
                person_pos = find_person(tl=tl, width=width, height=height, getpixel=getpixel, heads=heads, threshold=threshold)
                while person_pos is None:
                    threshold += 5
                    person_pos = find_person(tl=tl, width=width, height=height, getpixel=getpixel, heads=heads, threshold=threshold)
                distance = math.sqrt((person_pos[0] - center[0]) ** 2 + (person_pos[1] - center[1]) ** 2)
                print "jumping ..."
                jump_time = int(720 * distance / base_distance)
                call(base_adb_shell + str(jump_time))
                print "wait 2s"
                time.sleep(2)

        elif sel == 'tl':
            mouse_x, mouse_y = pyautogui.position()
            tl = (mouse_x, mouse_y)
            print "setting the top left corner location to (%d, %d)" % tl
        elif sel == 'br':
            mouse_x, mouse_y = pyautogui.position()
            br = (mouse_x, mouse_y)
            print "setting the bottom right corner location to (%d, %d)" % br
        elif sel == "test":
            for pos in heads:
                print pos
                pyautogui.moveTo(pos[0], pos[1])
                time.sleep(5)

        sel = raw_input(option_prompt)

    print 'bot stops'


if __name__ == '__main__':
    main()
