from django.utils import timezone
from django.utils.translation import ugettext

from mediane import models
from mediane.algorithms.enumeration import get_name_from
from mediane.algorithms.lri.BioConsert import BioConsert
from mediane.algorithms.lri.ExactAlgorithm import ExactAlgorithm
from mediane.algorithms.misc.borda_count import BordaCount
from mediane.distances.KendallTauGeneralizedNlogN import KendallTauGeneralizedNlogN
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION
from mediane.median_ranking_tools import parse_ranking_with_ties_of_str, dump_ranking_with_ties_to_str
from mediane.normalizations.enumeration import NONE, UNIFICATION, PROJECTION
from mediane.normalizations.unification import Unification
from mediane.normalizations.projection import Projection
MIN_MEASURE_DURATION = 3


def execute_median_rankings_computation_from_rankings(
        rankings,
        algorithm,
        normalization,
        distance,
        precise_time_measurement,
        dataset=None,
        algorithms=None,
):
    if str(normalization) == "Unification":
        rankings_real = Unification.rankings_to_rankings(rankings)
    elif str(normalization) == "Projection":
        rankings_real = Projection.rankings_to_rankings(rankings)
    else:
        rankings_real = rankings
    if algorithms:
        return [execute_median_rankings_computation_from_rankings(
            rankings=rankings_real,
            algorithm=a,
            normalization=normalization,
            distance=distance,
            precise_time_measurement=precise_time_measurement,
            dataset=dataset,
        ) for a in algorithms]
    iteration = 1
    start_timezone = timezone.now()
    c = algorithm.compute_median_rankings(rankings=rankings_real, distance=distance)
    duration = (timezone.now() - start_timezone).total_seconds()
    while precise_time_measurement and duration < MIN_MEASURE_DURATION:
        # print(iteration, duration)
        iteration = int((iteration / duration) * MIN_MEASURE_DURATION * 1.1)
        rang_iter = range(2, iteration)
        start_timezone = timezone.now()
        for k in rang_iter:
            algorithm.compute_median_rankings(rankings=rankings_real, distance=distance)
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
        distance=KendallTauGeneralizedNlogN(distance).get_distance_to_a_set_of_rankings(
            c[0],
            rankings=rankings,
        )[distance.id_order],
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
        algorithms=None,
):

    submission_results = []
    algorithms = algorithms or []
    if algorithm is not None:
        algorithms.append(algorithm)
    for d in datasets:
        if not d.complete:
            if str(normalization) == "Unification":
                rankings_real = Unification.rankings_to_rankings(d.rankings)
            elif str(normalization) == "Projection":
                rankings_real = Projection.rankings_to_rankings(d.rankings)
            else:
                rankings_real = d.rankings
        else:
            rankings_real = d.rankings
        for a in algorithms:
            submission_results.append(
                execute_median_rankings_computation_from_rankings(
                    rankings=rankings_real,
                    algorithm=a,
                    normalization=normalization,
                    distance=distance,
                    precise_time_measurement=precise_time_measurement,
                    dataset=d,
                )
            )

    return submission_results


def create_computation_job(
        datasets,
        normalization,
        distance,
        precise_time_measurement,
        algorithms,
        owner,
):
    job = models.Job.objects.create(
        owner=owner,
        dist=distance,
        norm=normalization,
        creation=timezone.now(),
        bench=precise_time_measurement,
        identifier=None,
    )
    for d in datasets:
        for a in algorithms:
            r = models.Result.objects.create(
                algo=a,
                dataset=d,
                job=job,
            )
            r.mark_as_todo()
    job.update_task_count()
    return job



def execute_median_rankings_computation_of_result(
        result,
):
    submission_result = execute_median_rankings_computation_from_rankings(
        rankings=result.dataset.rankings,
        algorithm=result.algo.get_instance(),
        normalization=result.job.norm,
        distance=result.job.dist,
        precise_time_measurement=result.job.bench,
        dataset=result.dataset,
    )
    result.consensuses = '\n'.join([dump_ranking_with_ties_to_str(c) for c in submission_result["consensus"]])
    result.distance_value = submission_result["distance"]
    result.duration = submission_result["duration"]
    result.save()


def cleanup_dataset(rankings_as_one_str):
    rankings_as_one_str = rankings_as_one_str.replace("\r", "")
    rankings_as_one_str = rankings_as_one_str.replace("\\\n", "")
    rankings_as_one_str = rankings_as_one_str.replace(":\n", "")
    if rankings_as_one_str[-1] == ':':
        rankings_as_one_str = rankings_as_one_str[:-1]
    return rankings_as_one_str

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


def compute_consensus_settings_based_on_datasets(
        n,
        m,
        complete,
        rankings,
        user,
        dbdatasets=None,
        algos=None,
):
    """

    :param n:
    :param m:
    :param complete:
    :param rankings:
    :param user: the user for which we are find the best settings, should be used to
    not select an algorithm/distance/norm that is not visible by the user
    :param dbdatasets:
    :param algos:
    :return:
    """
    dbdatasets = [] if dbdatasets is None else dbdatasets
    algos = [] if algos is None else algos
    from mediane.models import Distance, Normalization, Algorithm
    consensus_settings = {}
    consensus_settings["algo"] = Algorithm.objects.get(key_name=str(BioConsert().get_full_name())).pk
    consensus_settings["dist"] = Distance.objects.get(key_name=GENERALIZED_KENDALL_TAU_DISTANCE_WITH_UNIFICATION).pk
    # consensus_settings["norm"] = Normalization.objects.get(key_name=NONE if complete else UNIFICATION).pk
    consensus_settings["norm"] = Normalization.objects.get(key_name=NONE).pk
    if n < 70:
        try:
            import cplex
            consensus_settings["algo"] = Algorithm.objects.get(key_name=str(ExactAlgorithm().get_full_name())).pk
        except:
            pass
    elif n > 100 or len(dbdatasets) * len(algos) > 20:
        consensus_settings["algo"] = Algorithm.objects.get(key_name=str(BordaCount().get_full_name())).pk
    # consensus_settings["auto_compute"] = n < 50 and len(dbdatasets) * len(algos) < 50
    consensus_settings["auto_compute"] = False

    consensus_settings["bench"] = False
    consensus_settings["extended_analysis"] = len(dbdatasets) * len(algos) > 50
    # print(consensus_settings)
    return consensus_settings
