net_M = 20
net_N = 10 # 先写成10，之后改30
# 网络有20个节点，10行
T_TOTAL = 90
# 系统运行总时长（秒）

import random
BANDWIDTH_MIN = 5
BANDWIDTH_MAX = 20


# M*N的一个长方形网格，构建一个网格类
def get_bandwidth():
    # return random.randint(BANDWIDTH_MIN, BANDWIDTH_MAX)
    return 20
def get_node_fi():
    return random.randint(0, 9)

class Net:
    # Net类的节点统一使用(1,1)到(M,N)的坐标，而不是(0,0)到(M-1,N-1)的坐标
    def __init__(self):
        self.M = net_M
        self.N = net_N
        self.limit = 10 # 每个传感器上最多存储10Mb数据
        # 横向的线，horizontal[i][j]表示(i,j)和(i+1,j)之间的横线
        self.horizontal = []
        for i in range(self.M+3):
            self.horizontal.append([])
            for j in range(self.N+1):
                self.horizontal[i].append(0)
        # 纵向的线，vertical[i][j]表示(i,j)和(i,j+1)之间的竖线
        self.vertical = []
        for i in range(self.M+3):
            self.vertical.append([])
            for j in range(self.N+1):
                self.vertical[i].append(0)
        # 节点状态，即这一秒结束之后节点上有多少待发出的数据
        self.node_status = []
        # 节点上传速率最大值（bandwidth_max）和节点初始相位（fi）
        self.node_bandwidth_max = []
        self.node_fi = []
        for i in range(self.M+2): # 防溢出
            self.node_status.append([])
            self.node_bandwidth_max.append([])
            self.node_fi.append([])
            for j in range(self.N+2):
                self.node_status[i].append(0)
                self.node_bandwidth_max[i].append(get_bandwidth())
                # self.node_fi[i].append(get_node_fi())
    def bandwidth(self, i, j, t):
        """# 获取节点(i,j)在时间t的上传速率，使用折线函数b(t)，并四舍五入
        bandwidth_max = self.node_bandwidth_max[i][j]
        fi = (self.node_fi[i][j] + t) % 10
        tmp = (5 - abs(fi - 5)) * 0.2
        return round(bandwidth_max * tmp)"""
        # 获取节点(i,j)的上传速率，使用新的函数，𝜙=5+int(t/3)-m,其中m为传感器所在的列编号，int为取整。
        # 移动信号接收车的传输带宽为𝑏(𝜙 + 𝑡)
        fi = 5 + int(t/3) - i
        fi_plus_t = (fi + t) % 10
        tmp = (5 - abs(fi_plus_t - 5)) * 0.2
        return round(self.node_bandwidth_max[i][j] * tmp)
    def check(self, target_data):
        for i in range(1, self.M+1):
            for j in range(1, self.N+1):
                if self.node_status[i][j] > self.limit:
                    self.node_status[i][j] = self.limit
    def load(self, load_list, pack, leak_value_allow, t):
        delay, load_sum = 0,0 # 计算这次上传的时延，单位为(ms*Mb)
        details = {}
        for i, j in load_list:
            # 查找pack中结尾为[i, j]的路径
            lens = []
            for path in pack:
                if path[-1] == [i, j]:
                    lens.append(len(path) - 1)
            lens.sort() # 记录各条数据到达上传点的传输跳数，以备计算时延
            print("节点", i, j, "传输跳数", lens, "节点信息量", self.node_status[i][j])
            available_bandwidth = self.bandwidth(i, j, t)
            while available_bandwidth >= 5 - leak_value_allow and len(lens) > 0:
                # print(available_bandwidth, lens)
                if available_bandwidth >= 5:
                    self.node_status[i][j] -= 5
                    data.add_data_out(5)
                    load_sum += 5
                    jump = lens.pop(0)
                    delay += 5 * (50 * jump + 50 + t % 15 * 1000) # 延迟计算
                    available_bandwidth -= 5
                    print("节点", i, j, "上传5Mb", "时延", 50 * jump + 50 + t % 15 * 1000)
                elif available_bandwidth + leak_value_allow >= 5:
                    self.node_status[i][j] -= available_bandwidth
                    data.add_data_out(available_bandwidth)
                    load_sum += available_bandwidth
                    jump = lens.pop(0)
                    print("节点", i, j, "上传", available_bandwidth, "Mb",
                          "时延", available_bandwidth * (50 * jump + 50 + t % 15 * 1000))
                    delay += available_bandwidth * (50 * jump + 50 + t % 15 * 1000) # 延迟计算
                    available_bandwidth = 0

        return {
            "delay": delay,
            "load_sum": load_sum,
            "average_delay": 0 if load_sum == 0 else delay // load_sum,
            "details": details,
        }

class Data:
    global net_M, net_N
    def __init__(self):
        self.data_in = 0
        self.data_out = 0
    def add_data_in(self, add_sum):
        self.data_in += add_sum
        return self.data_out
    def add_data_out(self, add_sum):
        self.data_out += add_sum
        return self.data_out
    def cal_data_in_net(self, target_net):
        sum = 0
        for i in range(1, net_M+1):
            for j in range(1, net_N+1):
                sum += target_net.node_status[i][j]
        return sum
    def cal_data_leak(self, target_net):
        data_in_net = self.cal_data_in_net(target_net)
        leak = self.data_in - self.data_out - data_in_net
        return leak
    def cal_leak_percent(self, target_net):
        leak = self.cal_data_leak(target_net)
        percent = int((leak / self.data_in) * 100)
        return percent

net = Net()
data = Data()

class Car:
    def __init__(self, position_x, position_y, direction, net):
        self.position = [position_x, position_y]
        # 建立每一个时刻的信号接收车位置列表
        self.position_list = [] # 0 时刻的位置

        # 信号接收车位置列表
        route = [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 4, 4, 4, 4, 4, 4, 4, 4,
                 5, 6, 6, 6, 6, 6, 6, 6, 6, 7, 8, 8, 8, 8, 8, 8, 8, 8, 9, 10,
                 10, 10, 10, 10, 10, 10, 10, 11, 12, 12, 12, 12, 12, 12, 12, 12, 13, 14, 14, 14,
                 14, 14, 14, 14, 14, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16,
                 16, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17]

        for t in range(T_TOTAL + 1):
            position = [route[t] + 1, position_y]
            self.position_list.append(position)
        self.add_num = [
            [-1, 0], [0, 0], [1, 0], [-1, 1], [0, 1], [1, 1],
        ]

car = Car(position_x=2, position_y=5, direction=1, net=net)

def get_load_position(t, net, car):
    car_position = []
    for adder in car.add_num:
        car_position.append([car.position_list[t][0] + adder[0], car.position_list[t][1] + adder[1]])
    return car_position

def generate_data(t):
    if t % 15 != 0 and t % 15 != 1:
        return
    if t % 30 == 0 or t % 30 == 1:
        # 偶数行所有节点产生一个5Mb信号
        for i in range(1, net.M+1):
            for j in range(2, net.N+1, 2):
                net.node_status[i][j] += 5
    else:
        # 奇数行所有节点产生一个5Mb信号
        for i in range(1, net.M+1):
            for j in range(1, net.N+1, 2):
                net.node_status[i][j] += 5
    data.add_data_in(500)
    net.check(data) # 检查是否有溢出


# 测试区域
if __name__ == "__main__":
    """print(net.node_bandwidth_max[1][1])
    for i in range(30):
        print(net.bandwidth(1, 1, i))"""
    for t in range(T_TOTAL + 1):
        print("t="+str(t).ljust(5), end="")
        for i in range(1, net.M+1):
            print(net.bandwidth(i, 5, t), end='\t')
        print()
