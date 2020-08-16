from os import listdir
from random import sample  # seed, randint
import numpy as np
from operator import itemgetter


path = "/home/pierre/Bureau/Doctorat/Datasets/notes_syn_pour_expe/"
mu_standard = 10
sigma_standard = 5

mu_special = 16
sigma_special = 4


def create_ranking_from_hash(x, reverse: bool):
    ranking = []
    sorted_x = sorted(x.items(), key=itemgetter(1), reverse=reverse)
    bucket = []
    current_val = None
    for tup in sorted_x:
        key = tup[0]
        val = tup[1]
        if val == current_val:
            bucket.append(key)
        else:
            if current_val is not None:
                ranking.append(bucket)
            current_val = val
            bucket = [key]
    ranking.append(bucket)
    return ranking


def create_one_raw_dataset(nb_standard_students, nb_special_students, nb_disciplines,
                           nb_disciplines_standard_students, nb_disciplines_special_students):
    id_jdd = len(listdir(path + "notes_raw")) + 1
    id_output = "dat" + '{0:03}'.format(id_jdd)
    nb_total_students = nb_standard_students + nb_special_students
    matrix = np.zeros((nb_total_students, nb_disciplines), dtype=float)-1.
    disciplines = list(range(nb_disciplines))

    for i in range(nb_standard_students):
        student = matrix[i]
        disciplines_chosen = sample(disciplines, nb_disciplines_standard_students)
        marks = np.round(np.random.randn(nb_disciplines_standard_students) * sigma_standard + mu_standard, 2)
        marks[marks > 20.] = 20
        marks[marks < 0] = 0
        student[disciplines_chosen] = marks

    for i in range(nb_standard_students, nb_total_students):
        student = matrix[i]
        disciplines_chosen = sample(disciplines, nb_disciplines_special_students)
        marks = np.round(np.random.randn(nb_disciplines_special_students) * sigma_special + mu_special, 2)
        marks[marks > 20.] = 20
        marks[marks < 0] = 0
        student[disciplines_chosen] = marks

    f = open(path+"notes_raw/"+id_output, "w")
    for i in range(nb_total_students):
        list_marks = matrix[i].tolist()
        list_round = [round(num, 2) for num in list_marks]
        f.write(str(i)+";"+str(list_round)[1:-1].replace(",", ";").strip().replace(" ", ""))
        f.write("\n")
    f.close()

    h_moyennes_students = {}
    f = open(path+"moyennes_etudiants_raw/"+id_output, "w")
    for i in range(nb_total_students):
        moyenne_etudiant = np.round(np.mean(matrix[i][matrix[i] >= 0.]), 2)
        h_moyennes_students[i] = moyenne_etudiant
        f.write(str(i)+";"+str(moyenne_etudiant))
        f.write("\n")
    f.close()

    goldstandard = create_ranking_from_hash(h_moyennes_students, True)

    f = open(path+"goldstandards/"+id_output, "w")
    f.write(str(goldstandard))
    f.write("\n")
    f.close()

    matrix_disciplines = matrix.transpose()
    f = open(path+"moyennes_ue_raw/"+id_output, "w")
    for i in range(nb_disciplines):
        discipline = matrix_disciplines[i]
        moyenne_ue = np.round(np.mean(discipline[discipline >= 0.]), 2)
        f.write(str(i)+";"+str(moyenne_ue))
        f.write("\n")
    f.close()

    f = open(path+"jdd_classements/"+id_output, "w")
    for i in range(nb_disciplines):
        ranking_hash = {}
        discipline = matrix_disciplines[i]
        for id_student in range(nb_total_students):
            if discipline[id_student] >= 0:
                ranking_hash[id_student] = discipline[id_student]
        f.write(str(create_ranking_from_hash(ranking_hash, True)))
        f.write("\n")
    f.close()


for toto in range(1000):
    create_one_raw_dataset(280, 20, 17, 14, 9)
