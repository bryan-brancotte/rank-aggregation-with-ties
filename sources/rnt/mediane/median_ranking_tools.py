from typing import Callable, List, TypeVar

T = TypeVar('T')


def parse_ranking_with_ties(ranking: str, converter: Callable[[str], T]) -> List[List[T]]:
    ret = []
    st = ranking.find('[') + 1
    en = ranking.find(']')
    while st != -1 and en != -1:
        bucket = []
        for s in ranking[st + 1:  en].split(","):
            bucket.append(converter(s.strip()))
        ret.append(bucket)
        st = ranking.find('[', en + 1)
        en = ranking.find(']', st + 1)
    return ret


def parse_ranking_with_ties_of_str(ranking: str) -> List[List[str]]:
    return parse_ranking_with_ties(
        ranking=ranking,
        converter=lambda x: x
    )


def parse_ranking_with_ties_of_int(ranking: str) -> List[List[int]]:
    return parse_ranking_with_ties(
        ranking=ranking,
        converter=lambda x: int(x)
    )
