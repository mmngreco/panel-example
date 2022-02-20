import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import panel as pn
from functools import lru_cache

pd.DataFrame.__hash__ = lambda self: id(self)  # HACK: make cacheable


PRIMARY_COLOR = "#0072B5"
SECONDARY_COLOR = "#94EA84"


@lru_cache()
def load_data():
    data_url = "https://cdn.jsdelivr.net/gh/holoviz/panel@master/examples/assets/occupancy.csv"
    data = pd.read_csv(data_url, parse_dates=["date"]).set_index("date")
    return data


def mpl_plot(avg, highlight):
    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot()
    avg.plot(ax=ax, c=PRIMARY_COLOR)
    if len(highlight):
        highlight.plot(style="o", ax=ax, c=SECONDARY_COLOR)
    plt.tight_layout()
    return fig


@lru_cache()
def find_outliers(
    data, variable="Temperature", window=20, sigma=10, view_fn=mpl_plot
):
    avg = data[variable].rolling(window=window).mean()
    residual = data[variable] - avg
    std = residual.rolling(window=window).std()
    outliers = np.abs(residual) > std * sigma
    return view_fn(avg, avg[outliers])

# ============================================================================
# Panel
# ============================================================================

data = load_data()

pn.extension(sizing_mode="stretch_width", template="fast")

# Define labels and widgets
pn.pane.Markdown("Variable").servable(area="sidebar")

variable = pn.widgets.RadioBoxGroup(
    name="DF Columns",
    value="Temperature",
    options=list(data.columns),
).servable(area="sidebar")

window = pn.widgets.IntSlider(
    name="Window", value=20, start=1, end=60
).servable(area="sidebar")

# Make your functions interactive, i.e. react to changes in widget values
ifind_outliers = pn.bind(find_outliers, data, variable, window, 10)

# Layout the interactive functions
pn.panel(ifind_outliers, sizing_mode="scale_both").servable()

# Configure the template
pn.state.template.param.update(
    site="Panel",
    title="Example",
    accent_base_color=PRIMARY_COLOR,
    header_background=PRIMARY_COLOR,
)


