from mediane.algorithms.misc.borda_count import BordaCount
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE
from mediane.median_ranking_tools import parse_ranking_with_ties_of_str
from mediane.normalizations.enumeration import UNIFICATION, NONE


def evaluate_dataset_and_provide_stats(rankings_str):
    evaluation = {}
    elements = set()
    rankings = []
    complet = True
    invalid_rankings = {}
    cpt = -1
    tailles = set()
    for ranking_str in rankings_str:
        cpt += 1
        try:
            ranking = parse_ranking_with_ties_of_str(ranking_str)
        except ValueError as e:
            invalid_rankings[cpt] = e.args if len(e.args) > 1 else e.args[0]
            ranking = []
        rankings.append(ranking)
        ranking_elements = set()
        for bucket in ranking:
            for element in bucket:
                ranking_elements.add(element)
                elements.add(element)
                tailles.add(len(ranking_elements))
        if ranking_elements != elements or len(tailles) > 1:
            complet = False
    evaluation["complete"] = complet
    evaluation["n"] = len(elements)
    evaluation["m"] = len(rankings)
    evaluation["invalid"] = len(invalid_rankings) > 0
    evaluation["invalid_rankings_id"] = invalid_rankings
    evaluation["rankings"] = rankings

    return evaluation


def compute_consensus_settings_based_on_datasets(n, m, complete, rankings):
    consensus_settings = {}
    if n > 200 or True:
        consensus_settings["algo"] = BordaCount().get_full_name()
        consensus_settings["dist"] = GENERALIZED_KENDALL_TAU_DISTANCE
        consensus_settings["norm"] = NONE if complete else UNIFICATION
    consensus_settings["auto-compute"] = n < 50
    return consensus_settings
