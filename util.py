#!/usr/bin/python
# -*- coding: utf-8 -*-

import networkx as nx
import numpy as np
import Global
import NetworkInfo as ni
import copy


def max_flow(bandwidth, src_dict, dst_dict):

    """ 最小费用最大流：给定多源点和多汇点及其流量，返回最大流矩阵 """

    # 转换为networkx格式的图，边权均为1
    G = nx.DiGraph()
    for i in range(len(bandwidth)):
        for j in range(len(bandwidth)):
            if bandwidth[i][j] > 0:
                G.add_edge(i, j, capacity=bandwidth[i][j], weight=1)

    # 添加虚拟源点-1和汇点-2
    for (s, value) in src_dict.items():
        G.add_edge(-1, s, capacity=value, weight=1)
    for (d, value) in dst_dict.items():
        G.add_edge(d, -2, capacity=value, weight=1)

    # 最小费用最大流
    flow = nx.max_flow_min_cost(G, -1, -2)

    flow_matrix = [[0 for col in range(len(bandwidth))] for row in range(len(bandwidth))]
    for i in range(len(bandwidth)):
        for (j, f) in flow[i].items():
            if j >= 0:
                flow_matrix[i][j] = f

    # 返回流矩阵
    return flow_matrix


def distance(adj, u, v):

    """ Node距离：返回给定两个Node在网络中的距离（跳数） """

    return nx.shortest_path_length(nx.from_numpy_matrix(np.mat(adj)), u, v)


def get_avail(request, node_list, request_placement):

    """ 计算链可用性：如可用性不足，返回可用性最小的nf的索引位置，否则返回-1 """

    # avail = node_list[request.src].avail * node_list[request.dst].avail
    avail = 1

    # 可用性最小的nf的次序（在nf list中的序号而非id）
    bottleneck_index = -1
    bottleneck_avail = float("inf")
    for i, nf in enumerate(request_placement[request.id]):
        nf_fail = 1
        for k in nf.keys():
            nf_fail *= 1 - node_list[k].avail
        nf_avail = 1 - nf_fail
        avail *= nf_avail
        if nf_avail < bottleneck_avail:
            bottleneck_index = i
            bottleneck_avail = nf_avail

    if avail < request.avail:
        return bottleneck_index
    else:
        return -1


def get_rest_capacity(request, request_placement):

    """ 计算使用的实例剩余的capacity是否满足rate，返回不满足的nf索引位置，否则返回-1 """

    for i, nf in enumerate(request_placement[request.id]):
        rate_sum = 0
        for (v, instance) in nf.items():
            rate_sum += instance.capacity
        if rate_sum < request.rate:
            return i

    return -1


def get_placement_vector(request, request_placement):

    """ 将请求部署表 request_placement 转换为部署位置向量（全是list表示的Node） """

    vector = [[request.src]]
    for nf in request_placement[request.id]:
        vector.append(nf.keys())
    vector.append([request.dst])
    return vector


def add_instance(bandwidth, node_list, instance_registry, instance_num, request, request_placement, nf_index):

    """ 为指定nf增加一个实例 """

    # 找距离前驱和后继Node距离之和最小的Node
    vector = get_placement_vector(request, request_placement)
    pre_nodes = vector[nf_index]
    post_nodes = vector[nf_index + 2]
    candidate_nodes_distance = [[i, 0] for i in range(len(node_list))]
    for v in range(len(node_list)):
        distance_sum = 0
        for pre in pre_nodes:
            distance_sum += distance(bandwidth, pre, v)
        for post in post_nodes:
            distance_sum += distance(bandwidth, v, post)
        candidate_nodes_distance[v][1] = distance_sum
    # 排除已有同类实例的Node
    for u in vector[nf_index + 1]:
        candidate_nodes_distance[u][1] = float("inf")
    # 按照距离远近排序
    candidate_nodes_distance = sorted(sorted(candidate_nodes_distance, key=lambda n: node_list[n[0]].avail, reverse=True), key=lambda n: n[1])
    candidate_nodes = [n[0] for n in candidate_nodes_distance]
    nf_id = request.nf_list[nf_index]
    for v in candidate_nodes:
        # 如果已经有同类实例，且capacity还有剩余
        same_instance = None
        for instance in node_list[v].instances:
            if instance.type == nf_id and instance.capacity > 0:
                same_instance = instance
        if same_instance is not None:
            # 在表中登记这个新实例
            request_placement[request.id][nf_index][v] = same_instance
            break

        elif node_list[v].CPU > Global.NF_CPU_REQUIREMENT[nf_id] and v not in vector[nf_index + 1]:
            # 在request_placement中部署
            new_instance = ni.Instance(instance_num[nf_id], nf_id)
            instance_num[nf_id] += 1
            new_instance.placement = v
            request_placement[request.id][nf_index][v] = new_instance
            instance_registry[nf_id].append(new_instance)
            # 更新Node
            node_list[v].CPU -= Global.NF_CPU_REQUIREMENT[nf_id]
            node_list[v].instances.append(new_instance)
            break
    # 没有满足资源需求的Node了
    else:
        raise AssertionError("No CPU to satisfy Availability!")


def get_route(bandwidth, request, request_placement):

    """
        计算路由策略：给定实例的放置方案后，计算每一段的网络流；更新instance的capacity，返回总网络流矩阵
        实例之间的流量分配：按照实例剩余capacity的比例进行分配
    """

    flow_assignment = [{request.src: request.rate}]

    for i, nf in enumerate(request_placement[request.id]):
        capacity_sum = sum(instance.capacity for (v, instance) in nf.items())
        # 为每个实例确定流量分配
        flow_assignment_nf = {}
        for (v, instance) in nf.items():
            # 前面保证了总capacity大于需求的流量，因此实例的capacity不会不够
            c = instance.capacity * request.rate / float(capacity_sum)
            flow_assignment_nf[v] = int(round(c))

        """ 四舍五入取整，并使总和等于源 """
        delta = sum(flow_assignment_nf.values()) - request.rate
        max_value_key = max(flow_assignment_nf, key=lambda x: flow_assignment_nf[x])
        flow_assignment_nf[max_value_key] -= delta

        for (v, instance) in nf.items():
            instance.assignment[request.id] = flow_assignment_nf[v]
            instance.capacity -= flow_assignment_nf[v]
            # 应该不会发生这种事↓↓↓，不过还是严谨一下
            if instance.capacity < 0:
                raise AssertionError("No enough capacity of instance!")
        flow_assignment.append(flow_assignment_nf)

    flow_assignment.append({request.dst: request.rate})

    # 为每一段计算网络流
    flow_matrix = np.mat([[0 for col in range(len(bandwidth))] for row in range(len(bandwidth))])
    for k, segment in enumerate(flow_assignment):
        if k < len(flow_assignment)-1:
            flow_matrix_segment = np.mat(max_flow(bandwidth, flow_assignment[k], flow_assignment[k+1]), dtype="int32")
            flow_matrix += flow_matrix_segment
            # 更新带宽矩阵
            bandwidth = (np.mat(bandwidth) - flow_matrix_segment).tolist()

    return flow_matrix.tolist()