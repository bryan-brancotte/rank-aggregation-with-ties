/* implementation in C of BioConsert */

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#define L 2
#define C 6

/* malloc and free functions */
int* malloc_array_int(int n);
double* malloc_array_double(int n);

void free_array_int(int* t);
void free_array_double(double* t);

/* print functions */
void print_array_int(int* t, int n);
void print_array_double(double* t, int n);
void print_cost_matrix(double* m, int n);

/* general operations on arrays */
void fill_array_int(int* t, int dim, int nb);
void fill_array_double(double* t, int dim, double nb);
double vdot(double* t1, double* t2, int n);

/* utils */
int size_t2int(size_t val);
size_t int2size_t(int val);


/* rank aggregation functions */
double* get_cost_matrix(int* positions, double* vect_before, double* vect_tied, int n, int m);
void c_BioConsert(int* positions, int* departure_rankings, double* vect_before, double* vect_tied, int n, int m, int nb_rankings_departure, double* dist_min);
void bioConsert(int* departure_rankings, double* cost_matrix_1D, int n, int m, double* dist_min );
double improve_one_ranking(int* ranking, double* cost_matrix_1D, int n);
int compute_delta_costs(int* r, int element, double* m, int bucket_elem, int max_id_bucket, double* change, double* add, int n);
int search_to_change_bucket(int bucket_elem, double* change, int max_id_bucket);
int search_to_add_bucket(int bucket_elem, double* add, int max_id_bucket);
void change_bucket(int* r, int n, int element, int old_pos, int new_pos, int alone_in_old_bucket);
void add_bucket(int* r, int n, int element, int old_pos, int new_pos, int alone_in_old_bucket);


/* function called by python.
position : 1d representation of the n * m int matrix of the positions where n is the number of elements and m the number of rankings.
departure_rankings : 1d representation of the n * m int matrix representing the departure rankings.
vect_before & vect_tied : score scheme of the KCF
nb_rankings_departure : the number of departure rankings for bioconsert. Note that it is not necessary equal to m
dist_min is the adress of the double value representing the minimum score found by bioconsert (will be updated during the computation */
void c_BioConsert(int* positions, int* departure_rankings, double* vect_before, double* vect_tied, int n, int m, int nb_rankings_departure, double* dist_min)
{
    double* cost_matrix_1D = get_cost_matrix(positions, vect_before, vect_tied, n, m);

    //print_cost_matrix(cost_matrix_1D, n);
    bioConsert(departure_rankings, cost_matrix_1D, n, nb_rankings_departure, dist_min);

    free_array_double(cost_matrix_1D);
}


void bioConsert(int* departure_rankings, double* cost_matrix_1D, int n, int nb_rankings_departure, double* dst_min )
{
    int i, j;
    int* r = malloc_array_int(n);
    int cpt = 0, cpt2;
    for(i = 0; i < nb_rankings_departure; i++)
    {
        cpt2 = cpt;
        for(j = 0; j < n; j++)
        {
            r[j] = departure_rankings[cpt2++];
        }
        dst_min[i] += improve_one_ranking(r, cost_matrix_1D, n);
        cpt2 = cpt;
        for(j = 0; j < n; j++)
        {
            departure_rankings[cpt2++] = r[j];
        }
        cpt += n;
    }
    free_array_int(r);
}

double improve_one_ranking(int* r, double* cost_matrix_1D, int n)
{
    int i, elem, bucket_elem;
    double delta_dist = 0.;
    int max_id_bucket = -1;
    double* change = malloc_array_double(n + 2);
    double* add = malloc_array_double(n + 3);

    for(i = 0; i < n; i++)
    {
        if(max_id_bucket < r[i])
        {
            max_id_bucket = r[i];
        }
    }
    int terminated = 0;
    int alone = -1;
    int to = 0;
    
    while(!terminated)
    {
        terminated = 1;
        for(elem = 0; elem < n; elem++)
        {
            bucket_elem = r[elem];

            fill_array_double(change, max_id_bucket+1, 0.);
            fill_array_double(add, max_id_bucket+2, 0.);
            alone = compute_delta_costs(r, elem, cost_matrix_1D, bucket_elem, max_id_bucket, change, add, n);

            to = search_to_change_bucket(bucket_elem, change, max_id_bucket);
            if(to >= 0)
            {
                terminated = 0;
                delta_dist += change[to];
                change_bucket(r, n, elem, bucket_elem, to, alone);
                if(alone == 1)
                {
                    max_id_bucket -= 1;
                }
            }
            else
            {
                to = search_to_add_bucket(bucket_elem, add, max_id_bucket);
                if(to >= 0)
                {
                    terminated = 0;
                    delta_dist += add[to];
                    add_bucket(r, n, elem, bucket_elem, to, alone);
                    if(alone == 0)
                    {
                        max_id_bucket += 1;
                    }
                }
            }
        }

    }
  
    free_array_double(change);
    free_array_double(add);
    return delta_dist;
}

/*  r : the ranking : n vector, r[i] = id_bucket of element i
    element : the element which may move
    m : the cost matrix
    bucket_elem : the id_bucket of element to possibly move
    int max_id_bucket : the max of r
    change : n+2 double vector
    add : n+3 double vector
    n : number of elements

    returns : boolean 0/1 : is "element" alone in its current bucket?
 */
int compute_delta_costs(int* r, int element, double* m, int bucket_elem, int max_id_bucket, double* change, double* add, int n )
{
    /* pos : integer such that m[pos] = cost of having target before elem 0, m[pos+1] = cost of having target after elem 0, m[pos+2] = cost of having target tied with elem 0 */
    int alone = 1, e2, bucket_e2, pos = 3 * n * element;
    double tied_to_before = 0., tied_to_after = 0., tied_to_tied = 0.;
    /* for each element 0 to n-1 */
    for(e2 = 0; e2 < n; e2++)
    {
        /* bucket_e2 = bucket_id of element e2 */
        bucket_e2 = r[e2];
        /* if the target element is before e2,
            . tying the target with e2     ==> we get back the cost of having target before e2 and we pay the cost of tying them
            . putting the target after e2  ==> we get back the cost of having target before e2 and we pay the cost of having the target after e2
         */
        if(bucket_elem < bucket_e2)
        {
            change[bucket_e2] += m[pos + 2] - m[pos];
            change[bucket_e2+1] += m[pos + 1] - m[pos + 2];

            add[bucket_e2 + 1] += m[pos+1] - m[pos];
        }
        else if (bucket_elem > bucket_e2)
        {
            change[bucket_e2] += m[pos+2] - m[pos+1];
            if(bucket_e2 != 0)
            {
                change[bucket_e2 - 1] += m[pos] - m[pos+2];
            }
            add[bucket_e2] += m[pos] - m[pos+1];
        }
        else
        {
            if(element != e2)
            {
                if(alone)
                {
                    alone = 0;
                }
                tied_to_before += m[pos];
                tied_to_after += m[pos+1];
                tied_to_tied += m[pos+2];
            }
        }
        /* change of elements to compare target with */
        pos += 3;
    }
    if(bucket_elem != 0)
    {
        change[bucket_elem - 1] += tied_to_before - tied_to_tied;
    }
    change[bucket_elem + 1] += tied_to_after - tied_to_tied;
    add[bucket_elem + 1] += tied_to_after - tied_to_tied;
    add[bucket_elem] += tied_to_before - tied_to_tied;

    //add[bucket_elem+1] += add[bucket_elem];

    return alone;
}


int search_to_change_bucket(int bucket_elem, double* change, int max_id_bucket)
{
    int i = bucket_elem + 1;
    int res = -1;
/*
        delta_change[id_bucket_element:max_id_bucket+1] = cumsum(delta_change[id_bucket_element:max_id_bucket+1])
        delta_change[0:id_bucket_element] = cumsum(delta_change[0:id_bucket_element][::-1])

*/

    if(change[i-1] < 0)
    {
        res = i-1;
    }
    while(res == -1 && i <= max_id_bucket)
    {
        change[i] += change[i-1];
        if(change[i] < 0)
        {
            res = i;
        }
        i++;
    }

    if(res == -1)
    {

        i = bucket_elem - 2;
        //printf("%d ", i+1);
        if(i >= -1 && change[i+1] < 0)
        {
            res = i+1;
        }

        while(res == -1 && i >= 0)
        {
            change[i] += change[i+1];

            if(change[i] < 0)
            {
                res = i;
            }
            i--;
        }

    }

    return res;
}

void change_bucket(int* r, int n, int element, int old_pos, int new_pos, int alone_in_old_bucket)
{

    int i;
    r[element] = new_pos;
    if(alone_in_old_bucket == 1)
    {
        for(i = 0; i < n; i++)
        {
            if(r[i] > old_pos)
            {
                r[i] -= 1;
            }
        }
    }
}

/*      
        delta_add[0:id_bucket_element+1] = cumsum(delta_add[0:id_bucket_element+1][::-1])
        delta_add[id_bucket_element+1:max_id_bucket+2] = cumsum(delta_add[id_bucket_element+1:max_id_bucket+2])
        new_pos = argmax(add_costs[buck_elem+1:] < 0).item() + buck_elem + 1
        if new_pos <= max_id_bucket + 1:
            return new_pos, add_costs[new_pos]
        new_pos = argmax(add_costs[0:buck_elem+1] < 0).item()
        if new_pos > 0 or add_costs[0] < 0:
            return buck_elem - new_pos, add_costs[new_pos]
        return -1, 0.0
*/
int search_to_add_bucket(int bucket_elem, double* add, int max_id_bucket)
{

    int i = bucket_elem + 2;
    int res = -1;

    if(add[i-1] < 0)
    {
        res = i-1;
    }

    while(res == -1 && i <= max_id_bucket + 1)
    {
        add[i] += add[i-1];

        if(add[i] < 0)
        {
            res = i;
        }
        i++;
    }

    if(res == -1)
    {
        i = bucket_elem-1;

        if(add[i+1] < 0)
        {
            res = i+1;
        }

        while(res == -1 && i >= 0)
        {
            add[i] += add[i+1];

            if(add[i] < 0)
            {
                res = i;
            }
            i--;
        }
    }
    return res;
}

void add_bucket(int* r, int n, int element, int old_pos, int new_pos, int alone_in_old_bucket)
{
    int i;
    if(old_pos < new_pos)
    {
        if(alone_in_old_bucket == 1)
        {
            for(i = 0; i < n; i++)
            {
                if(r[i] > old_pos && r[i] < new_pos)
                {
                    r[i] -= 1;
                }
            }
            r[element] = new_pos - 1;
        }
        else
        {
            for(i = 0; i < n; i++)
            {
                if(r[i] >= new_pos)
                {
                    r[i] += 1;
                }
            }
            r[element] = new_pos;
        }   
    }
    else
    {
        if(alone_in_old_bucket == 1)
        {
            for(i = 0; i < n; i++)
            {
                if(r[i] >= new_pos && r[i] < old_pos)
                {
                    r[i] += 1;
                }
            }   
            r[element] = new_pos;
        }
        else
        {
            for(i = 0; i < n; i++)
            {
                if(r[i] >= new_pos)
                {
                    r[i] += 1;
                }
            }
            r[element] = new_pos;
        }
    }
}

double* get_cost_matrix(int* positions, double* vect_before, double* vect_tied, int n, int m)
{
    double* score_matrix = malloc_array_double(n * n * 3);

    int elem1, elem2, i, before, after, tied, only_1, only_2, none, pos_elem1, pos_elem2;
    double x_bef_y, y_bef_x, x_y_tied;
    int index1,index2;
    int pos_left = 0, pos_right, save;

    for(elem1 = 0; elem1 < n; elem1++)
    {
        pos_left = m * elem1;
        pos_right = pos_left + m;

        for(elem2 = elem1 + 1 ; elem2 < n; elem2++)
        {
            save = pos_left;

            before = 0;
            after = 0;
            tied = 0;
            only_1 = 0;
            only_2 = 0;
            none = 0;

            for(i = 0; i < m; i++)
            {
                pos_elem1 = positions[save++];
                pos_elem2 = positions[pos_right++];
                if(pos_elem1 >= 0)
                {
                    if(pos_elem2 >= 0)
                    {
                        if(pos_elem1 > pos_elem2)
                        {
                            after++;
                        }
                        else
                        {
                            if(pos_elem1 < pos_elem2)
                            {
                                before++;
                            }
                            else
                            {
                                tied++;
                            }
                        }
                    }
                    else
                    {
                        only_1++;
                    }
                }
                else
                {
                    if(pos_elem2 >= 0)
                    {
                        only_2++;
                    }
                    else
                    {
                        none++;
                    }
                }
            }
            x_bef_y = vect_before[0] * before + vect_before[1] * after + vect_before[2] * tied + vect_before[3] * only_1 + vect_before[4] * only_2 + vect_before[5] * none;
            y_bef_x = vect_before[1] * before + vect_before[0] * after + vect_before[2] * tied + vect_before[4] * only_1 + vect_before[3] * only_2 + vect_before[5] * none;
            x_y_tied = vect_tied[0] * before + vect_tied[1] * after + vect_tied[2] * tied + vect_tied[3] * only_1 + vect_tied[4] * only_2 + vect_tied[5] * none;
            index1 = 3 * (n * elem1 + elem2);
            index2 = 3 * (n * elem2 + elem1);
            score_matrix[index1] = x_bef_y;
            score_matrix[index1 + 1] = y_bef_x;
            score_matrix[index1 + 2] = x_y_tied;
            score_matrix[index2] = y_bef_x;
            score_matrix[index2 + 1] = x_bef_y;
            score_matrix[index2 + 2] = x_y_tied;
        }
    }
    return score_matrix;
}

void print_cost_matrix(double* m, int n)
{
    int i,j,pos = 0;
    for(i = 0; i < n; i++)
    {
        for(j = 0; j < n; j++)
        {
            printf("%d %d : %lf %lf %lf\n", i,j, m[pos], m[pos+1], m[pos+2]);
            pos+= 3;
        }
    }
    printf("\n");
}


int* malloc_array_int(int n)
{
    int* t = NULL;
    t = (int*)(malloc(int2size_t(n) * sizeof(int)));
    if(t == NULL)
    {
        fprintf(stderr, "Impossible to allocate int array %d, check memory capacity\n", n);
        exit(1);
    }
    int i;
    for(i = 0; i < n; i++)
    {
        t[i] = 0;
    }
    return t;
}

double* malloc_array_double(int n)
{
    double* t = NULL;
    t = (double*)(malloc(int2size_t(n) * sizeof(double)));

    if(t == NULL)
    {
        fprintf(stderr, "Impossible to allocate double array %d, check memory capacity\n", n);
        exit(1);
    }
    int i;
    for(i = 0; i < n; i++)
    {
        t[i] = 0.;
    }
    return t;
}

void free_array_int(int* t)
{
    free(t);
}

void free_array_double(double* t)
{
    free(t);
}

double vdot(double* t1, double* t2, int n)
{
    double res = 0.;
    int i;
    for(i = 0; i < n; i++)
    {
        res += t1[i] * t2[i];
    }
    return res/n;
}

void print_array_int(int* t, int n)
{
    int i;
    for(i = 0; i < n; i++)
    {
        printf("%d ", t[i]);
    }
    printf("\n");
}

void print_array_double(double* t, int n)
{
    int i;
    for(i = 0; i < n; i++)
    {
        printf("%lf ", t[i]);
    }
    printf("\n");
}



int size_t2int(size_t val)
{
    return (val <= INT_MAX) ? (int)((ssize_t)val) : -1;
}

size_t int2size_t(int val)
{
    return (val < 0) ? __SIZE_MAX__ : (size_t)((unsigned)val);
}

void fill_array_int(int* t, int dim, int nb)
{
    int i;
    for(i = 0; i < dim; i++)
    {
        t[i] = nb;
    }
}

void fill_array_double(double* t, int dim, double nb)
{
    int i;
    for(i = 0; i < dim; i++)
    {
        t[i] = nb;
    }
}


int main(int argc, char** argv)
{
    return 0;
}
