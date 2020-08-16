from typing import List, Dict, Set
from random import shuffle
from numpy import asarray, ndarray, zeros, count_nonzero, vdot, array, shape, where
from igraph import Graph
from mediane.algorithms.lri.ExactAlgorithm_bis import ExactAlgorithmBis
from mediane.distances.ScoringScheme import ScoringScheme


default_scores = ScoringScheme.get_default().matrix


def generate_random_permutations_dataset(nb_elements: int, nb_rankings: int)->List[List[List[int]]]:
    initial_list = []
    for i in range(nb_elements):
        initial_list.append([i])
    rankings = []
    for i in range(nb_rankings):
        ranking = list(initial_list)
        shuffle(ranking)
        rankings.append(ranking)
    return rankings


def number_of_scc(rankings: List[List[List[int]]], scoring_scheme: List[List[float]])->int:
    return len(get_scc(rankings, scoring_scheme))


def get_scc(rankings: List[List[List[int]]], scoring_scheme=default_scores)->List:
    sizes = []
    for scc in graph_of_elements(positions(rankings), asarray(scoring_scheme)).components():
        sizes.append(len(scc))
    return sizes


def number_of_optimal_solutions(rankings: List[List[List[int]]], scoring_scheme=default_scores)->int:
    return len(ExactAlgorithmBis(scoring_scheme=scoring_scheme).compute_median_rankings(rankings, None, False))


def graph_of_elements(pos_matrix: ndarray, matrix_scoring_scheme=default_scores) -> Graph:
    weak_graph = Graph(directed=True)
    cost_before = asarray(matrix_scoring_scheme[0])
    cost_tied = asarray(matrix_scoring_scheme[1])
    cost_after = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                        cost_before[5]])
    n = shape(pos_matrix)[0]
    m = shape(pos_matrix)[1]
    for i in range(n):
        weak_graph.add_vertex(name=str(i))

    edges = []
    for e1 in range(n):
        mem = pos_matrix[e1]
        d = count_nonzero(mem == -1)
        for e2 in range(e1 + 1, n):
            a = count_nonzero(mem + pos_matrix[e2] == -2)
            b = count_nonzero(mem == pos_matrix[e2])
            c = count_nonzero(pos_matrix[e2] == -1)
            e = count_nonzero(mem < pos_matrix[e2])
            relative_positions = array([e - d + a, m - e - b - c + a, b - a, c - a, d - a, a])
            put_before = vdot(relative_positions, cost_before)
            put_after = vdot(relative_positions, cost_after)
            put_tied = vdot(relative_positions, cost_tied)
            if put_before > put_after or put_before > put_tied:
                edges.append((e2, e1))
            if put_after > put_before or put_after > put_tied:
                edges.append((e1, e2))
    weak_graph.add_edges(edges)
    return weak_graph


def only_one_topological_sort(g: Graph)->bool:
    cfcs = g.components()
    edges = []
    for i in range(len(cfcs)):
        cfc1 = cfcs[i]
        for j in range(i+1, len(cfcs)):
            connected = False
            for elem1 in cfc1:
                if connected:
                    break
                for elem2 in cfcs[j]:
                    if g.are_connected(elem1, elem2):
                        edges.append((i, j))
                        connected = True
                        break
    nb_vertex_g2 = len(cfcs)
    cfc_graph = Graph(directed=True)
    cfc_graph.add_vertices(nb_vertex_g2)
    cfc_graph.add_edges(edges)
    only_one = True
    while nb_vertex_g2 > 1 and only_one:
        deg = where(asarray(cfc_graph.indegree()) == 0)[0]
        if len(deg) > 1:
            only_one = False
        else:
            cfc_graph.delete_vertices(deg[0])
        nb_vertex_g2 -= 1
    return only_one


def positions(rankings: List[List[List[int]]]) -> ndarray:
    elem_id = {}
    id_elem = 0
    for ranking in rankings:
        for bucket in ranking:
            for element in bucket:
                if element not in elem_id:
                    elem_id[element] = id_elem
                    id_elem += 1
    pos_matrix = zeros((len(elem_id), len(rankings)), dtype=int) - 1
    id_ranking = 0
    # print("debut positions")
    for ranking in rankings:
        id_bucket = 0
        for bucket in ranking:
            for element in bucket:
                pos_matrix[elem_id.get(element)][id_ranking] = id_bucket
            id_bucket += 1
        id_ranking += 1
    # print("fin positions")

    return pos_matrix


def find_dataset(nb_elem: int, nb_rankings: int, min_opt=None, max_opt=None, min_scc=None, max_scc=None, size_scc=None,
                 max_tries=None, number_of_results=1)->Set[List[List[List[int]]]]:
    scores = default_scores
    memoi = []
    tries = 0
    algo = ExactAlgorithmBis(scoring_scheme=scores)
    datasets_found = set()
    dataset_found_dict = []
    while (len(datasets_found) < number_of_results) and (max_tries is None or tries <= max_tries):
        rankings_random = generate_random_permutations_dataset(nb_elem, nb_rankings)
        rankings = rename_dataset(rankings_random, rankings_random[0])
        if is_rankings_new(rankings, dataset_found_dict):
            conditions_on_scc = True
            conditions_on_opt_solutions = True
            medianes = None
            gr = None
            if min_scc is not None or max_scc is not None or size_scc is not None:
                gr = graph_of_elements(positions(rankings))
                scc = gr.components()
                if not((size_scc is None or size_scc == scc) and
                        (min_scc is None or min_scc <= len(scc)) and
                        (max_scc is None or len(scc) <= max_scc)):
                    conditions_on_scc = False
            if conditions_on_scc and (min_opt is not None or max_opt is not None):
                if max_opt == 1:
                    if gr is None:
                        gr = graph_of_elements(positions(rankings))
                    unique_topol = only_one_topological_sort(gr)
                    if not unique_topol:
                        conditions_on_opt_solutions = False
                if conditions_on_opt_solutions:
                    medianes = algo.compute_median_rankings(rankings, None, False)
                    nb_opt = len(medianes)
                    print(len(medianes), " medianes")
                    if nb_opt == 2:
                        print("rankings")
                        print(rankings)
                        print("medianes")
                        print(medianes)
                    if not ((min_opt is None or min_opt <= nb_opt) and (max_opt is None or nb_opt <= max_opt)):
                        conditions_on_opt_solutions = False
            if conditions_on_scc and conditions_on_opt_solutions:
                if medianes is None:
                    datasets_found.add(str(rankings))
                    dataset_found_dict.append(hash_rankings(rankings))
                else:
                    final_dataset = rename_dataset(rankings, medianes[0])
                    datasets_found.add(str(final_dataset))
                    dataset_found_dict.append(hash_rankings(final_dataset))
            memoi.append(hash_rankings(rankings))

    return datasets_found


def hash_rankings(rankings: List[List[List[int]]])->Dict[str, int]:
    hash_mult = {}
    for ranking in rankings:
        ranking_st = str(ranking)
        if ranking_st not in hash_mult:
            hash_mult[ranking_st] = 1
        else:
            hash_mult[ranking_st] += 1
    return hash_mult


def is_rankings_new(rankings: List[List[List[int]]], already_found: List[Dict])->bool:
    dict_view = hash_rankings(rankings)
    for already_done in already_found:
        if already_done == dict_view:
            return False
    return True


def rename_dataset(rankings: List[List[List[int]]], ranking_rererence: List[List[int]]):
    h_rename = {}
    id_elem = 1
    for bucket in ranking_rererence:
        h_rename[bucket[0]] = id_elem
        id_elem += 1
    res_rename = []
    for ranking in rankings:
        ranking_rename = []
        for bucket in ranking:
            bucket_rename = []
            for elem in bucket:
                bucket_rename.append(h_rename[elem])
            ranking_rename.append(bucket_rename)
        res_rename.append(ranking_rename)
    return res_rename

import os
from ast import literal_eval
n1 = 17
m1 = 11

for i1 in [15, 16]:
    print("i = ", i1)
    all_datasets = find_dataset(n1, m1, min_scc=i1, max_scc=i1, max_opt=1, number_of_results=5)
    print(all_datasets)
    os.mkdir("/home/pierre/Bureau/Cecile/cfc"+str(i1))
    cpt = 1
    for dataset in all_datasets:
        f = open("/home/pierre/Bureau/Cecile/cfc"+str(i1)+"/jdd"+str(cpt), "w")
        ras = literal_eval(dataset)

        for ranki in ras:
            f.write(str(ranki))
            f.write("\n")
        cpt += 1
        f.close()

# ranki = [[[3], [1], [2], [4]], [[3], [2], [1], [4]]]
# print(only_one_topological_sort(graph_of_elements(positions(ranki))))
