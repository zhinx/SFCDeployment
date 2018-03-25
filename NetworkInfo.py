#!/usr/bin/python
# -*- coding: utf-8 -*-

import Global


class Node(object):
    # 物理机资源
    id = 0
    CPU = 0
    CPU_max = 0
    avail = 0
    instances = []

    def __init__(self, id, CPU, avail):
        self.id = id
        self.CPU = CPU
        self.CPU_max = CPU
        self.avail = avail
        self.instances = []


class Request(object):
    # 请求
    id = 0
    src = 0
    dst = 0
    nf_list = []
    rate = 0
    avail = 0
    rank = 0

    def __init__(self, id, src, dst, nf_list, rate, avail):
        self.id = id
        self.src = src
        self.dst = dst
        self.nf_list = nf_list
        self.rate = rate
        self.avail = avail


class Instance(object):
    # NF 实例
    id = 0
    # NF种类
    type = 0
    cpu_requirement = 0
    capacity = 0
    # 部署在哪个节点
    placement = 0
    # 分配给每个请求多少处理能力 eg. {0: 12, 1: 6} 分别给0和1号请求分配12和6单位的处理能力，为0则不分配
    assignment = {}

    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.cpu_requirement = Global.NF_CPU_REQUIREMENT[type]
        self.capacity = Global.NF_CAPACITY[type]
        self.assignment = {}
