from django.utils import timezone
from django.utils.translation import ugettext

from mediane.algorithms.enumeration import get_name_from
from mediane.distances.KendallTauGeneralizedNSquare import KendallTauGeneralizedNSquare
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE

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
