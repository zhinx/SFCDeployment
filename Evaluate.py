#!/usr/bin/python
# -*- coding: utf-8 -*-

import NetworkInfo as ni
import DeployAlgorithm
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import Global


def evaluate(node_list, bandwidth, rest_bandwidth, node_pos, request_placement, instance_num, flow_matrix_request, request_list):

    """ 部署结果评估，返回总带宽消耗和实例使用量 """

    G = nx.DiGraph()
    for i in range(len(rest_bandwidth)):
        for j in range(len(rest_bandwidth)):
            if rest_bandwidth[i][j] > 0:
                G.add_edge(i, j, capacity=rest_bandwidth[i][j], weight=1)
    pos = node_pos

    # edge_color = []
    edge_labels = {}
    for (i, j) in G.edges():
        # edge_color.append(G[i][j]["capacity"])
        edge_labels[(i, j)] = G[i][j]["capacity"]

    # 带宽消耗
    band_cost = (np.mat(bandwidth) - np.mat(rest_bandwidth)).sum()
    instance_cost = 0

    # 结果输出
    print "======== Deploy Complete ========"

    for i in range(len(request_placement)):
        r = request_list[i]
        nf_instance_num = {}
        print "Request " + str(r.id) + ":"
        print "\tSrc: " + str(r.src)
        print "\tDst: " + str(r.dst)
        print "\tRate: " + str(r.rate)
        print "\tAvailability Request: " + str(r.avail)
        print "\tNF List: " + str(r.nf_list)
        for j, nf in enumerate(r.nf_list):
            nf_instance_num[nf] = len(request_placement[i][j].keys())
            print "\t\tNF " + str(nf) + " (" + str(nf_instance_num[nf]) + "): " + str(request_placement[i][j].keys())
        print "\tBandwidth Cost: " + str(np.mat(flow_matrix_request[i]).sum())
        instance_cost_request = sum(map(lambda (k, v): v * Global.NF_INSTANCE_STATE_COST[k], nf_instance_num.items()))
        instance_cost += instance_cost_request
        print "\tInstance State Cost: " + str(instance_cost_request) + "\n"

    print "-------- Deploy Info --------"
    print "Total Bandwidth Cost: " + str(band_cost)
    print "Total Instance State Cost: " + str(instance_cost)
    print "Total Instances Used: "
    for i in range(len(instance_num)):
        print "\tNF " + str(i) + ": " + str(instance_num[i])

    # 绘图
    nx.draw_networkx_nodes(G, pos=pos, node_color=[node_list[i].CPU / float(node_list[i].CPU_max) for i in range(len(node_list))], cmap=plt.cm.Reds_r)
    nx.draw_networkx_labels(G, pos=pos)
    nx.draw_networkx_edges(G, pos=pos, alpha=0.4, width=1.5, arrows=False)
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels, font_size=10, label_pos=0.2, bbox=dict(facecolor='white', edgecolor='None', alpha=0.65))

    plt.show()

    return band_cost, instance_cost
