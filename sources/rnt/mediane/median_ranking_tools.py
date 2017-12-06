from typing import Callable, List, TypeVar

T = TypeVar('T')


def parse_ranking_with_ties(ranking: str, converter: Callable[[str], T]) -> List[List[T]]:
    ranking = ranking.strip()
    ret = []
    st = ranking.find('[', ranking.find('[') + 1)
    en = ranking.find(']')
    ranking_end = ranking.rfind(']')
    old_en = en
    if ranking[ranking_end + 1:] != "":
        raise ValueError("remaining chars at the end: '%s'" % ranking[ranking_end + 1:])
    while st != -1 and en != -1:
        bucket = []
        for s in ranking[st + 1:  en].split(","):
            bucket.append(converter(s.strip()))
        ret.append(bucket)
        st = ranking.find('[', en + 1, ranking_end)
        old_en = en
        en = ranking.find(']', max(en + 1, st + 1), ranking_end)
    if st != en:
        if st == -1:
            raise ValueError("missing open bucket")
        if en == -1:
            raise ValueError("missing closing bucket")
    if ranking[old_en + 1:ranking_end] != "":
        raise ValueError("misplaced chars: '%s'" % ranking[old_en + 1:ranking_end])
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
