from builtins import next
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle
from numpy.linalg import svd


def plot(ax, data, labels=None, title="Unknown file"):
    colors = cycle('brmyk')
    markers = cycle('ospP*h')
    if labels is None:
        labels = np.zeros(len(data))
    ulabels = set(labels)
    cols = dict()
    marks = dict()
    for label in ulabels:
        cols[label] = next(colors)
        marks[label] = next(markers)
    maxx, minx = max(data[:, 0]), min(data[:, 0])
    range_x = maxx - minx
    maxy, miny = max(data[:, 1]), min(data[:, 1])
    range_y = maxy - miny
    # fig, ax = plt.subplots()
    for label in np.unique(labels):
        ax.scatter(data[labels == label][:, 0], data[labels == label][:, 1],
                   marker=marks[label],
                   color=cols[label])
        # ax.annotate(str(labels[p]), (data[p, 0], data[p, 1]))

    # ax.plot([minx, maxx], [0, 0], color="black", linewidth=0.5)
    # ax.plot([0, 0], [miny, maxy], color="black", linewidth=0.5)
    ax.set_title(title)
    ax.set_xlim(minx - 0.2 * range_x, maxx + 0.2 * range_x)
    ax.set_ylim(miny - 0.2 * range_y, maxy + 0.2 * range_y)
    ax.grid(linestyle='dotted')
    # ax.set_aspect('equal', adjustable='box')


def plot_svd(ax, data, labels=None, title="Unknown file", normalize=True):
    if normalize:
        data = data - np.mean(data, axis=0)
        data = data / (np.max(data, axis=0) - np.min(data, axis=0))
    u, s, v = svd(data)
    s[1] = -s[1]
    plot(ax, u[:, 0:2] * s[0:2], title="SVD", labels=labels)
