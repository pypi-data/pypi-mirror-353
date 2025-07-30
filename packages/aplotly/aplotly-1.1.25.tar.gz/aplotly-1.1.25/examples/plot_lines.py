import numpy as np
import pandas as pd

from aplotly.plots import plot_multiple_lines

fig = plot_multiple_lines(
    [pd.Series(np.random.rand(100), index=np.arange(100)) for _ in range(8)],
    labels=["Test 1", "Test 2", "Test 3", "Test 4", "Test 5", "Test 6", "Test 7", "Test 8"],
    styles=[{"shape": "hv"}, {"shape": "vh"}, {"shape": "linear"}, {"shape": "hv"}, {"shape": "vh"}, {"shape": "linear"}, {"shape": "hv"}, {"shape": "vh"}],
    xlabel="X",
    ylabel="Y",
    color_palette="contrast",
    fade_secondary_lines=True,
)
fig.show()
