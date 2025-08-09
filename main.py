# 火花杯2025 A题
from net import *
# from control import *
import tkinter as tk
import ctypes
import time

leak_value_allow = 0

global net, car
global T_TOTAL
global net_M, net_N

# 初始化时间变量
current_t = 0

# 构建窗口
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except AttributeError:
    pass


point_texts = [[]]
link_texts_horizontal = [[]]
link_texts_vertical = [[]]
band_texts = [[]]

root = tk.Tk()
root.title("2025火花杯A题 传感器数据调度问题")
root.geometry("2500x1250")

color_ltblue = "#BBBBF6"
color_white = "#ffffff"
color_grey = "#888888"
color_black = "#000000"

control_frame = tk.Frame(root, bg=color_grey)
control_frame.place(relx=0.6, rely=0.05, relwidth=0.8, relheight=0.18, anchor="center")
bandwidth_frame = tk.Frame(root, bg=color_grey)
bandwidth_frame.place(relx=0.6, rely=0.95, relwidth=0.8, relheight=0.18, anchor="center")

# 显示带宽
for i in range(1, net.M+1):
    band_texts.append(tk.Label(bandwidth_frame))
    band_texts[-1].place(relx=0.05 * i - 0.025, rely=0.5, relwidth=0.03, relheight=0.06, anchor="center")

# 时间t
time_text = tk.Label(root, text="", bg=color_grey, fg=color_white)
time_text.place(relx=0.1, rely=0.2, relwidth=0.18, relheight=0.36, anchor="center")

# 显示区域
display = tk.Frame(root, bg=color_white)
display.place(relx=0.6, rely=0.5, relwidth=0.8, relheight=0.8, anchor="center")
# 设置一个按钮
button = tk.Button(control_frame, text="下一秒", bg="green", fg=color_white)
button.place(relx=0.95, rely=0.5, relwidth=0.08, relheight=0.6, anchor="center")

for i in range(1, net_M + 1):
    point_texts.append([]) # point_texts[i][0]保存当前时刻这一列最大上传带宽
    point_texts[-1].append(tk.Label(bandwidth_frame, fg=color_ltblue, font=("Consolas", 15)))
    point_texts[-1][0].place(relx=0.05 * i - 0.025, rely=0.5,
                                 relwidth=0.04, relheight=0.6, anchor="center")
    link_texts_vertical.append([[]])
    link_texts_horizontal.append([[]])
    for j in range(1, net_N + 1):
        # 创建一个矩形，在display框架下
        point_texts[i].append(tk.Label(display, bg=color_ltblue))
        point_texts[i][-1].place(relx=0.05 * i - 0.025, rely=0.1 * j - 0.05,
                                 relwidth=0.03, relheight=0.06, anchor="center")
        if i != net_M:
            link_texts_horizontal[i].append(tk.Label(display, bg=color_grey))
            link_texts_horizontal[i][-1].place(relx=0.05 * i, rely=0.1 * j - 0.05,
                                            relwidth=0.02, relheight=0.04, anchor="center")
        if j != net_N:
            link_texts_vertical[i].append(tk.Label(display, bg=color_grey))
            link_texts_vertical[i][-1].place(relx=0.05 * i - 0.025, rely=0.1 * j,
                                            relwidth=0.02, relheight=0.04, anchor="center")

from operate import *
def set(t):
    generate_data(t)
    load_list = get_load_position(t, net, car)
    print("Time", t)
    pack = operate(net, t)
    delay_data = net.load(load_list, pack, leak_value_allow, t)
    print("delay_data", delay_data)
    for i in range(1, net.M + 1):
        text = str(net.bandwidth(i, 5, t)) + "Mb"
        point_texts[i][0].config(text=text, font=("Consolas", 15), fg="blue")
    for j in range(1, net_N + 1):
        for i in range(1, net_M + 1):
            # 如果在load_list中有[i, j]
            text = str(i) + ',' + str(j) + '\n'
            if [i, j] in load_list:
                color = "red"
            else:
                color = "black"
            """if net.node_status[i][j] > 0:
                if net.node_status[i][j] == 5:
                    text += '■'
                elif net.node_status[i][j] == 10:
                    text += '■ ■'"""
            text += str(net.node_status[i][j])
            point_texts[i][j].config(text=text, font=("Consolas", 10), fg=color)
            # print(i, j)
            # print(net.horizontal)
            if i != net_M:
                link_texts_horizontal[i][j].config(text=net.horizontal[i][j])
            if j != net_N:
                link_texts_vertical[i][j].config(text=net.vertical[i][j])

current_t = 0
set(current_t)

def next_second():
    global current_t
    current_t += 1
    text = "Time: " + str(current_t) + "\n"
    text += "Data In: " + str(data.data_in) + "\n"
    text += "Data Out: " + str(data.data_out) + "\n"
    text += "Data In Net: " + str(data.cal_data_in_net(net)) + "\n"
    text += "Data Leak: " + str(data.cal_data_leak(net)) + "\n"
    print(data.cal_leak_percent(net))
    text += "Data Leak Percent: " + str(data.cal_leak_percent(net))
    # 左对齐
    if current_t > T_TOTAL:
        text += "运行结束"
        while True:
            time.sleep(1)
    time_text.config(text=text, font=("Consolas", 16), fg="white", justify=tk.LEFT)

    set(current_t)

button.config(command=next_second)



root.mainloop()


