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


import numpy as np
import matplotlib.pyplot as plt

def plot_hist_and_rank_distribution(Y, bins=40):
    plt.figure(figsize=(12,5))
    plt.subplot(1,2,1)
    plt.title(r"Histogram")
    plt.hist(Y, bins=bins, rwidth=0.9)
    plt.ylabel(r"$p$")
    plt.xlabel(r"$y$")
    plt.minorticks_on()
    plt.subplot(1,2,2)
    plt.title("Rank distribution")
    plt.plot(sorted(Y), marker='o', markersize=3)
    plt.ylabel(r"$y_k$")
    plt.xlabel(r"$k$ (rank)")
    plt.tight_layout()
    plt.show()


def plot_losses_and_errors(alg, X, Y, fname=None, logscale=False, lang='en'):
    err = np.abs(Y - alg.risk.model.evaluate(X))
    plt.figure(figsize=(10,5))
    plt.subplot(1,2,1)
    if lang == 'en':
        plt.title('Fit curve')
        plt.xlabel('step')
        plt.ylabel('mean of losses')
    else:
        plt.title('Кривая обучения')
        plt.xlabel('шаг')
        plt.ylabel('средние потери')
    plt.plot(alg.lvals, color='k')
    if logscale:
        plt.gca().set_yscale('log')
    plt.minorticks_on()
    plt.subplot(1,2,2)
    if lang == 'en':
        plt.title('Errors')
        plt.xlabel('error rank')
        plt.ylabel('error value')
    else:
        plt.title('Ошибки')
        plt.xlabel('Ранг ошибки')
        plt.ylabel('Значение ошибки')
    plt.plot(sorted(err), marker='o', markersize='5', color='k')
    plt.minorticks_on()
    plt.tight_layout()
    if fname:
        plt.savefig(fname)
    plt.show()

def plot_losses(alg, fname=None, logscale=False, lang='en', ax=None):
    if ax is None:
        ax = plt.gca()
    
    if lang == 'en':
        ax.set_title('Losses curve')
        ax.set_xlabel('step')
        ax.set_ylabel('Mean of losses')
    else:
        ax.set_title('Кривая потерь')
        ax.set_xlabel('шаг')
        ax.set_ylabel('Средние потери')
    ax.plot(alg.lvals, color='k')
    if logscale:
        ax.set_yscale('log')
    ax.minorticks_on()
    if fname:
        plt.savefig(fname)
    
def plot_errors(mod, Xs, Y, fname=None, lang='en', ax=None):
    import numpy as np
    import matplotlib.pyplot as plt

    err = np.abs(Y - mod.evaluate(Xs))
    if ax is None:
        ax = plt.gca()
    if lang == 'en':
        ax.set_title('Errors')
        ax.set_xlabel('error rank')
        ax.set_ylabel('error value')
    else:
        ax.set_title('Ошибки')
        ax.set_xlabel('Ранг ошибки')
        ax.set_ylabel('Значение ошибки')
    ax.plot(sorted(err), marker='o', markersize=4, color='k')
    ax.minorticks_on()
    if fname:
        plt.savefig(fname)
    
def plot_errors_hist(mod, X, Y, fname=None, lang='en', hist=False, bins=20, 
                     density=False, ax=None):
    import numpy as np
    import matplotlib.pyplot as plt

    err = np.abs(Y - mod.evaluate(X))
    if ax is None:
        ax = plt.gca()
    if lang == 'en':
        ax.set_title('Errors hist')
        ax.set_xlabel('errors value')
        # ax.set_ylabel('error value')
    else:
        ax.set_title('Гистограмма ошибок')
        ax.set_xlabel('Величина ошибки')
        # ax.set_ylabel('Значение ошибки')
    ax.hist(err, bins=bins, color='k', rwidth=0.9, density=density)
    ax.minorticks_on()
    if fname:
        plt.savefig(fname)
    
def plot_yy(mod, Xs, Y, title="", b=0.1, ax=None):

    if ax is None:
        ax = plt.gca()

    Yp = mod.evaluate(Xs)
    E = np.abs(Y - Yp) / np.abs(Y)
    c = sum(E < b) / len(E) * 100
    ymax, ymin = np.max(Y), np.min(Y)
    ypmax, ypmin = np.max(Yp), np.min(Yp)
    ymax = max(ymax, ypmax)
    ymin = min(ymin, ypmin)
    ax.set_title("Y-Y plot")
    ax.plot([ymin, ymax], [ymin, ymax], color='k', linewidth=0.66)
    ax.fill_between([ymin, ymax], [ymin-b, ymax-b], [ymin+b, ymax+b], color='LightGray')
    ax.scatter(Y, Yp, c='k', s=12, label=r'$\{|err|<%.2f\}\ \to\ %s$ %%' % (b, int(c)))
    if title:
        ax.set_title(title)
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(ymin, ymax)
    ax.set_xlabel("original")
    ax.set_ylabel("predicted")
    ax.legend()

def plot_sample_weights(alg, label=None, ax=None):
    if ax is None:
        ax = plt.gca()
    ax.plot(sorted(alg.sample_weights), label=label, marker='o')

def plot_cls_function(mod, X, Y, sorted=False, ax=None):
    N = len(Y)
    Y_p = mod.evaluate(X)

    if ax is None:
        ax = plt.gca()
    
    if sorted:
        I_p = np.argsort(Y_p)
        ax.scatter(range(len(Y)), Y_p[I_p], c=Y[I_p], s=25)
    else:        
        ax.scatter(range(len(Y)), Y_p, c=Y, s=25)

    ax.hlines(0, -5, N+5, colors='k', linewidths=0.75)
    ax.minorticks_on()
    ax.grid(1)
    ax.set_xlim(-5, N+5)
    ax.set_xlabel(r'$k$ (номер точки)')
    ax.set_ylabel(r'$f(\mathbf{x}_k)$')
    plt.title(r"Распределение значений функции $f(x)$")

def plot_contour(callable, xrange, yrange, offset=[0,0], levels=None, colors='k', linewidths=1.0, linestyles="solid"):
    linspace = np.linspace

    offset = np.array(offset, "d")
    xmin, xmax = xrange
    ymin, ymax = yrange
    xx, yy = np.meshgrid(linspace(xmin, xmax, 100), linspace(ymin, ymax, 100))
    xy = np.c_[xx.ravel(), yy.ravel()]
    zz = callable(xy)
    zz = zz.reshape(xx.shape)
    cs = plt.contour(xx+offset[0], yy+offset[1], zz, levels=levels, colors=colors, linewidths=linewidths, linestyles=linestyles)
    plt.clabel(cs, colors=colors)
    