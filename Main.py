#!/usr/bin/python
# -*- coding: utf-8 -*-

from algorithm import ExtendAlgorithm
from algorithm import RandomAlgorithm
from algorithm import VNEAlgorithm
import Input
import Evaluate

""" 输入 """
nodes_file = "./resources/nodes.csv"
matrix_file = "./resources/network_matrix.csv"
node_list, bandwidth, adj, node_pos = Input.data_init(nodes_file, matrix_file)
# node_list_origin, bandwidth_origin, adj_origin, node_pos = Input.data_init(nodes_file, matrix_file)


""" 单轮实验 """

# request_list = [ni.Request(0, 45, 3, [1, 2, 3], 50, 0.995), ni.Request(1, 1, 38, [2, 3], 50, 0.995)]
request_list = Input.get_requests(5, [2, 4], [20, 50], [0.9, 0.99])


""" 部署 """
band_cost, instance_cost = Evaluate.evaluate(node_list, bandwidth, node_pos, request_list,
                                             ExtendAlgorithm.extend_deploy(bandwidth, node_list, request_list))

band_cost, instance_cost = Evaluate.evaluate(node_list, bandwidth, node_pos, request_list,
                                             RandomAlgorithm.random_deploy(bandwidth, node_list, request_list))

band_cost, instance_cost = Evaluate.evaluate(node_list, bandwidth, node_pos, request_list,
                                             VNEAlgorithm.vne_deploy(bandwidth, node_list, request_list))


""" 多轮实验 """

# band_cost_list = []
# instance_cost_list = []
#
# for i in range(10):
#     node_list = copy.deepcopy(node_list_origin)
#     bandwidth = copy.deepcopy(bandwidth_origin)
#     request_list = Input.get_requests(5, [2, 3], [55, 55], [0.999, 0.9995])
#
#     print "Deploy Round: " + str(i)
#     request_placement, instance_registry, instance_num, rest_bandwidth, flow_matrix_request = DeployAlgorithm.greedy_deploy(bandwidth, node_list, request_list)
#     band_cost, instance_cost = Evaluate.evaluate(node_list, bandwidth, rest_bandwidth, node_pos, request_placement, instance_num, flow_matrix_request, request_list)
#
#     band_cost_list.append(band_cost)
#     instance_cost_list.append(instance_cost)
#
# print "Average Bandwidth Cost: " + str(sum(band_cost_list) / float(len(band_cost_list)))
# print "Average Instance State Cost: " + str(sum(instance_cost_list) / float(len(instance_cost_list)))
