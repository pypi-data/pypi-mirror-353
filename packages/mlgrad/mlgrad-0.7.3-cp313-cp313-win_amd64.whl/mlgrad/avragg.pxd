# cython: language_level=3

cimport cython
cimport numpy

from mlgrad.funcs cimport SoftAbs_Sqrt, Square, Func, ParameterizedFunc
from mlgrad.funcs2 cimport SoftMin, SoftMax, PowerMax
from mlgrad.averager cimport ScalarAverager
from libc.math cimport pow, sqrt, log, exp

# from mlgrad.miscfuncs cimport init_rand, rand, fill

ctypedef double (*FuncEvaluate)(Func, double) nogil
ctypedef double (*FuncDerivative)(Func, double) nogil
ctypedef double (*FuncDerivative2)(Func, double) nogil
ctypedef double (*FuncDerivativeDivX)(Func, double) nogil

cdef inline double fabs(double x) noexcept nogil:
    if x >= 0:
        return x
    else:
        return -x

cdef inline double fmax(double x, double y) noexcept nogil:
    if x > y:
        return x
    else:
        return y


ctypedef fused number:
    float
    double

cdef extern from "Python.h":
    double PyFloat_GetMax()
    double PyFloat_GetMin()

cdef extern from "pymath.h" nogil:
    bint Py_IS_FINITE(double x)
    bint Py_IS_INFINITY(double x)
    bint Py_IS_NAN(double x)
    bint copysign(double x, double x)

cdef inline double array_min(double[::1] arr):
    cdef Py_ssize_t i, N = arr.shape[0]
    cdef double *aa = &arr[0]
    cdef double v, min_val = aa[0]

    for i in range(N):
        v = aa[i]
        if v < min_val:
            min_val = v

    return min_val

cdef inline double array_mean(double[::1] arr):
    cdef Py_ssize_t i, N = arr.shape[0]
    cdef double *aa = &arr[0]
    cdef double s

    s = 0
    for i in range(N):
        s += aa[i]

    return s / N

cdef inline double array_std(double[::1] arr, double mu):
    cdef Py_ssize_t i, N = arr.shape[0]
    cdef double *a = &arr[0]
    cdef double v, s

    s = 0
    for i in range(N):
        v = a[i] - mu
        s += v*v

    return sqrt(s/N)

# cdef inline void array_add_scalar(double[::1] arr, const double v):
#     cdef Py_ssize_t i, N = arr.shape[0]

#     for i in range(N):
#         arr[i] += v

cdef class Penalty:
    cdef readonly Func func

    cdef double evaluate(self, double[::1] Y, double u)
    cdef double derivative(self, double[::1] Y, double u)
    cdef void gradient(self, double[::1] Y, double u, double[::1] grad)
    cdef double iterative_next(self, double[::1] Y, double u)

@cython.final
cdef class PenaltyAverage(Penalty):
    pass

@cython.final
cdef class PenaltyAverage2(Penalty):
    pass

@cython.final
cdef class PenaltyScale(Penalty):
    pass

#############################################################

cdef class Average:
    cdef readonly double tol
    cdef readonly Py_ssize_t n_iter 
    cdef readonly Py_ssize_t K 
    # cdef public bint success    
    cdef public double u
    cdef public double pval
    cdef bint evaluated
    #
    cdef double init_u(self, double[::1] Y)
    #
    cdef double _evaluate(self, double[::1] Y)
    cdef _gradient(self, double[::1] Y, double[::1] grad)
    cdef _weights(self, double[::1] Y, double[::1] weights)
    #    
    # cpdef fit(self, double[::1] Y)
    #
    # cdef bint stop_condition(self)

cdef class AverageIterative(Average):
    cdef readonly Penalty penalty
    
# @cython.final
cdef class MAverage(AverageIterative):
    cdef public Func func
    #

# @cython.final
# cdef class MAverage2(AverageIterative):
#     cdef Func func
    #
    
    
# @cython.final
cdef class SAverage(AverageIterative):
    cdef public Func func
    
# @cython.final
# cdef class Average_Iterative(Average):
#     pass

# @cython.final
# cdef class MAverage_Iterative(Average):
#     cdef Func func

# @cython.final
# cdef class Average_FG(Average):
#     #
#     cdef ScalarAverager deriv_averager
    
@cython.final
cdef class ParameterizedAverage(Average):
    cdef ParameterizedFunc func
    cdef Average avr

@cython.final
cdef class WMAverage(Average):
    cdef public Average avr
    cdef bint initial

# @cython.final
# cdef class WMAverageMixed(Average):
#     cdef Average avr
#     cdef double gamma
    
@cython.final
cdef class TMAverage(Average):
    cdef public Average avr

# @cython.final
# cdef class HMAverage(Average):
#     cdef Average avr
#     cdef double[::1] Z

@cython.final
cdef class WMZAverage(Average):
    cdef public double c, alpha
    cdef public MAverage mavr, savr
    cdef double mval, sval
    cdef double[::1] U, GU

@cython.final
cdef class WMZSum(Average):
    cdef public double c, alpha
    cdef public MAverage mavr, savr
    cdef double mval, sval
    cdef double[::1] U, GU
    

@cython.final
cdef class WZAverage(Average):
    cdef public double alpha
    cdef double mval, sval
    

@cython.final
cdef class ArithMean(MAverage):
    pass

@cython.final
cdef class RArithMean(Average):
    cdef Func func

@cython.final
cdef class KolmogorovMean(Average):
    cdef Func func, invfunc
    cdef double uu

@cython.final
cdef class SoftMinimal(Average):
    cdef SoftMin softmin

@cython.final
cdef class SoftMaximal(Average):
    cdef SoftMax softmax

@cython.final
cdef class PowerMaximal(Average):
    cdef PowerMax powermax
    
@cython.final
cdef class Minimal(Average):
    pass

@cython.final
cdef class Maximal(Average):
    pass
