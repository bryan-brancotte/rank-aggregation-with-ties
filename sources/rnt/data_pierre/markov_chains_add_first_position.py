from typing import Set, List, Dict
from os import listdir, mkdir
from random import randint, seed
import numpy as np
from median_ranking_tools import get_rankings_from_file


def add_left(ranking: np.ndarray, elem: int):
    # id of bucket of elem
    bucket_elem = ranking[elem]
    # if elem alone in its bucket: nothing to do. Otherwise
    # all the elements placed after or tied with elem have their bucket id +1
    if np.sum(ranking == bucket_elem) > 1:
        ranking[ranking >= bucket_elem] += 1
        ranking[elem] = bucket_elem


def add_right(ranking: np.ndarray, elem: int):
    # id of bucket of elem
    bucket_elem = ranking[elem]
    # if a most two elements in the bucket of elem: nothing to do. Otherwise
    # all the elements placed afterelem have their bucket id +1, same for elem
    if np.sum(ranking == bucket_elem) > 2:
        ranking[ranking > bucket_elem] += 1
        ranking[elem] = bucket_elem + 1


def change_left(ranking: np.ndarray, elem: int):
    bucket_elem = ranking[elem]
    size_bucket_elem = np.sum(ranking == bucket_elem)
    if bucket_elem != 0:
        if size_bucket_elem == 1:
            ranking[ranking > bucket_elem] -= 1
        ranking[elem] -= 1


def change_right(ranking: np.ndarray, elem: int):
    bucket_elem = ranking[elem]
    size_bucket_elem = np.sum(ranking == bucket_elem)
    size_bucket_following = np.sum(ranking == bucket_elem+1)
    id_last_bucket = np.max(ranking)
    if bucket_elem != id_last_bucket and (size_bucket_elem > 1 or size_bucket_following > 1):
        ranking[elem] += 1
        if size_bucket_elem == 1:
            ranking[ranking > bucket_elem] -= 1


def remove_element(ranking: np.ndarray, elem: int):
    # id of bucket of elem
    bucket_elem = ranking[elem]
    size_bucket_elem = np.sum(ranking == bucket_elem)
    if size_bucket_elem == 1:
        ranking[ranking > bucket_elem] -= 1

    ranking[elem] = -1


def put_element_end(ranking: np.ndarray, elem: int):
    ranking[elem] = np.max(ranking) + 1


def step_element_incomplete(ranking: np.ndarray, elem: int, missing_elements: Set):
    alea = randint(1, 5)
    if elem in missing_elements:
        if alea == 5:
            put_element_end(ranking, elem)
            missing_elements.remove(elem)
    else:
        if alea == 1:
            add_left(ranking, elem)
        elif alea == 2:
            add_right(ranking, elem)

        elif alea == 3:
            change_left(ranking, elem)

        elif alea == 4:
            change_right(ranking, elem)

        elif alea == 5:
            remove_element(ranking, elem)
            missing_elements.add(elem)


def change_ranking_complete(ranking: np.ndarray, steps: int, nb_elements: int):
    for step in range(steps):
        step_element_complete(ranking, randint(0, nb_elements-1))


def step_element_complete(ranking: np.ndarray, elem: int):
    alea = randint(1, 4)
    if alea == 1:
        add_left(ranking, elem)
    elif alea == 2:
        add_right(ranking, elem)

    elif alea == 3:
        change_left(ranking, elem)

    elif alea == 4:
        change_right(ranking, elem)


def change_ranking_incomplete(ranking: np.ndarray, steps: int, nb_elements: int, missing_elements: Set):
    for step in range(steps):
        step_element_incomplete(ranking, randint(0, nb_elements-1), missing_elements)


def create_file(nb_elements: int, nb_rankings: int, steps: int, rankings: List):
    folder = "/home/pierre/Bureau/Doctorat/Datasets/steps_bis/datasets_steps/"
    features = "n="+str(nb_elements)+"_m="+str(nb_rankings)+"_steps="+str(steps)+"_id="
    id_file = 0
    for fichier in listdir(folder):
        if features in fichier:
            id_file += 1
    output = open(folder+features+str(id_file), "w")
    for ranking in rankings:
        output.write(str(ranking))
        output.write("\n")
    output.close()


def create_dataset(nb_elements: int, nb_rankings: int, steps: int, complete=False):
    rankings_list = []

    rankings = np.zeros((nb_rankings, nb_elements), dtype=int)
    for i in range(nb_rankings):
        rankings[i] = np.arange(nb_elements)
    for ranking in rankings:
        missing_elements = set()
        if not complete:
            change_ranking_incomplete(ranking, steps, nb_elements, missing_elements)
        else:
            change_ranking_complete(ranking, steps, nb_elements)
        ranking_list = []
        nb_buckets = np.max(ranking)+1
        for i in range(nb_buckets):
            ranking_list.append([])
        for elem in range(nb_elements):
            bucket_elem = ranking[elem]
            if bucket_elem >= 0:
                ranking_list[bucket_elem].append(elem)
        if len(ranking_list) > 0:
            rankings_list.append(ranking_list)
    return rankings_list


def create_dataset_from_rankings(rankings: List[List[List[int]]], steps: int, complete=False):
        rankings_list = []
        h_elem_id = {}
        h_id_elem = {}

        cpt_elem = 0
        for ranking in rankings:
            for bucket in ranking:
                for elem in bucket:
                    if elem not in h_elem_id:
                        h_elem_id[elem] = cpt_elem
                        h_id_elem[cpt_elem] = elem
                        cpt_elem += 1

        nb_elem = len(h_elem_id)
        rankings = get_positions(rankings, h_elem_id).transpose()

        for ranking in rankings:
            missing_elements = set(np.where(ranking == -1)[0])
            if not complete:
                change_ranking_incomplete(ranking, steps, nb_elem, missing_elements)
            else:
                change_ranking_complete(ranking, steps, nb_elem)
            ranking_list = []
            nb_buckets = np.max(ranking) + 1
            for i in range(nb_buckets):
                ranking_list.append([])
            for elem in range(nb_elem):
                bucket_elem = ranking[elem]
                if bucket_elem >= 0:
                    ranking_list[bucket_elem].append(h_id_elem.get(elem))
            if len(ranking_list) > 0:
                rankings_list.append(ranking_list)
        return rankings_list


def get_positions(rankings: List[List[List[int]]], elements_id: Dict) -> np.ndarray:
        positions = np.zeros((len(elements_id), len(rankings)), dtype=int) - 1
        id_ranking = 0
        # print("debut positions")
        for ranking in rankings:
            id_bucket = 0
            for bucket in ranking:
                for element in bucket:
                    positions[elements_id.get(element)][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1
        # print("fin positions")

        return positions
    # create_file(nb_elements, nb_rankings, steps, rankings_list)


# seed(1)
# res = create_dataset(nb_elements=300, nb_rankings=20, steps=1000000, complete=True)
# for re in res:
#    print(re)
# for step_wanted in [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 200000, 500000]:
#    print(step_wanted)
#    for repet in range(10):
#        # create_dataset(nb_elements=50, nb_rankings=10, steps=steps_wanted)
#        create_dataset(nb_elements=35, nb_rankings=11, steps=step_wanted)


seed(1)
path = "/home/pierre/Bureau/Doctorat/Datasets/notes_syn_2/steps/"

for id_jdd in range(1, 101):
    print(id_jdd)
    id_output = "dat" + '{0:03}'.format(id_jdd)
    for st in range(100, 5001, 100):
        old_rankings = get_rankings_from_file(path + "step"+str(st-100)+"/jdd_classements/" + id_output)

        new_rankings = create_dataset_from_rankings(rankings=old_rankings, steps=100, complete=False)

        f = open(path + "step"+str(st)+"/jdd_classements/" + id_output, "w")
        for ranking_new in new_rankings:
            f.write(str(ranking_new))
            f.write("\n")
        f.close()

