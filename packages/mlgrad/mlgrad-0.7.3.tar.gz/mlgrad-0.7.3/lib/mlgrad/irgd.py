# coding: utf-8

# The MIT License (MIT)
#
# Copyright (c) <2015-2021> <Shibzukhov Zaur, szport at gmail dot com>
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

from sys import float_info

import numpy as np

class IRGD:
    #
    def __init__(self, gd, weights, tol=1.0e-5, n_iter=100, h_anneal=0.99, M=12, callback=None):
        """
        """
        self.gd = gd
        
        self.tol = tol
        self.n_iter = n_iter
        self.M = M
        self.m = 0

        self.param_best = np.zeros(len(self.gd.risk.param), dtype='d')
#         self.param_prev = np.zeros((m,), dtype='d')
        
        self.h_anneal = h_anneal
        
        self.callback = callback
        
        self.weights = weights
        
        self.lval = self.lval1 = self.lval2 = 0
        
        self.completed = False
        
        # self.K = 0
        # self.m = 0
        
        self.lvals = []
        #self.qvals = []
        self.n_iters = []
        
        self.K = 0
        
    #
    @property
    def risk(self):
        return self.gd.risk

    @property
    def sample_weights(self):
        return np.asarray(self.weights.weights)    
    #
    def fit(self):
        risk = self.gd.risk
                           
        self.weights.init()
        self.weights.eval_weights()
        risk.use_weights(self.weights.weights)

        self.lval_min = self.lval = self.weights.get_qvalue()
        self.lval_min_prev = self.lval_min * 2
        Q = 1 + abs(self.lval_min)
        # print(self.lval)
        self.param_best = risk.model.param.copy()
        
        if self.callback is not None:
            self.callback(self)

        m = 0
        M = self.M
        tol = self.tol
        for K in range(self.n_iter):     
            self.lval_prev = self.lval
            # print(K)
            self.gd.fit()
            
            self.n_iters.append(self.gd.K)

            if self.callback is not None:
                self.callback(self)

            self.weights.eval_weights()
            risk.use_weights(self.weights.weights)
            
            self.lval = self.weights.get_qvalue()
            # print(self.lval)
                
            if abs(self.lval - self.lval_prev) / Q < tol:
                self.completed = 1
            
            elif abs(self.lval - self.lval_min) / Q < tol:
                self.completed = 1

            elif abs(self.lval - self.lval_min_prev) / Q < tol:
                if m > 7:
                    self.completed = 1
                else:
                    m += 1

            if self.lval < self.lval_min:
                self.param_best = risk.param.copy()
                self.lval_min_prev = self.lval_min
                self.lval_min = self.lval
                Q = 1 + abs(self.lval_min)
                m = 0
            elif self.lval < self.lval_min_prev:
                self.lval_min_prev = self.lval

            # if self.lval > self.lval_prev:
            #     self.gd.h_rate.h *= self.h_anneal
            #     self.gd.h_rate.init()

            if m > M:
                self.completed = 1

            self.lvals.append(self.lval)

            if self.completed:
                break
        #
        self.K += K
        self.finalize()

    #
    def finalize(self):
        risk = self.gd.risk

        # print(self.lval_best)
        risk.model.param[:] = self.param_best
    #
    def stop_condition(self):
        
        if abs(self.lval - self.lval_best) / (1 + abs(self.lval_best)) < self.tol:
            return True

        if abs(self.lval_best_prev - self.lval_best) / (1 + abs(self.lval_best)) < self.tol:
            return True
        
        return False

