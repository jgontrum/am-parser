#
# Copyright (c) 2020 Saarland University.
#
# This file is part of AM Parser
# (see https://github.com/coli-saar/am-parser/).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import sys
import json
import collections

from edge_to_irtg import edge2irtg
from get_edges_from_mrp import get_id2lex, get_mrp_edges
from convert_irtg_to_mrp import get_edges, get_input, get_mrp_edges, get_nodes, get_tops, irtg2mrp
from eliminate_h_top import eliminate_h
from a_star_mrp import *
from process_c import *


labels = 'L LR LA H P S A C N D T E R F G Q U'.split()
priority_dict = {label:index for (index, label) in enumerate(labels)}
non_deducible = ["id", "flavour", "framework", "version", "time"]
mrp_data_path = sys.argv[1]
companion_data = json.load(open(sys.argv[2], 'r', encoding = 'utf8'))
outdir = sys.argv[3]

def update_id_labels(edge_dict, label_dict):
    for (u,v) in edge_dict.keys():
        if type(u) == str:
            label_dict[u] = u
        elif u - 1111 >= 0:
            if int(str(u)[:-4]) in label_dict.keys():
                label_dict[u] = label_dict[int(str(u)[:-4])]
            else: label_dict[u] = 'Non-Terminal'
    nodes_in_edge_dict = list(set([node for edge in edge_dict.keys() for node in edge]))
    label_dict_nodes = list(label_dict.keys())
    for edge in edge_dict.keys():
        for node in edge:
            if node not in label_dict.keys():
                label_dict[node] = 'Non-Terminal'
    return label_dict


with open(mrp_data_path,encoding='utf8', errors='ignore') as infile:
    counter = 0
    for line in infile:
        #print(line)
        mrp_dict = json.loads(line)
        id = mrp_dict["id"]
        print(id)
        edges = get_mrp_edges(mrp_dict, get_remote = True)
        edges = eliminate_h(edges)
        labels = get_id2lex(mrp_dict)
        compressed_edges = compress_c_edge(edges)
        compressed_labels = update_id_labels(compressed_edges, labels)
        irtg_format_compressed = edge2irtg(compressed_edges, labels)
        print(irtg_format_compressed)
        node_tokens = node_to_token_index(companion_data, mrp_dict, compressed_labels, id)
        #print(companion_data)
        #print(compressed_labels)
        #print(node_tokens)
        alignments = align(compressed_edges, priority_dict, mrp_dict, node_tokens, compressed_labels)
