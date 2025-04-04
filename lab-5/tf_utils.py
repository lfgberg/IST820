import glob
import pickle
import numpy as np
import config
import os
import random
import json
from shutil import copyfile, rmtree
from sklearn.model_selection import train_test_split
import subprocess
import networkx as nx
from binary2image import getGreyScaleImage, getRGBImage

# from binary2cfg import get_CFG


def split():
    # b = glob.glob('data/CFG_hex/Benign/*')
    # v = glob.glob('data/CFG_hex/Virus/*')
    b = glob.glob("data/binary/Benign/*")
    v = glob.glob("data/binary/Virus/*")
    idx = list(range(len(b + v)))
    lbs = [config.benign_label] * int(len(b))
    lbs.extend([config.malware_label] * int(len(v)))
    k = train_test_split(idx, lbs, test_size=0.2)
    print(len(k[2]), np.sum(np.array(k[2]) == 0), np.sum(np.array(k[2]) == 1))
    print(len(k[3]), np.sum(np.array(k[3]) == 0), np.sum(np.array(k[3]) == 1))
    with open(config.CFG_split_data, "wb") as jf:
        pickle.dump(k, jf)


def check_distribution(fns, ns=None):
    lbs = []
    for f in fns:
        if ns != None:
            lbs.append(
                config.malware_label
                if ns[f].find("Virus") != -1
                else config.benign_label
            )
        else:
            lbs.append(
                config.malware_label if f.find("Virus") != -1 else config.benign_label
            )

    print(len(lbs), np.sum(np.array(lbs) == 0), np.sum(np.array(lbs) == 1))
    return lbs


def count_dims():
    max_features = 0
    max_nodes = 0
    files = glob.glob("data/CFG_hex/Virus/*") + glob.glob("data/CFG_hex/Benign/*")
    for f in files:
        with open(f, "r") as jf:
            strs = json.load(jf)
            max_nodes = max(max_nodes, len(strs["nodes"]))
            for node in strs["nodes"]:
                if node["vector"] != None:
                    b = bytearray.fromhex(node["vector"])
                    uint8 = []
                    for i in range(len(b)):
                        uint8.append(b[i])
                    max_features = max(max_features, len(uint8))
    print("rnn config.max_features = ", max_features)


class GNNGraph(object):
    def __init__(self, g, label, node_features=None):
        self.num_nodes = g.number_of_nodes()  #
        self.label = label  #
        self.node_features = node_features  #
        self.degrees = list(dict(g.degree()).values())  #
        self.edges = list(g.edges)  #


def Graphdata():
    files = glob.glob("data/CFG_hex/Virus/*") + glob.glob("data/CFG_hex/Benign/*")
    g_list = []
    for f in files:
        with open(f, "r") as jf:
            strs = json.load(jf)
            g = nx.Graph()
            node_features = []
            n_edges = 0
            block_id = {}
            for idx, node in enumerate(strs["nodes"]):
                block_id[node["id"]] = idx
                g.add_node(idx)
                uint8 = []
                if node["vector"] != None:
                    b = bytearray.fromhex(node["vector"])
                    for i in range(len(b)):
                        uint8.append(b[i])
                uint8.extend([config.max_features] * (config.feature_dim - len(uint8)))
                node_features.append(uint8)
            for link in strs["links"]:
                g.add_edge(block_id[link["source"]], block_id[link["target"]])
            node_features = np.stack(node_features)
            g_list.append(
                GNNGraph(
                    g,
                    (
                        config.malware_label
                        if f.find("Virus") != -1
                        else config.benign_label
                    ),
                    node_features,
                )
            )
    with open(config.graph_data, "wb") as jf:
        pickle.dump(g_list, jf)


if __name__ == "__main__":
    count_dims()
    split()
    Graphdata()
