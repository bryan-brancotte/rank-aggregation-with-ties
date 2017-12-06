from django.utils import timezone

from mediane.distances.KendallTauGeneralizedNSquare import KendallTauGeneralizedNSquare
from mediane.distances.enumeration import GENERALIZED_KENDALL_TAU_DISTANCE


def compute_median_rankings(
        rankings,
        algorithm,
        normalization,
        distance,
        precise_time_measurement,
):
    instance = algorithm()
    iteration = 1
    c = None
    duration = 0
    start_timezone = timezone.now()
    c = instance.compute_median_rankings(rankings=rankings)
    duration = (timezone.now() - start_timezone).total_seconds()
    while precise_time_measurement and duration < 2:
        # print(iteration, duration)
        iteration = int(iteration / duration * 2.2)
        rang_iter = range(2, iteration)
        start_timezone = timezone.now()
        for k in rang_iter:
            instance.compute_median_rankings(rankings=rankings)
        duration = (timezone.now() - start_timezone).total_seconds()

    return dict(
        consensus=c,
        distance=KendallTauGeneralizedNSquare().get_distance_to_a_set_of_rankings(
            c[0],
            rankings=rankings,
        )[GENERALIZED_KENDALL_TAU_DISTANCE],
        duration=(int(duration / iteration * 1000.0 * 1000.0 * 1000.0)) / 1000.0 / 1000.0,
    )
