from mediane.algorithms.misc.borda_count import *

b1 = [1]
b2 = [2]
b3 = [3]
b4 = [2]
b5 = [3]
b6 = [1]
b7 = [3]
b8 = [1]
b9 = [2]

r1 = [b1, b2, b3]
r2 = [b4, b5, b6]
r3 = [b7, b8, b9]

rankings = [r1, r2, r3]

alg = BordaCount()

print(alg.compute_median_rankings(rankings, True))

print(rankings)