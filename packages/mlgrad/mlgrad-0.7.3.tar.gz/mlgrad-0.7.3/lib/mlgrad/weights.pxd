# cython: language_level=3

cimport cython

from mlgrad.funcs cimport Func
from mlgrad.loss cimport Loss
from mlgrad.risks cimport ERisk, Risk, ERisk2, ERisk22, Functional
from mlgrad.avragg cimport Average
from mlgrad.models cimport Model

cimport mlgrad.inventory as inventory


cdef extern from "Python.h":
    double PyFloat_GetMax()
    double PyFloat_GetMin()

cdef inline double array_min(double[::1] arr):
    cdef Py_ssize_t i, N = arr.shape[0]
    cdef double v, min_val = arr[0]

    for i in range(N):
        v = arr[i]
        if v < min_val:
            min_val = v

    return min_val

cdef inline double sum_memoryview(double[::1] X):
    cdef double S
    cdef Py_ssize_t i, m = X.shape[0]
    
    S = 0
    for i in range(m):
        S += X[i]
    return S

cdef inline void mult_scalar_memoryview(double[::1] X, double c):
    cdef Py_ssize_t i, m = X.shape[0]

    for i in range(m):
        X[i] *= c
        
cdef inline void normalize_memoryview(double[::1] X):
    cdef double S, c
    cdef Py_ssize_t i, m = X.shape[0]

    S = 0
    for i in range(m):
        S += X[i]
    c = 1/S
    
    for i in range(m):
        X[i] *= c        

cdef class Weights(object):
    #
    cdef public double[::1] weights
    cdef bint normalize
    #
    cpdef init(self)
    cpdef eval_weights(self)
    cpdef double[::1] get_weights(self)
    cpdef double get_qvalue(self)
    cpdef set_param(self, name, val)

@cython.final   
cdef class ArrayWeights(Weights):
    pass

@cython.final
cdef class ConstantWeights(Weights):
    pass

@cython.final
cdef class RWeights(Weights):
    cdef public Risk risk
    # cdef readonly double[::1] lval_all
    # cdef public Func func
    # cdef bint normalize
    pass

@cython.final
cdef class MWeights(Weights):
    cdef public Risk risk
    cdef readonly double[::1] lvals
    # cdef public double best_u
    cdef public Average average
    cdef bint first_time #, u_only, use_best_u

@cython.final
cdef class MWeights2(Weights):
    cdef public ERisk2 risk
    cdef readonly double[::1] lvals
    # cdef public double best_u
    cdef public Average average
    cdef bint first_time #, u_only, use_best_u

@cython.final
cdef class MWeights22(Weights):
    cdef public ERisk22 risk
    cdef readonly double[::1] lvals
    # cdef public double best_u
    cdef public Average average
    cdef bint first_time #, u_only, use_best_u
    
@cython.final
cdef class WeightsCompose(Weights):
    cdef Weights _weights1
    cdef Weights _weights2
