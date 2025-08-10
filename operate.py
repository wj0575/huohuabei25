from net import *
from queue import PriorityQueue

def manhattan_distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)
def heuristic(i, j, goals):
    # 计算到最近目标点的曼哈顿距离
    min_dist = min(abs(i - g[0]) + abs(j - g[1]) for g in goals)
    return min_dist * 0.8  # 可调节启发式权重

def operate(net, car, t, leak_value_allow, A, B):
    car_position = car.position_list[t]
    queue = []
    load_positions = get_load_position(t, net, car)
    in_positions = get_in_position(t, net, car)
    pack = []
    for dis in range(0, net.M + net.N + 1): # 按距离从小到大的顺序，处理各个节点上数据的去向。先构建队列
        for i in range(1, net.M + 1):
            for j in range(1, net.N + 1):
                if [i, j] in load_positions:
                    continue
                if manhattan_distance(i, j, car_position[0], car_position[1]) == dis:
                    if net.node_status[i][j] == 5:
                        queue.append((i, j))
                    elif net.node_status[i][j] == 10:
                        queue.append((i, j))
                        queue.append((i, j))
    for i in range(1, net.M + 1):
        for j in range(1, net.N + 1):
            # 清空当前节点的信息，以备A*算法计算下一个时刻
            if [i, j] not in load_positions:
                net.node_status[i][j] = 0
            net.horizontal[i][j] = 0
            net.vertical[i][j] = 0
    while queue:
        current_i, current_j = queue.pop(0)
        path_found = []
        targets = load_positions.copy()
        while not path_found:
            # A*算法实现
            q = PriorityQueue()
            q.put((0, current_i, current_j, []))
            came_from = {}
            g_score = {(i, j): float('inf') for i in range(1, net.M + 1) for j in range(1, net.N + 1)}
            g_score[(current_i, current_j)] = 0
            f_score = {(i, j): float('inf') for i in range(1, net.M + 1) for j in range(1, net.N + 1)}
            f_score[(current_i, current_j)] = heuristic(current_i, current_j, targets)

            while not q.empty():
                _, i, j, path = q.get()
                # 到达目标区域，并且该上传点未占满
                if ([i, j] in targets and net.node_status[i][j] + 5 <=
                        (net.bandwidth(i, j, t) + 10 + leak_value_allow
                        if [i, j] in load_positions else 10) -
                        (5 if [i, j] in in_positions else 0)):
                    path_found = path + [[i, j]]
                    break
                if len(path) > 20:
                    continue
                # 扩展相邻节点（上下左右）
                for di, dj, link_type in [(-1, 0, 'horizontal'), (1, 0, 'horizontal'),
                                          (0, -1, 'vertical'), (0, 1, 'vertical')]:
                    ni, nj = i + di, j + dj
                    # 如果已经走过，不允许再走
                    if (ni, nj) in came_from or [ni, nj] in path:
                        continue
                    if 1 <= ni <= net.M and 1 <= nj <= net.N:
                        # 检查链路带宽
                        available_link = (10 - net.horizontal[min(i, ni)][j] if link_type == 'horizontal'
                            else 10 - net.vertical[i][min(j, nj)])

                        # 检查目标点的拥挤程度
                        available_point = (((10 - net.node_status[ni][nj]) if [ni, nj] not in targets
                                           else (10 + net.bandwidth(ni, nj, t) - net.node_status[ni][nj])) -
                                           5 if [ni, nj] in in_positions else 0)

                        if available_link < 5:
                            continue # 带宽不足或者目标点完全占满

                        # 计算移动成本（带宽占用越高成本越高）A表示带宽占用权重，B表示目标点拥挤度权重
                        tentative_g = g_score[(i, j)] + (10 - available_link) * A + (10 - available_point) * B

                        if tentative_g < g_score[(ni, nj)]:
                            came_from[(ni, nj)] = (i, j)
                            g_score[(ni, nj)] = tentative_g
                            new_f = tentative_g + heuristic(ni, nj, targets)
                            q.put((new_f, ni, nj, path + [[i, j]]))


            # 将相邻targets中的相邻点加入targets
            new_targets = targets.copy()
            for target in targets:
                for ai, aj in [[0, -1], [1, 0], [0, 1], [-1, 0]]:
                    if (ai + target[0] < 1 or ai + target[0] > net.M or
                            aj + target[1] < 1 or aj + target[1] > net.N):
                        continue
                    if [ai + target[0], aj + target[1]] not in new_targets:
                        new_targets.append([ai + target[0], aj + target[1]])
            if targets == new_targets:
                break
            targets = new_targets.copy()
        if not path_found:
            continue

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