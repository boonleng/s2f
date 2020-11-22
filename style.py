'''
    Use dark theme with jupyter theme tool:

    jt -t monokai -tfs 14 -ofs 11 -nfs 10 -dfs 12 -fs 11 -lineh 150 -cellw 100%

    To reset:

    jt -r
'''

import matplotlib
import matplotlib.pyplot

from cycler import cycler

context_properties = {
    'figure.figsize': (8, 4.5),
    'figure.dpi': 144,
    'font.family': 'serif',
    'font.serif': ['Arial'],
    'font.sans-serif': ['System Font', 'Verdana', 'Arial'],
    'axes.axisbelow': True,
    'axes.linewidth': 1.0,
    'axes.titlepad': 12.0,
    'figure.titlesize': 'x-large',
    'xtick.direction': 'in',
    'xtick.major.pad': 9.0,
    'xtick.major.size': 4.0,
    'xtick.major.width': 1.0,
    'ytick.direction': 'in',
    'ytick.major.pad': 7.5,
    'grid.linewidth': 0.5,
}
white = (0.85, 0.85, 0.85)
dark_context_properties = {
    'figure.facecolor': (0.0, 0.0, 0.0, 0.0),
    'axes.facecolor': (0.2, 0.2, 0.2, 0.75),
    'axes.edgecolor': white,
    'axes.labelcolor': white,
    'axes.prop_cycle': cycler('color', [
        '#3399ff',
        '#99ff00',
        '#ffcc00',
        '#ff3399',
        '#9933ff',
        '#33ffff',
    ]),
    'hatch.color': white,
    'text.color': white,
    'xtick.color': white,
    'ytick.color': white,
    'grid.color': (0.35, 0.35, 0.35)
}
black = (0.1, 0.1, 0.1)
light_context_properties = {
    'figure.facecolor': (1.0, 1.0, 1.0, 0.0),
    'axes.facecolor': (1.0, 1.0, 1.0, 0.8),
    'axes.edgecolor': black,
    'axes.labelcolor': black,
    'axes.prop_cycle': cycler('color', [
        '#1f77b4',
        '#ff7f0e',
        '#2ca02c',
        '#d62728',
        '#9467bd',
        '#8c564b',
        '#e377c2',
        '#7f7f7f',
        '#bcbd22',
        '#17becf'
    ]),
    'hatch.color': black,
    'text.color': black,
    'xtick.color': black,
    'ytick.color': black,
    'grid.color': (0.7, 0.7, 0.7)
}
context_properties.update(light_context_properties)

def use_dark_theme():
    context_properties.update(dark_context_properties)
    matplotlib.pyplot.rc_context(context_properties)
    matplotlib.pyplot.rcParams.update(context_properties)

def use_light_theme():
    context_properties.update(light_context_properties)
    matplotlib.pyplot.rc_context(context_properties)
    matplotlib.pyplot.rcParams.update(context_properties)
