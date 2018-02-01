from django.utils import timezone
from django.utils.translation import ugettext

from mediane.algorithms.enumeration import get_name_from
from mediane.algorithms.misc.borda_count import BordaCount
from mediane.distances.KendallTauGeneralizedNSquare import KendallTauGeneralizedNSquare
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE
from mediane.median_ranking_tools import parse_ranking_with_ties_of_str
from mediane.normalizations.enumeration import NONE, UNIFICATION

MIN_MEASURE_DURATION = 3


def execute_median_rankings_computation_from_rankings(
        rankings,
        algorithm,
        normalization,
        distance,
        precise_time_measurement,
        dataset=None,
):
    iteration = 1
    start_timezone = timezone.now()
    c = algorithm.compute_median_rankings(rankings=rankings)
    duration = (timezone.now() - start_timezone).total_seconds()
    while precise_time_measurement and duration < MIN_MEASURE_DURATION:
        # print(iteration, duration)
        iteration = int((iteration / duration) * MIN_MEASURE_DURATION * 1.1)
        rang_iter = range(2, iteration)
        start_timezone = timezone.now()
        for k in rang_iter:
            algorithm.compute_median_rankings(rankings=rankings)
        duration = (timezone.now() - start_timezone).total_seconds()

    return dict(
        dataset=dict(
            id=-1,
            name=ugettext('typed'),
        ) if dataset is None else
        dict(
            id=dataset.id,
            name=str(dataset),
        ),
        consensus=c,
        distance=KendallTauGeneralizedNSquare().get_distance_to_a_set_of_rankings(
            c[0],
            rankings=rankings,
        )[GENERALIZED_KENDALL_TAU_DISTANCE],
        duration=(int(duration / iteration * 1000.0 * 1000.0 * 1000.0)) / 1000.0 / 1000.0,
        algo=dict(
            id=algorithm.get_full_name(),
            name=str(get_name_from(algorithm.get_full_name())),
        ),
    )


def execute_median_rankings_computation_from_datasets(
        datasets,
        algorithm,
        normalization,
        distance,
        precise_time_measurement,
):
    submission_results = []
    for d in datasets:
        submission_results.append(
            execute_median_rankings_computation_from_rankings(
                rankings=d.rankings,
                algorithm=algorithm,
                normalization=normalization,
                distance=distance,
                precise_time_measurement=precise_time_measurement,
                dataset=d,
            )
        )

    return submission_results


def evaluate_dataset_and_provide_stats(rankings_str):
    evaluation = {}
    elements = None
    rankings = []
    complete = True
    invalid_rankings = {}
    cpt = -1
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
                if element in ranking_elements:
                    invalid_rankings[cpt] = "Duplicated element '%s'" % element
                ranking_elements.add(element)
        if elements is None:
            elements = ranking_elements
        if ranking_elements != elements:
            complete = False
            elements.update(ranking_elements)
    evaluation["complete"] = complete
    evaluation["n"] = len(elements)
    evaluation["m"] = len(rankings)
    evaluation["invalid"] = len(invalid_rankings) > 0
    evaluation["invalid_rankings_id"] = invalid_rankings
    evaluation["rankings"] = rankings

    return evaluation


def compute_consensus_settings_based_on_datasets(n, m, complete, rankings, user):
    """

    :param n:
    :param m:
    :param complete:
    :param rankings:
    :param user: the user for which we are find the best settings, should be used to
    not select an algorithm/distance/norm that is not visible by the user
    :return:
    """
    from mediane.models import Distance
    consensus_settings = {}
    if n > 200 or True:
        consensus_settings["algo"] = BordaCount().get_full_name()
        consensus_settings["dist"] = Distance.objects.get(key_name=GENERALIZED_KENDALL_TAU_DISTANCE).pk
        consensus_settings["norm"] = NONE if complete else UNIFICATION
    consensus_settings["auto-compute"] = n < 50
    return consensus_settings
