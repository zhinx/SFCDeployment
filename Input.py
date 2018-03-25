#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import numpy as np
import NetworkInfo as ni
import random
import Global


def data_init(nodes_file, matrix_file):

    """ 从文件读入网络数据 """

    # 读取节点信息
    node_list = []
    node_name = {}
    node_pos = {}

    with open(nodes_file) as fn:
        reader = csv.reader(fn)
        next(reader)
        for i, line in enumerate(reader):
            node_name[line[0]] = i
            node_list.append(ni.Node(i, int(line[3]), float(line[4])))
            node_pos[i] = np.array([float(line[1]), float(line[2])])

    # 读取网络信息
    bandwidth = [[0 for col in range(len(node_name))] for row in range(len(node_name))]
    adj = [[0 for col in range(len(node_name))] for row in range(len(node_name))]

    with open(matrix_file) as fm:
        reader = csv.reader(fm)
        next(reader)
        for i, line in enumerate(reader):
            bandwidth[node_name[line[1]]][node_name[line[2]]] = int(line[3])
            bandwidth[node_name[line[2]]][node_name[line[1]]] = int(line[3])
            adj[node_name[line[1]]][node_name[line[2]]] = 1
            adj[node_name[line[2]]][node_name[line[1]]] = 1

    return node_list, bandwidth, adj, node_pos


def get_requests(request_num, nf_list_length, rate, avail):

    """ 随机生成请求集合 """

    request_list = []

    src_list = [1, 34, 37, 31, 3, 11, 8, 40, 32]
    dst_list = [36, 48, 0, 29, 28, 46, 24, 38]

    for i in range(request_num):
        r = ni.Request(i, random.choice(src_list), random.choice(dst_list),
                       random.sample(range(Global.NF_TYPE_NUM), random.randint(nf_list_length[0], nf_list_length[1])),
                       random.randint(rate[0], rate[1]), random.uniform(avail[0], avail[1]))
        request_list.append(r)

    return request_list


if __name__ == "__main__":
    nodes_file = "./nodes.csv"
    matrix_file = "./network_matrix.csv"
    node_list, bandwidth, adj = data_init(nodes_file, matrix_file)
