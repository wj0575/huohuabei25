# 火花杯2025 A题
import tkinter as tk
import ctypes

T_TOTAL = 90

global net_M, net_N

def demo(leak_value_allow, A, B, auto_update=False):
    # 初始化时间变量
    global current_t
    current_t = 0
    from net import Net, Data, Car # 导入Net, Data, Car类
    net = Net()
    data = Data()
    car = Car(position_x=2, position_y=5, direction=1, net=net)

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

    delay, delay_wait, delay_rest = 0, 0, 0 # 两类时延分别计算总和

    for i in range(1, net.M + 1):
        point_texts.append([]) # point_texts[i][0]保存当前时刻这一列最大上传带宽
        point_texts[-1].append(tk.Label(bandwidth_frame, fg=color_ltblue, font=("Consolas", 15)))
        point_texts[-1][0].place(relx=0.05 * i - 0.025, rely=0.5,
                                     relwidth=0.04, relheight=0.6, anchor="center")
        link_texts_vertical.append([[]])
        link_texts_horizontal.append([[]])
        for j in range(1, net.N + 1):
            # 创建一个矩形，在display框架下
            point_texts[i].append(tk.Label(display, bg=color_ltblue))
            point_texts[i][-1].place(relx=0.05 * i - 0.025, rely=0.1 * j - 0.05,
                                     relwidth=0.03, relheight=0.06, anchor="center")
            if i != net.M:
                link_texts_horizontal[i].append(tk.Label(display, bg=color_grey))
                link_texts_horizontal[i][-1].place(relx=0.05 * i, rely=0.1 * j - 0.05,
                                                relwidth=0.02, relheight=0.01, anchor="center")
            if j != net.N:
                link_texts_vertical[i].append(tk.Label(display, bg=color_grey))
                link_texts_vertical[i][-1].place(relx=0.05 * i - 0.025, rely=0.1 * j,
                                                relwidth=0.005, relheight=0.04, anchor="center")
        # 记录这一秒的运行状态


    from operate import generate_data, get_load_position, operate
    def set(t):
        generate_data(t, net, data)
        load_list = get_load_position(t, net, car)
        pack = operate(net, car, t, leak_value_allow, A, B)
        data.result["path"].append(pack) # 在result中记录这一秒的路径
        delay_data = net.load(load_list, pack, leak_value_allow, t, data)
        data.result["delay_average"].append(data.cal_delay() // data.data_out)
        data.result["delay_wait"].append(delay_data["delay_wait"])
        data.result["delay_rest"].append(delay_data["delay_rest"])
        for i in range(1, net.M + 1):
            text = str(net.bandwidth(i, 5, t)) + "Mb"
            point_texts[i][0].config(text=text, font=("Consolas", 15), fg="blue")
        for j in range(1, net.N + 1):
            for i in range(1, net.M + 1):
                # 如果在load_list中有[i, j]
                text = str(i) + ',' + str(j) + '\n'
                if [i, j] in load_list:
                    color = "blue"
                else:
                    color = "black"
                if net.node_status[i][j] >= 10:
                    color_bg = "#FFAA80"
                elif net.node_status[i][j] >= 5:
                    color_bg = "#FFD170"
                else:
                    color_bg = "#B2FF6C"
                text += str(net.node_status[i][j])
                point_texts[i][j].config(text=text, font=("Consolas", 10), fg=color, bg=color_bg)
                if i != net.M:
                    if net.horizontal[i][j] >= 10:
                        color_bg = "#D90D0D"
                    elif net.horizontal[i][j] >= 5:
                        color_bg = "#E3961C"
                    else:
                        color_bg = "#5FE348"
                    link_texts_horizontal[i][j].config(text="", bg=color_bg)
                if j != net.N:
                    if net.vertical[i][j] >= 10:
                        color_bg = "#D90D0D"
                    elif net.vertical[i][j] >= 5:
                        color_bg = "#E3961C"
                    else:
                        color_bg = "#5FE348"
                    link_texts_vertical[i][j].config(text="", bg=color_bg)

    def next_second():
        global current_t, T_TOTAL
        current_t += 1
        text = "Time: " + str(current_t) + " s\n"
        text += "Data In: " + str(data.data_in) + " Mb\n"
        text += "Data Out: " + str(data.data_out) + " Mb\n"
        text += "Data In Net: " + str(data.cal_data_in_net(net)) + " Mb\n"
        text += "Data Leak: " + str(data.cal_data_leak(net)) + " Mb\n"
        text += "Data Leak Percent: " + str(data.cal_leak_percent(net)) + " %\n"
        text += "\n"
        text += "Average Delay: " + str(data.cal_delay() // data.data_out) + "ms\n"
        text += "Average Delay Wait: " + str(data.delay_wait // data.data_out) + "ms\n"
        text += "Average Delay Rest: " + str(data.delay_rest // data.data_out) + "ms\n"
        # 左对齐
        if current_t > T_TOTAL:
            text += "运行结束"
            # 关闭窗口
            root.destroy()
            return
        time_text.config(text=text, font=("Consolas", 12), fg="white", justify=tk.LEFT)

        set(current_t)

    button.config(command=next_second)
    current_t = 0
    set(current_t)

    def auto_update():
        if current_t <= T_TOTAL:
            root.after(100, auto_update)
        next_second()
    if auto_update:
        auto_update()  # 启动自动刷新
    root.mainloop() # 窗口运行显示状态

    data.result["summary"] = {
        "leak_value_allow": leak_value_allow,
        "A": A,
        "B": B,
        "run_time": len(data.result["path"]) - 1,
        "data_in": data.data_in,
        "data_leak": data.data_in - data.data_out,
        "data_leak_percent": (data.data_in - data.data_out) / data.data_in,
        "average_delay": data.result["delay_average"][-1],
        "average_delay_wait": data.result["delay_wait"][-1] // data.data_out,
        "average_delay_rest": data.result["delay_rest"][-1] // data.data_out,
    }
    return data.result.copy()