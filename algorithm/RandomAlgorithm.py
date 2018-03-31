#!/usr/bin/python
# -*- coding: utf-8 -*-

import networkx as nx
import numpy as np
import Global
import NetworkInfo as ni
import copy
import util
import random


def random_deploy(bandwidth_origin, node_list, request_list):

    """ 随机部署算法 """

    # 剩余带宽矩阵
    bandwidth = copy.copy(bandwidth_origin)

    # 储存每个请求的带宽消耗矩阵
    flow_matrix_request = {}

    # 实例注册表(每种NF一个子表)
    instance_registry = [[] for i in range(Global.NF_TYPE_NUM)]

    # 每个请求选择的部署位置
    request_placement = []
    for r in request_list:
        request_placement.append([{} for nf in r.nf_list])

    # 每个类型nf实例个数
    instance_num = [0] * Global.NF_TYPE_NUM

    """ 依次部署请求 """
    for request in request_list:
        # 依次部署请求中的nf
        for i, nf in enumerate(request.nf_list):
            # 随机选择一个点
            sample_node = random.sample(range(len(node_list)), len(node_list))
            # 直到满足资源需求
            for v in sample_node:
                if node_list[v].CPU > Global.NF_CPU_REQUIREMENT[nf]:
                    # 新建一个实例，并放置在当前Node
                    new_instance = ni.Instance(instance_num[nf], nf)
                    instance_num[nf] += 1
                    new_instance.placement = v
                    # 在两个表中登记这个新实例
                    request_placement[request.id][i][v] = new_instance
                    instance_registry[nf].append(new_instance)
                    # 更新Node
                    node_list[v].CPU -= Global.NF_CPU_REQUIREMENT[nf]
                    node_list[v].instances.append(new_instance)
                    break

            # 没有满足资源需求的Node了
            else:
                raise AssertionError("No CPU!")

        # 计算可用性
        avail_bottleneck_index = util.get_avail(request, node_list, request_placement)
        # 所有使用的实例剩余capacity总和
        capacity_bottleneck_index = util.get_rest_capacity(request, request_placement)

        # 可用性和剩余capacity拉满
        while avail_bottleneck_index > -1 or capacity_bottleneck_index > -1:

            if avail_bottleneck_index > -1:
                bottleneck_index = avail_bottleneck_index
            elif capacity_bottleneck_index > -1:
                bottleneck_index = capacity_bottleneck_index
            else:
                break

            # placed_nodes = request_placement[request.id][bottleneck_index].keys()
            # # 随机选择一个点
            # sample_node = random.sample(range(len(node_list)), len(node_list))
            # # 直到满足资源需求
            # for v in sample_node:
            #     if v not in placed_nodes:
            #         # 如果已经有同类实例，且capacity还有剩余
            #         same_instance = None
            #         for instance in node_list[v].instances:
            #             if instance.type == nf and instance.capacity > 0:
            #                 same_instance = instance
            #         if same_instance is not None:
            #             # 在表中登记这个新实例
            #             request_placement[request.id][bottleneck_index][v] = same_instance
            #             break
            #
            #         # 如果没有同类实例
            #         elif node_list[v].CPU > Global.NF_CPU_REQUIREMENT[nf]:
            #             # 新建一个实例，并放置在当前Node
            #             new_instance = ni.Instance(instance_num[nf], nf)
            #             instance_num[nf] += 1
            #             new_instance.placement = v
            #             # 在两个表中登记这个新实例
            #             request_placement[request.id][bottleneck_index][v] = new_instance
            #             instance_registry[nf].append(new_instance)
            #             # 更新Node
            #             node_list[v].CPU -= Global.NF_CPU_REQUIREMENT[nf]
            #             node_list[v].instances.append(new_instance)
            #             break
            #
            # # 没有满足资源需求的Node了
            # else:
            #     raise AssertionError("No CPU!")

            """ 增加实例时随机选点有bug，暂时使用更优的部分extend策略 """
            util.add_instance(bandwidth, node_list, instance_registry, instance_num, request, request_placement,
                              bottleneck_index)

            # 计算可用性和剩余capacity
            avail_bottleneck_index = util.get_avail(request, node_list, request_placement)
            capacity_bottleneck_index = util.get_rest_capacity(request, request_placement)

        """ 根据部署位置计算链的网络流 """
        flow_matrix = util.get_route(bandwidth, request, request_placement)
        flow_matrix_request[request.id] = flow_matrix
        bandwidth = (np.mat(bandwidth) - np.mat(flow_matrix)).tolist()

    """ 部署完毕 """

    return request_placement, instance_num, bandwidth, flow_matrix_request