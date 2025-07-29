#ifndef   	SORT_H_
# define   	SORT_H_

#include "common.h"

// ---------- Relational functions (return bool) -----------------------------


/*
   x < y, i.e., x is strictly lower than y in all dimensions. Assumes minimization.
*/

static inline bool
strongly_dominates(const double * restrict x, const double * restrict y, dimension_t dim)
{
    ASSUME(dim >= 2);
    for (dimension_t d = 0; d < dim; d++)
        if (x[d] >= y[d])
            return false;
    return true;
}

static inline bool
weakly_dominates(const double * restrict x, const double * restrict y, const dimension_t dim)
{
    ASSUME(dim >= 2);
    /* The code below is a vectorized version of this code:
    for (dimension_t d = 0; d < dim; d++)
        if (x[d] > y[d])
            return false;
    return true;
    */
    // GCC 15 is not yet able to infer this from attribute ASSUME().
    bool dominated = (x[0] <= y[0]) & (x[1] <= y[1]);
    for (dimension_t d = 2; d < dim; d++)
        dominated &= (x[d] <= y[d]);
    return dominated;
}

static inline bool
lexicographic_less_3d(const double * restrict a, const double * restrict b)
{
    return a[2] < b[2] || (a[2] == b[2] && (a[1] < b[1] || (a[1] == b[1] && a[0] <= b[0])));
}

// ---------- Comparison functions (e.g, qsort). Return 'int' ----------------

// General type for comparison functions used in qsort().
typedef int (*cmp_fun_t)(const void *, const void *);

static inline int
cmp_double_asc_rev(const void * restrict p1, const void * restrict p2, dimension_t dim)
{
    const double *x1 = *((const double **)p1);
    const double *x2 = *((const double **)p2);
    for (int i = dim - 1; i >= 0; i--) {
        if (x1[i] < x2[i])
            return -1;
        if (x1[i] > x2[i])
            return 1;
    }
    return 0;
}

static inline int
cmp_double_asc_rev_3d(const void * restrict p1, const void * restrict p2)
{
    return cmp_double_asc_rev(p1, p2, 3);
}

static inline int
cmp_double_asc_rev_4d(const void * restrict p1, const void * restrict p2)
{
    return cmp_double_asc_rev(p1, p2, 4);
}

static inline int
cmp_double_asc_only_3d(const void * restrict p1, const void * restrict p2)
{
    const double x1 = *(*(const double **)p1 + 2);
    const double x2 = *(*(const double **)p2 + 2);
    return (x1 < x2) ? -1 : (x1 > x2 ? 1 : 0);
}

static inline int
cmp_double_asc_only_4d(const void * restrict p1, const void * restrict p2)
{
    const double x1 = *(*(const double **)p1 + 3);
    const double x2 = *(*(const double **)p2 + 3);
    return (x1 < x2) ? -1 : (x1 > x2 ? 1 : 0);
}

static inline int
cmp_double_asc_y_des_x(const void * restrict p1, const void * restrict p2)
{
    const double x1 = *(const double *)p1;
    const double x2 = *(const double *)p2;
    const double y1 = *((const double *)p1+1);
    const double y2 = *((const double *)p2+1);
    return (y1 < y2) ? -1: ((y1 > y2) ? 1 : (x1 > x2 ? -1 : 1));
}

static inline int
cmp_doublep_x_asc_y_asc(const void * restrict p1, const void * restrict p2)
{
    const double x1 = **(const double **)p1;
    const double x2 = **(const double **)p2;
    const double y1 = *(*(const double **)p1 + 1);
    const double y2 = *(*(const double **)p2 + 1);
    return (x1 < x2) ? -1 : ((x1 > x2) ? 1 :
                             ((y1 < y2) ? -1 : ((y1 > y2) ? 1 : 0)));
}


#endif 	    /* !SORT_H_ */
