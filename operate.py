from net import *
from queue import PriorityQueue

def manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)
def heuristic(i, j, goals):
    # 计算到最近目标点的曼哈顿距离
    min_dist = min(abs(i - g[0]) + abs(j - g[1]) for g in goals)
    return min_dist * 0.8  # 可调节启发式权重

def operate(net, t):
    car_position = car.position_list[t]
    queue = []
    for dis in range(0, net.M + net.N + 1): # 按距离从小到大的顺序，处理各个节点上数据的去向。先构建队列
        for i in range(1, net.M + 1):
            for j in range(1, net.N + 1):
                # print(i, j, net.node_status[i][j])
                if manhattan_distance(i, j, car_position[0], car_position[1]) == dis:
                    if net.node_status[i][j] == 5:
                        queue.append((i, j))
                    elif net.node_status[i][j] == 10:
                        queue.append((i, j))
                        queue.append((i, j))
    for i in range(1, net.M + 1):
        for j in range(1, net.N + 1):
            # 清空当前节点的信息，以备A*算法计算下一个时刻
            net.node_status[i][j] = 0
            net.horizontal[i][j] = 0
            net.vertical[i][j] = 0
    load_positions = get_load_position(t, net, car)
    pack = []
    while queue:
        current_i, current_j = queue.pop(0)

        # A*算法实现
        q = PriorityQueue()
        q.put((0, current_i, current_j, []))
        came_from = {}
        g_score = {(i, j): float('inf') for i in range(1, net.M + 1) for j in range(1, net.N + 1)}
        g_score[(current_i, current_j)] = 0
        f_score = {(i, j): float('inf') for i in range(1, net.M + 1) for j in range(1, net.N + 1)}
        f_score[(current_i, current_j)] = heuristic(current_i, current_j, load_positions)

        path_found = []
        while not q.empty():
            _, i, j, path = q.get()
            # 到达目标区域，并且该上传点未占满
            if [i, j] in load_positions and net.node_status[i][j] + 5 <= net.bandwidth(i, j, t):
                path_found = path + [[i, j]]
                break
            if len(path) > 20:
                continue
            # 扩展相邻节点（上下左右）
            for di, dj, link_type in [(-1, 0, 'horizontal'), (1, 0, 'horizontal'),
                                      (0, -1, 'vertical'), (0, 1, 'vertical')]:
                ni, nj = i + di, j + dj
                if 1 <= ni <= net.M and 1 <= nj <= net.N:
                    # 检查链路带宽
                    available_link = (10 - net.horizontal[min(i, ni)][j] if link_type == 'horizontal'
                        else 10 - net.vertical[i][min(j, nj)])

                    # 检查目标点的拥挤程度
                    available_point = (10 - net.node_status[ni][nj] if [ni, nj] not in load_positions
                                       else 10 + net.bandwidth(ni, nj, t) - net.node_status[ni][nj])

                    if available_link < 5:
                        continue # 带宽不足或者目标点完全占满

                    # 计算移动成本（带宽占用越高成本越高）
                    tentative_g = g_score[(i, j)] + (10 - available_link) * 0.1 + (10 - available_point) * 0.1

                    if tentative_g < g_score[(ni, nj)]:
                        came_from[(ni, nj)] = (i, j)
                        g_score[(ni, nj)] = tentative_g
                        new_f = tentative_g + heuristic(ni, nj, load_positions)
                        q.put((new_f, ni, nj, path + [[i, j]]))
        # 记录最终路径或最近路径
        if not path_found:
            # 返回一个列表仅包含初始位置的坐标，即不动
            path_found = [[current_i, current_j]]
        # 更新网络状态
        prev = path_found[0]
        for node in path_found[1:]:
            # 更新水平/垂直线路带宽
            if prev[0] == node[0]:  # 垂直移动
                net.vertical[prev[0]][min(prev[1], node[1])] += 5
            else:  # 水平移动
                net.horizontal[min(prev[0], node[0])][prev[1]] += 5
            prev = node

        # 更新终点节点状态
        end_i, end_j = path_found[-1]
        net.node_status[end_i][end_j] += 5

        print(path_found)
        pack.append(path_found)
    return pack

def find_nearest_path(start_i, start_j, target):
    # 简单直线路径生成（实际可替换为BFS）
    path = [[start_i, start_j]]
    i, j = start_i, start_j
    while (i != target[0]) or (j != target[1]):
        if i < target[0]:
            i += 1
        elif i > target[0]:
            i -= 1
        if j < target[1]:
            j += 1
        elif j > target[1]:
            j -= 1
        path.append([i, j])
    return path