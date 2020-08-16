from random import shuffle


def generate_random_permutations_dataset(nb_elements: int, nb_rankings: int):
    initial_list = list(range(1, nb_elements+1))
    rankings = []
    for i in range(nb_rankings):
        ranking = list(initial_list)
        shuffle(ranking)
        rankings.append(ranking)
    return rankings

