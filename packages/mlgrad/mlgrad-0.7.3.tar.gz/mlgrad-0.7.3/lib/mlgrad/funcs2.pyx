# coding: utf-8

# The MIT License (MIT)
#
# Copyright (c) <2015-2024> <Shibzukhov Zaur, szport at gmail dot com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

cimport cython

import numpy as np
# from mlgrad.models import asarray1d

cdef double double_max = PyFloat_GetMax()
cdef double double_min = PyFloat_GetMin()


enpty = np.empty

numpy.import_array()

# cdef _asarray(o):
#     if type(o) is ndarray:
#         return o
#     else:
#         return asarray(o)

# asarray = np.asarray

cdef class Func2:

    cdef void _evaluate_items(self, double[::1] X, double[::1] Y):
        pass
    #    
    cdef double _evaluate(self, double[::1] X):
        return 0
    #
    cdef double _evaluate_ex(self, double[::1] X, double[::1] W):
        return 0
    #
    cdef void _gradient(self, double[::1] X, double[::1] grad):
        pass
    #
    cdef void _gradient_ex(self, double[::1] X, double[::1] grad, double[::1] W):
        pass
    #
    cdef double _gradient_j(self, double[::1] X, Py_ssize_t j):
        return 0
    #
    def evaluate_items(self, double[::1] X):
        cdef numpy.npy_intp n = X.shape[0]
        Y = numpy.PyArray_EMPTY(1, &n, numpy.NPY_DOUBLE, 0)
        self._evaluate_items(X, Y)
        return Y
    #
    def evaluate(self, double[::1] X):
        return self._evaluate(X)
    #
    def evaluate_ex(self, double[::1] X, double[::1] W):
        return self._evaluate_ex(X, W)
    #
    def gradient(self, double[::1] X):
        cdef numpy.npy_intp n = X.shape[0]
        grad = numpy.PyArray_EMPTY(1, &n, numpy.NPY_DOUBLE, 0)
        self._gradient(X, grad)
        return grad
    #
    def gradient_ex(self, double[::1] X, double[::1] W):
        cdef numpy.npy_intp n = X.shape[0]
        grad = numpy.PyArray_EMPTY(1, &n, numpy.NPY_DOUBLE, 0)
        self._gradient_ex(X, grad, W)
        return grad

cdef class Func2Layer:

    cdef void _evaluate(self, double[::1] X, double[::1] Y):
        pass
    cdef void _gradient(self, double[::1] X, double[::1] Y):
        pass
    
cdef class SquareNormLayer(Func2Layer):
    #
    def __init__(self, n):
        self.funcs = []
        self.starts = list_int()
        self.counts = list_int()
    #
    def add(self, Func2 func, int start, int count):
        self.funcs.append(func)
        self.starts.append(start)
        self.counts.append(count)
    #
    cdef void _evaluate(self, double[::1] X, double[::1] Y):
        cdef Py_ssize_t j, m = len(self.funcs)
        cdef Func2 func
        cdef Py_ssize_t start, count

        for j in range(m):
            func = <Func2>self.funcs[j]
            start = self.starts._get(j)
            count = self.counts._get(j)
            Y[j] = func._evaluate(X[start:start+count])
    #
    cdef void _gradient(self, double[::1] X, double[::1] Y):
        cdef Py_ssize_t j, m = len(self.funcs)
        cdef Func2 func
        cdef Py_ssize_t start, count

        for j in range(m):
            func = <Func2>self.funcs[j]
            start = self.starts._get(j)
            count = self.counts._get(j)
            func._gradient(X[start:start+count], Y[start:start+count])
    
@cython.final
cdef class MixedNorm(Func2):
    #
    def __init__(self, Func2 func1, Func2 func2, tau1, tau2):
        self.func1 = func1
        self.func2 = func2
    #
    @cython.final
    cdef void _evaluate_items(self, double[::1] X, double[::1] Y):
        cdef numpy.npy_intp n = X.shape[0]
        cdef double[::1] t1 = numpy.PyArray_EMPTY(1, &n, numpy.NPY_DOUBLE, 0)
        cdef double[::1] t2 = numpy.PyArray_EMPTY(1, &n, numpy.NPY_DOUBLE, 0)
        cdef double* t1_ptr = &t1[0]
        cdef double* t2_ptr = &t2[0]
        cdef double* Y_ptr = &Y[0]
        cdef Py_ssize_t i
        cdef double tau1 = self.tau1, tau2 = self.tau2

        self.func1._evaluate_items(X, t1)
        self.func2._evaluate_items(X, t2)

        for i in range(X.shape[0]):
            Y_ptr[i] = tau1 * t1_ptr[i] + tau2 * t2_ptr[i]
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        return self.tau1 * self.func1._evaluate(X) + \
			   self.tau2 * self.func2._evaluate(X) 
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] Y):
        cdef numpy.npy_intp n = X.shape[0]
        cdef double[::1] t1 = numpy.PyArray_EMPTY(1, &n, numpy.NPY_DOUBLE, 0)
        cdef double[::1] t2 = numpy.PyArray_EMPTY(1, &n, numpy.NPY_DOUBLE, 0)
        cdef double* t1_ptr = &t1[0]
        cdef double* t2_ptr = &t2[0]
        cdef double* Y_ptr = &Y[0]
        cdef Py_ssize_t i
        cdef double tau1 = self.tau1, tau2 = self.tau2

        self.func1._gradient(X, t1)
        self.func2._gradient(X, t2)

        for i in range(X.shape[0]):
            Y_ptr[i] = tau1 * t1_ptr[i] + tau2 * t2_ptr[i]

@cython.final
cdef class FuncNorm(Func2):
    #
    def __init__(self, Func func):
        self.func = func
#         self.all = all
    #
    @cython.final
    cdef void _evaluate_items(self, double[::1] X, double[::1] Y):
        self.func._evaluate_array(&X[0], &Y[0], X.shape[0])
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        cdef Py_ssize_t i
        cdef double s
        cdef double* X_ptr = &X[0]
        cdef Func func = self.func

        s = 0
        for i in range(X.shape[0]):
            s += func._evaluate(X_ptr[i])
        return s
    #
    @cython.final
    cdef double _evaluate_ex(self, double[::1] X, double[::1] W):
        cdef Py_ssize_t i
        cdef double s
        cdef double* X_ptr = &X[0]
        cdef double* W_ptr = &W[0]
        cdef Func func = self.func

        s = 0
        for i in range(X.shape[0]):
            s += W_ptr[i] * func._evaluate(X_ptr[i])
        return s
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] grad):
        self.func._derivative_array(&X[0], &grad[0], X.shape[0])
    #
    @cython.final
    cdef void _gradient_ex(self, double[::1] X, double[::1] grad, double[::1] W):
        cdef Py_ssize_t i
        cdef double* W_ptr = &W[0]
        cdef double* grad_ptr = &grad[0]
    
        self.func._derivative_array(&X[0], &grad[0], X.shape[0])
        for i in range(X.shape[0]):
            grad_ptr[i] *= W_ptr[i]
    #
    @cython.final
    cdef double _gradient_j(self, double[::1] X, Py_ssize_t j):
        return self.func._derivative(X[j])
    #
    def _repr_latex_(self):
        return r"$||\mathbf{w}||_{%s}^{%s}=\sum_{i=0}^n w_i^{%s}$" % (self.p, self.p, self.p)

@cython.final    
cdef class PowerNorm(Func2):
    
    def __init__(self, p=2.0):
        self.p = p
#         self.all = all
    #
    @cython.final
    cdef void _evaluate_items(self, double[::1] X, double[::1] Y):
        cdef Py_ssize_t i
        cdef double v, p=self.p
        cdef double* X_ptr = &X[0]
        cdef double* Y_ptr = &Y[0]

        for i in range(X.shape[0]):
            v = X_ptr[i]
            if v >= 0:
                Y_ptr[i] = pow(v, p) / p
            else:
                Y_ptr[i] = pow(-v, p) / p
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        cdef Py_ssize_t i
        cdef double s, v, p=self.p
        cdef double* X_ptr = &X[0]

        s = 0
        for i in range(X.shape[0]):
            v = X_ptr[i]
            if v >= 0:
                s += pow(v, p)
            else:
                s += pow(-v, p)
        
        s /= p
        return s
    #
    @cython.final
    cdef double _evaluate_ex(self, double[::1] X, double[::1] W):
        cdef Py_ssize_t i, m
        cdef double s, v, p=self.p
        cdef double* X_ptr = &X[0]
        cdef double* W_ptr = &W[0]

        s = 0
        for i in range(X.shape[0]):
            v = X_ptr[i]
            if v >= 0:
                s = fma(W_ptr[i], pow(v, p), s)
            else:
                s = fma(W_ptr[i], pow(-v, p), s)
        
        s /= self.p
        return s
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] grad):
        cdef Py_ssize_t i, m
        cdef double v, p1 = self.p-1
        cdef double* X_ptr = &X[0]
        cdef double* grad_ptr = &grad[0]
    
        for i in range(X.shape[0]):
            v = X_ptr[i]
            if v < 0:
                grad_ptr[i] = -pow(-v, p1)
            else:
                grad_ptr[i] = pow(v, p1)
    #
    @cython.final
    cdef void _gradient_ex(self, double[::1] X, double[::1] grad, double[::1] W):
        cdef Py_ssize_t i, m
        cdef double v, p1 = self.p-1
        cdef double* X_ptr = &X[0]
        cdef double* W_ptr = &W[0]
        cdef double* grad_ptr = &grad[0]
    
        for i in range(X.shape[0]):
            v = X_ptr[i]
            if v < 0:
                grad_ptr[i] = -W_ptr[i] * pow(-v, p1)
            else:
                grad_ptr[i] = W_ptr[i] * pow(v, p1)
    #
    @cython.final
    cdef double _gradient_j(self, double[::1] X, Py_ssize_t j):
        cdef double v, p1 = self.p-1
        cdef double* X_ptr = &X[0]
    
        v = X_ptr[j]
        if v < 0:
            return -pow(-v, p1)
        else:
            return pow(v, p1)
    #
    def _repr_latex_(self):
        return r"$||\mathbf{w}||_{%s}^{%s}=\sum_{i=0}^n w_i^{%s}$" % (self.p, self.p, self.p)

@cython.final
cdef class SquareNorm(Func2):
    #
    @cython.final
    cdef void _evaluate_items(self, double[::1] X, double[::1] Y):
        cdef Py_ssize_t i
        cdef double v
        cdef double* X_ptr = &X[0]
        cdef double* Y_ptr = &Y[0]

        for i in range(X.shape[0]):
            v = X_ptr[i]
            Y_ptr[i] = 0.5 * v * v
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v
        cdef double* X_ptr = &X[0]

        s = 0
        for i in range(m):
            v = X_ptr[i]
            s += v * v

        s /= 2.
        return s
    #
    @cython.final
    cdef double _evaluate_ex(self, double[::1] X, double[::1] W):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v
        cdef double* X_ptr = &X[0]
        cdef double* W_ptr = &W[0]

        s = 0
        for i in range(m):
            v = X_ptr[i]
            s += W_ptr[i] * v * v

        s /= 2.
        return s
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] grad):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double* X_ptr = &X[0]
        cdef double* grad_ptr = &grad[0]

        for i in range(m):
            grad_ptr[i] = X_ptr[i]    
    #
    @cython.final
    cdef void _gradient_ex(self, double[::1] X, double[::1] grad, double[::1] W):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double* X_ptr = &X[0]
        cdef double* W_ptr = &W[0]
        cdef double* grad_ptr = &grad[0]

        for i in range(m):
            grad_ptr[i] = W_ptr[i] * X_ptr[i]    
    #
    @cython.final
    cdef double _gradient_j(self, double[::1] X, Py_ssize_t j):
        return X[j]
    #
    def _repr_latex_(self):
        return r"$||\mathbf{w}||_2^2=\sum_{i=0}^n w_i^2$"
        

@cython.final
cdef class AbsoluteNorm(Func2):
    #
    @cython.final
    cdef void _evaluate_items(self, double[::1] X, double[::1] Y):
        cdef Py_ssize_t i
        cdef double* X_ptr = &X[0]
        cdef double* Y_ptr = &Y[0]

        for i in range(X.shape[0]):
            Y_ptr[i] = fabs(X_ptr[i])
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        cdef Py_ssize_t i
        cdef double s
        cdef double* X_ptr = &X[0]

        s = 0
        for i in range(X.shape[0]):
            s += fabs(X_ptr[i])
        return s
    #
    @cython.final
    cdef double _evaluate_ex(self, double[::1] X, double[::1] W):
        cdef Py_ssize_t i
        cdef double s
        cdef double* X_ptr = &X[0]
        cdef double* W_ptr = &W[0]

        s = 0
        for i in range(X.shape[0]):
            s = fma(W_ptr[i], fabs(X_ptr[i]), s)
        return s
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] grad):
        cdef Py_ssize_t i, m
        cdef double* X_ptr = &X[0]
        cdef double* grad_ptr = &grad[0]

        for i in range(X.shape[0]):
            v = X_ptr[i]
            if v > 0:
                grad_ptr[i] = 1
            elif v < 0:
                grad_ptr[i] = -1
            else:
                grad_ptr[i] = 0
    #
    @cython.final
    cdef void _gradient_ex(self, double[::1] X, double[::1] grad, double[::1] W):
        cdef Py_ssize_t i, m
        cdef double* X_ptr = &X[0]
        cdef double* W_ptr = &W[0]
        cdef double* grad_ptr = &grad[0]

        for i in range(X.shape[0]):
            v = X_ptr[i]
            if v > 0:
                grad_ptr[i] = W_ptr[i]
            elif v < 0:
                grad_ptr[i] = -W_ptr[i]
            else:
                grad_ptr[i] = 0
    #
    @cython.final
    cdef double _gradient_j(self, double[::1] X, Py_ssize_t j):
        cdef double v = X[j]
        
        if v < 0:
            v = -v
        return v
    #    
    def _repr_latex_(self):
        return r"$||\mathbf{w}||_1=\sum_{i=0}^n |w_i|$"

@cython.final
cdef class SoftAbsoluteNorm(Func2):
    #
    def __init__(self, eps=0.001):
        self.eps = eps
        self.eps2 = eps * eps
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        cdef Py_ssize_t i
        cdef double s, v
        cdef double* X_ptr = &X[0]

        s = 0
        for i in range(X.shape[0]):
            v = X_ptr[i]
            s += v * v
        return sqrt(self.eps2 + s) - self.eps
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] grad):
        cdef Py_ssize_t i
        cdef double s, v
        cdef double* X_ptr = &X[0]
        cdef double* grad_ptr = &grad[0]

        s = 0
        for i in range(X.shape[0]):
            grad_ptr[i] = v = X_ptr[i]
            s += v * v
        s = sqrt(self.eps2 + s)
        
        for i in range(X.shape[0]):
            grad_ptr[i] /= s
    #
    @cython.final
    cdef double _gradient_j(self, double[::1] X, Py_ssize_t j):
        cdef Py_ssize_t i
        cdef double s, v
        cdef double* X_ptr = &X[0]

        s = 0
        for i in range(X.shape[0]):
            v = X_ptr[i]
            s += v * v
        s = sqrt(self.eps2 + s)
        
        return X_ptr[j] / s
    #    
    def _repr_latex_(self):
        return r"$||\mathbf{w}||_1=\sum_{i=0}^n |w_i|$"

@cython.final
cdef class SquareForm(Func2):
    
    def __init__(self, double[:,::1] matrix):
        if matrix.shape[0] != matrix.shape[1]-1:
            raise RuntimeError("Invalid shape: (%s,%s)" % (matrix.shape[0], matrix.shape[1]))
        self.matrix = matrix
    #
    @cython.final
    cdef double _evaluate(self, double[::1] x):
        cdef double[:,::1] mat = self.matrix
        cdef Py_ssize_t n_row = mat.shape[0]
        cdef Py_ssize_t n_col = mat.shape[1]
        cdef double s, val
        cdef Py_ssize_t i, j
        
        val = 0
        for j in range(n_row):
            s = mat[j,0]
            for i in range(1, n_col):
                s = fma(mat[j,i], x[i-1], s)
            val += s*s
        return 0.5*val
    #
    @cython.final
    cdef void _gradient(self, double[::1] x, double[::1] y):
        cdef double[:,::1] mat = self.matrix
        cdef Py_ssize_t n_row = mat.shape[0]
        cdef Py_ssize_t n_col = mat.shape[1]
        cdef double s
        cdef Py_ssize_t i, j
        
        n_row = mat.shape[0]
        n_col = mat.shape[1]
        
        fill_memoryview(y, 0)
        for j in range(n_row):
            s = mat[j,0]
            for i in range(1, n_col):
                s = fma(mat[j,i], x[i-1], s)

            for i in range(1, n_col):
                y[i-1] += s*mat[j,i]

@cython.final
cdef class SoftMin(Func2):
    
    def __init__(self, p=1.0):
        self.p = p
        self.evals = None
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v, v_min
        cdef double p = self.p
        
        v_min = double_max
        for i in range(m):
            v = X[i]
            if v < v_min:
                v_min = v
        
        s = 0
        for i in range(m):
            s += exp(p*(v_min - X[i]))

        s = log(s)
        s -= p * v_min
        
        return -s / p
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] grad):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v, v_min
        cdef double p = self.p
        # cdef double* grad_ptr = &grad[0]
        cdef double[::1] evals = self.evals

        if evals is None or evals.shape[0] != m:
            evals = self.evals = np.empty(m, 'd')
        
        v_min = double_max
        for i in range(m):
            v = X[i]
            if v < v_min:
                v_min = v

        s = 0
        for i in range(m):
            evals[i] = v = exp(p*(v_min - X[i]))
            s += v

        for i in range(m):
            grad[i] = evals[i] / s
    #
    @cython.final
    cdef double _gradient_j(self, double[::1] X, Py_ssize_t j):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v, v_min
        # cdef double* X_ptr = &X[0]
        cdef double p = self.p

        v_min = double_max
        for i in range(m):
            v = X[i]
            if v < v_min:
                v_min = v

        s = 0
        for i in range(m):
            s += exp(p*(v_min - X[i]))

        return exp(p*(v_min - X[j])) / s 
    #
    def _repr_latex_(self):
        return r"$||\mathbf{w}||_{%s}^{%s}=\sum_{i=0}^n w_i^{%s}$" % (self.p, self.p, self.p)

@cython.final
cdef class SoftMax(Func2):
    
    def __init__(self, p=1.0):
        self.p = p
        self.evals = None
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v, v_max
        cdef double p = self.p
        
        v_max = double_min
        for i in range(m):
            v = X[i]
            if v > v_max:
                v_max = v
        
        s = 0
        for i in range(m):
            s += exp(p*(X[i] - v_max))

        s = log(s)
        s = fma(p, v_max, s)
        
        return s / p
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] grad):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v, v_max
        cdef double p = self.p
        cdef double[::1] evals = self.evals

        if evals is None or evals.shape[0] != m:
            evals = self.evals = np.empty(m, 'd')
        
        v_max = double_min
        for i in range(m):
            v = X[i]
            if v > v_max:
                v_max = v

        s = 0
        for i in range(m):
            evals[i] = v = p*exp(p*(X[i] - v_max))
            s += v

        for i in range(m):
            grad[i] = evals[i] / s
    #
    @cython.final
    cdef double _gradient_j(self, double[::1] X, Py_ssize_t j):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v, v_max
        cdef double p = self.p

        v_max = double_min
        for i in range(m):
            v = X[i]
            if v > v_max:
                v_max = v

        s = 0
        for i in range(m):
            s += exp(p*(X[i] - v_max))

        return exp(p*(X[j] - v_max)) / s 
    #

@cython.final
cdef class PowerMax(Func2):
    
    def __init__(self, p=1.0):
        self.p = p
        self.evals = None
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v, v_max
        cdef double p = self.p
        
        v_max = double_min
        for i in range(m):
            v = fabs(X[i])
            if v > v_max:
                v_max = v
        
        s = 0
        for i in range(m):
            v = X[i]
            if v >= 0:
                s += pow(v / v_max, p)
            else:
                s += pow(-v / v_max, p)

        s = pow(s, 1/p)
        s *= v_max
        
        return s
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] grad):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v
        cdef double p = self.p
        cdef double[::1] evals = self.evals

        if evals is None or evals.shape[0] != m:
            evals = self.evals = np.empty(m, 'd')

        s = self._evaluate(X)
        
        for i in range(m):
            v = X[i] / s
            evals[i] = p * pow(v, p-1)
    #
    @cython.final
    cdef double _gradient_j(self, double[::1] X, Py_ssize_t j):
        cdef Py_ssize_t i
        cdef double s
        cdef double p = self.p

        s = self._evaluate(X)
        return p * pow(X[j] / s, p-1)
    #

@cython.final
cdef class SquareDiff1(Func2):
    #
    @cython.final
    cdef void _evaluate_items(self, double[::1] X, double[::1] Y):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double v
        cdef double *XX = &X[0]
        cdef double *YY = &X[0]
        # cdef int num_threads = inventory.get_num_threads()

        # for i in prange(1, m, nogil=True, schedule='static', num_threads=num_threads):
        Y[0] = 0
        for i in range(1,m):
            v = XX[i] - XX[i-1]
            YY[i] = 0.5 * v * v
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v
        cdef double *XX = &X[0]
        # cdef int num_threads = inventory.get_num_threads()

        s = 0
        # for i in prange(1, m, nogil=True, schedule='static', num_threads=num_threads):
        for i in range(1,m):
            v = XX[i] - XX[i-1]
            s += v * v

        return 0.5 * s
    #
    @cython.final
    cdef double _evaluate_ex(self, double[::1] X, double[::1] W):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v
        cdef double *XX = &X[0]
        # cdef int num_threads = inventory.get_num_threads()

        s = 0
        # for i in prange(1, m, nogil=True, schedule='static', num_threads=num_threads):
        for i in range(1,m):
            v = W[i] * (XX[i] - XX[i-1])
            s += v * v

        return 0.5 * s
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] grad):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double *XX = &X[0]
        cdef double *GG = &grad[0]
        # cdef int num_threads = inventory.get_num_threads()

        grad[0] = XX[1] - XX[0]
        grad[m-1] = XX[m-1] - XX[m-2]
        # for i in prange(1, m-1, nogil=True, schedule='static', num_threads=num_threads):
        for i in range(1, m-1):
            GG[i] = 2*XX[i] - XX[i-1] - XX[i+1]
    #
    @cython.final
    cdef void _gradient_ex(self, double[::1] X, double[::1] grad, double[::1] W):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double *XX = &X[0]
        cdef double *GG = &grad[0]
        # cdef int num_threads = inventory.get_num_threads()

        grad[0] = W[0] * (XX[1] - XX[0])
        grad[m-1] = W[m-1] * (XX[m-1] - XX[m-2])
        # for i in prange(1, m-1, nogil=True, schedule='static', num_threads=num_threads):
        for i in range(1, m-1):
            GG[i] = W[i] * (2*XX[i] - XX[i-1] - XX[i+1])

#from pybaselines.utils import difference_matrix
#diff_matrix = difference_matrix(data_size, 2)
#output = (diff_matrix.T @ diff_matrix).todia().data[::-1]
#if lower_only:
#    output = output[2:]

# @cython.final
# cdef class SquareDiff2(Func2):
#     #
#     @cython.final
#     cdef void _evaluate_items(self, double[::1] X, double[::1] Y):
#         cdef Py_ssize_t i, m = X.shape[0]
#         cdef double v
#         cdef double *XX = &X[0]
#         cdef double *YY = &X[0]
#         # cdef int num_threads = inventory.get_num_threads()

#         v = -2*XX[0] + XX[1]
#         YY[0] = 0.5 * v * v
#         # for i in prange(1, m-1, nogil=True, schedule='static', num_threads=num_threads):
#         for i in range(1, m-1):
#             v = XX[i] - 2*XX[i+1] + XX[i+2]
#             YY[i] = 0.5 * v * v
#         v = -2*XX[m-1] + XX[m-2]
#         YY[m-1] = 0.5 * v * v
#     #
#     @cython.final
#     cdef double _evaluate(self, double[::1] X):
#         cdef Py_ssize_t i, m = X.shape[0]
#         cdef double v, s
#         cdef double *XX = &X[0]
#         # cdef int num_threads = inventory.get_num_threads()

#         v = -2*XX[0] + XX[1]
#         s = v * v
#         # for i in prange(1, m-1, nogil=True, schedule='static', num_threads=num_threads):
#         for i in range(1, m-1):
#             v = XX[i] - 2*XX[i+1] + XX[i+2]
#             s += v * v
#         v = -2*XX[m-1] + XX[m-2]
#         s += v * v

#         return 0.5 * s
#     #
#     @cython.final
#     cdef double _evaluate_ex(self, double[::1] X, double[::1] W):
#         cdef Py_ssize_t i, m = X.shape[0]
#         cdef double v, s
#         cdef double *XX = &X[0] 
#         cdef double *WW = &W[0]
#         # cdef int num_threads = inventory.get_num_threads()

#         v = -2*XX[0] + XX[1]
#         s = WW[0] * v * v
#         # for i in prange(1, m-1, nogil=True, schedule='static', num_threads=num_threads):
#         for i in range(1, m-1):
#             v = XX[i] - 2*XX[i+1] + XX[i+2]
#             s += WW[i] * v * v
#         v = -2*XX[m-1] + XX[m-2]
#         s += WW[m-1] * v * v

#         return 0.5 * s
#     #
#     @cython.final
#     cdef void _gradient(self, double[::1] X, double[::1] grad):
#         cdef Py_ssize_t i, m = X.shape[0]
#         cdef double s, v
#         cdef double *XX = &X[0]
#         cdef double *GG = &grad[0]
#         # cdef int num_threads = inventory.get_num_threads()

#         GG[0] = -XX[0] - 2*XX[1] + XX[2]
#         GG[1] = -2*XX[0] + 5*XX[1] - 4*XX[2] + XX[3]
#         GG[m-1] = XX[m-1] - 2*XX[m-2] + XX[m-3]
#         GG[m-2] = -2*XX[m-1] + 5*XX[m-2] - 4*XX[m-3] + XX[m-4]
#         # for i in prange(2, m-2, nogil=True, schedule='static', num_threads=num_threads):
#         for i in range(2, m-2):
#             GG[i] = XX[i-2] - 4*XX[i-1] + 6*XX[i] - 4*XX[i+1] + XX[i+2]
#     #
#     @cython.final
#     cdef void _gradient_ex(self, double[::1] X, double[::1] grad, double[::1] W):
#         cdef Py_ssize_t i, m = X.shape[0]
#         cdef double s, v
#         cdef double *XX = &X[0]
#         cdef double *WW = &W[0]
#         cdef double *GG = &grad[0]
#         # cdef int num_threads = inventory.get_num_threads()


#         YY[0] = -2*XX[0] + XX[1]
#         # for i in prange(1, m-1, nogil=True, schedule='static', num_threads=num_threads):
#         for i in range(1, m-1):
#             YY[i] = XX[i] - 2*XX[i+1] + XX[i+2]
#         YY[m-1] = -2*XX[m-1] + XX[m-2]
        
#         GG[0] = WW[0]*YY[0]
#         GG[1] = -2*WW[0]*YY[0] + WW[1]*YY[1]

#         # for i in prange(2, m-2, nogil=True, schedule='static', num_threads=num_threads):
#         for i in range(2, m-2):
#             GG[i] = WW[i-1]*YY[i-1] - 2*WW[i]*YY[i] + WW[i+1]*YY[i+1]

#         GG[m-1] = WW[m-1]*YY[m-1]
#         GG[m-2] = -2*WW[m-1]*YY[m-1] + WW[m-2]*YY[m-2]

@cython.final
cdef class FuncDiff2(Func2):
    #
    def __init__(self, Func func):
        self.func = func
        self.temp_array = None
    #
    cdef void _evaluate_diff2(self, double *XX, double *YY, const Py_ssize_t m) noexcept nogil:
        cdef Py_ssize_t i
        # cdef int num_threads = inventory.get_num_threads()

        YY[0] = 0
        YY[m-1] = 0
        # for i in prange(1, m-1, nogil=True, schedule='static', num_threads=num_threads):
        for i in range(1, m-1):
            YY[i] = XX[i-1] - 2*XX[i] + XX[i+1]
    #
    @cython.final
    cdef void _evaluate_items(self, double[::1] X, double[::1] Y):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double v
        cdef double *XX = &X[0]
        cdef double *YY = &Y[0]
        # cdef int num_threads = inventory.get_num_threads()

        self._evaluate_diff2(XX, YY, m)
        self.func._evaluate_array(YY, YY, m)
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        cdef Func func = self.func
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double v, s
        cdef double *XX = &X[0]
        # cdef int num_threads = inventory.get_num_threads()

        s = 0
        # for i in prange(1, m-1, nogil=True, schedule='static', num_threads=num_threads):
        for i in range(1, m-1):
            v = XX[i-1] - 2*XX[i] + XX[i+1]
            s += func._evaluate(v)

        return s
    #
    @cython.final
    cdef double _evaluate_ex(self, double[::1] X, double[::1] W):
        cdef Func func = self.func
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double v, s
        cdef double *XX = &X[0] 
        cdef double *WW = &W[0]
        # cdef int num_threads = inventory.get_num_threads()

        s = 0
        # for i in prange(1, m-1, nogil=True, schedule='static', num_threads=num_threads):
        for i in range(1,m-1):
            v = XX[i-1] - 2*XX[i] + XX[i+1]
            s += WW[i] * func._evaluate(v)

        return s
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] G):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v
        cdef double *XX = &X[0]
        cdef double *GG = &G[0]
        # cdef int num_threads = inventory.get_num_threads()
        cdef double[::1] temp_array = self.temp_array
        cdef double* TT

        if temp_array is None or temp_array.shape[0] != m:
            self.temp_array = temp_array = np.empty(m, "d")

        TT = &temp_array[0]

        self._evaluate_diff2(XX, TT, m)
        self.func._derivative_array(TT, TT, m)

        GG[0] = 0
        GG[m-1] = 0
        # for i in prange(2, m-2, nogil=True, schedule='static', num_threads=num_threads):
        for i in range(1, m-1):
            GG[i] = TT[i-1] - 2*TT[i] + TT[i+1]        
    #
    @cython.final
    cdef void _gradient_ex(self, double[::1] X, double[::1] G, double[::1] W):
        cdef Py_ssize_t i, m = X.shape[0]
        cdef double s, v
        cdef double *XX = &X[0]
        cdef double *WW = &W[0]
        cdef double *GG = &G[0]
        # cdef int num_threads = inventory.get_num_threads()
        cdef double[::1] temp_array = self.temp_array
        cdef double* TT

        if temp_array is None or temp_array.shape[0] != m:
            self.temp_array = temp_array = np.empty(m, "d")

        TT = &temp_array[0]
                
        self._evaluate_diff2(XX, TT, m)
        self.func._derivative_array(TT, TT, m)
        
        GG[0] = 0
        GG[m-1] = 0

        # for i in prange(1, m-1, nogil=True, schedule='static', num_threads=num_threads):
        for i in range(1, m-1):
            GG[i] = WW[i-1]*TT[i-1] - 2*WW[i]*TT[i] + WW[i+1]*TT[i+1]

@cython.final
cdef class Rosenbrok(Func2):
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        return 10. * (X[1] - X[0]**2)**2 + 0.1*(1. - X[0])**2
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] grad):
        grad[0] = -40. * (X[1] - X[0]**2) * X[0] - 0.2 * (1. - X[0])
        grad[1] = 20. * (X[1] - X[0]**2)
        
        
@cython.final
cdef class Himmelblau(Func2):
    #
    @cython.final
    cdef double _evaluate(self, double[::1] X):
        return (X[0]**2 + X[1] - 11)**2 + (X[0] + X[1]**2 - 7)**2
    #
    @cython.final
    cdef void _gradient(self, double[::1] X, double[::1] grad):
        grad[0] = 4*(X[0]**2 + X[1] - 11) * X[0] + 2*(X[0] + X[1]**2 - 7)
        grad[1] = 2*(X[0]**2 + X[1] - 11) + 4*(X[0] + X[1]**2 - 7) * X[1]
