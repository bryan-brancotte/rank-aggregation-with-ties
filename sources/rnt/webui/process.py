from mediane.median_ranking_tools import parse_ranking_with_ties_of_str


def evaluate_dataset_and_provide_stats_and_settings_for_consensus(rankings_str):
    evaluation = {}
    elements = set()
    rankings = []
    complet = True
    invalid_rankings = []
    cpt = -1
    for ranking_str in rankings_str:
        cpt += 1
        try:
            ranking = parse_ranking_with_ties_of_str(ranking_str)
        except ValueError:
            invalid_rankings.append(cpt)
            ranking = []
        rankings.append(ranking)
        ranking_elements = set()
        print(ranking)
        for bucket in ranking:
            for element in bucket:
                ranking_elements.add(element)
                elements.add(element)
        if ranking_elements != elements:
            complet = False
    evaluation["complet"] = complet
    evaluation["n"] = len(elements)
    evaluation["m"] = len(rankings)
    evaluation["invalid"] = len(invalid_rankings) > 0
    evaluation["invalid_rankings"] = invalid_rankings

    return evaluation
