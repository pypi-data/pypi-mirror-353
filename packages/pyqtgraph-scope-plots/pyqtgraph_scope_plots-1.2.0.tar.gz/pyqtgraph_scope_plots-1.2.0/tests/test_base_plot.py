# Copyright 2025 Enphase Energy, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from io import StringIO
from typing import cast

import pytest
import pyqtgraph as pg
from PySide6.QtGui import QColor
from pytestqt.qtbot import QtBot

from pyqtgraph_scope_plots.plots_table_widget import PlotsTableWidget
from pyqtgraph_scope_plots.multi_plot_widget import (
    MultiPlotWidget,
    MultiPlotStateModel,
    LinkedMultiPlotStateModel,
    PlotWidgetModel,
)
from .test_util import assert_cast
from pyqtgraph_scope_plots.util import not_none


@pytest.fixture()
def plot(qtbot: QtBot) -> PlotsTableWidget:
    """Creates a signals plot with multiple data items"""
    plot = PlotsTableWidget()
    plot._set_data_items(
        [
            ("0", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
            ("1", QColor("orange"), MultiPlotWidget.PlotType.DEFAULT),
            ("2", QColor("blue"), MultiPlotWidget.PlotType.DEFAULT),
        ]
    )
    plot._set_data(
        {
            "0": ([0, 0.1, 1, 2], [0.01, 1, 1, 0]),
            "1": ([0, 1, 2], [0.5, 0.25, 0.5]),
            "2": ([0, 1, 2], [0.7, 0.6, 0.5]),
        }
    )
    qtbot.addWidget(plot)
    plot.show()
    qtbot.waitExposed(plot)
    return plot


def plot_item(widget: PlotsTableWidget, index: int) -> pg.PlotItem:
    return assert_cast(pg.PlotItem, assert_cast(pg.PlotWidget, widget._plots.widget(index)).getPlotItem())


def test_num_plots_table(qtbot: QtBot, plot: PlotsTableWidget) -> None:
    qtbot.waitUntil(lambda: plot._plots.count() == 3)
    assert plot._table.rowCount() == 3
    assert plot._table.item(0, plot._table.COL_NAME).text() == "0"
    assert plot._table.item(1, plot._table.COL_NAME).text() == "1"
    assert plot._table.item(2, plot._table.COL_NAME).text() == "2"

    plot._set_data_items(
        [
            ("0", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
            ("1", QColor("orange"), MultiPlotWidget.PlotType.DEFAULT),
            ("2", QColor("blue"), MultiPlotWidget.PlotType.DEFAULT),
            ("3", QColor("green"), MultiPlotWidget.PlotType.DEFAULT),
        ]
    )
    qtbot.waitUntil(lambda: plot._plots.count() == 4)
    assert plot._table.rowCount() == 4
    assert plot._table.item(0, plot._table.COL_NAME).text() == "0"
    assert plot._table.item(1, plot._table.COL_NAME).text() == "1"
    assert plot._table.item(2, plot._table.COL_NAME).text() == "2"
    assert plot._table.item(3, plot._table.COL_NAME).text() == "3"

    plot._set_data_items(
        [
            ("0", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
            ("3", QColor("green"), MultiPlotWidget.PlotType.DEFAULT),
        ]
    )
    qtbot.waitUntil(lambda: plot._plots.count() == 2)
    assert plot._table.rowCount() == 2
    assert plot._table.item(0, plot._table.COL_NAME).text() == "0"
    assert plot._table.item(1, plot._table.COL_NAME).text() == "3"


def test_empty_default_plots(qtbot: QtBot, plot: PlotsTableWidget) -> None:
    plot._set_data_items([])
    qtbot.waitUntil(lambda: plot._plots.count() == 1)
    assert plot._table.rowCount() == 0


def test_plot_merge(qtbot: QtBot, plot: PlotsTableWidget) -> None:
    qtbot.waitUntil(lambda: plot._plots.count() == 3)  # wait for plots to be ready

    plot._plots._merge_data_into_item(["0"], 1)  # merge
    qtbot.waitUntil(lambda: plot._plots.count() == 2)  # wait for widgets to merge
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 2
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(1)).getPlotItem()).listDataItems()) == 1
    assert plot._table.rowCount() == 3  # signals table should not change
    assert plot._table.item(0, plot._table.COL_NAME).text() == "0"
    assert plot._table.item(1, plot._table.COL_NAME).text() == "1"
    assert plot._table.item(2, plot._table.COL_NAME).text() == "2"

    plot._plots._merge_data_into_item(["0"], 1)  # move
    qtbot.waitUntil(lambda: plot._plots.count() == 2)
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 1
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(1)).getPlotItem()).listDataItems()) == 2
    assert plot._table.rowCount() == 3  # signals table should not change
    assert plot._table.item(0, plot._table.COL_NAME).text() == "0"
    assert plot._table.item(1, plot._table.COL_NAME).text() == "1"
    assert plot._table.item(2, plot._table.COL_NAME).text() == "2"

    plot._plots._merge_data_into_item(["1"], 1)  # merge all
    qtbot.waitUntil(lambda: plot._plots.count() == 1)
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 3
    assert plot._table.rowCount() == 3  # signals table should not change
    assert plot._table.item(0, plot._table.COL_NAME).text() == "0"
    assert plot._table.item(1, plot._table.COL_NAME).text() == "1"
    assert plot._table.item(2, plot._table.COL_NAME).text() == "2"

    plot._plots._merge_data_into_item(["2"], 0, insert=True)  # insert at top
    qtbot.waitUntil(lambda: plot._plots.count() == 2)  # new plot created
    assert plot._table.rowCount() == 3  # signals table should not change
    assert plot._table.item(0, plot._table.COL_NAME).text() == "0"
    assert plot._table.item(1, plot._table.COL_NAME).text() == "1"
    assert plot._table.item(2, plot._table.COL_NAME).text() == "2"

    plot._plots._merge_data_into_item(["0"], 2, insert=True)  # insert at bottom
    qtbot.waitUntil(lambda: plot._plots.count() == 3)


def test_plot_merge_multi(qtbot: QtBot, plot: PlotsTableWidget) -> None:
    qtbot.waitUntil(lambda: plot._plots.count() == 3)  # wait for plots to be ready

    plot._plots._merge_data_into_item(["0", "1"], 0)  # merge into self, including self
    qtbot.waitUntil(lambda: plot._plots.count() == 2)  # wait for widgets to merge
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 2
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(1)).getPlotItem()).listDataItems()) == 1

    plot._plots._merge_data_into_item(["0", "1"], 1)  # merge into other, not including self
    qtbot.waitUntil(lambda: plot._plots.count() == 1)  # wait for widgets to merge
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 3

    plot._plots._merge_data_into_item(["1", "2"], 2, insert=True)  # insert at bottom
    qtbot.waitUntil(lambda: plot._plots.count() == 2)
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 1
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(1)).getPlotItem()).listDataItems()) == 2

    plot._plots._merge_data_into_item(["0", "1", "2"], 2, insert=True)  # insert all
    qtbot.waitUntil(lambda: plot._plots.count() == 1)
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 3


def test_invalid_plot_merge(qtbot: QtBot, plot: PlotsTableWidget) -> None:
    plot._set_data_items(
        [
            ("0", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
            ("1", QColor("orange"), MultiPlotWidget.PlotType.DEFAULT),
            ("2", QColor("blue"), MultiPlotWidget.PlotType.DEFAULT),
            ("3", QColor("cyan"), MultiPlotWidget.PlotType.ENUM_WAVEFORM),
            ("4", QColor("brown"), MultiPlotWidget.PlotType.ENUM_WAVEFORM),
        ]
    )

    qtbot.waitUntil(lambda: plot._plots.count() == 5)  # wait for plots to be ready

    plot._plots._merge_data_into_item(["3"], 0)  # invalid merge, different types
    plot._plots._merge_data_into_item(["0"], 3)  # invalid merge, different types
    plot._plots._merge_data_into_item(["3"], 4)  # can't merge enums
    plot._plots._merge_data_into_item(["4"], 3)  # can't merge enums

    assert plot._plots.count() == 5  # check nothing changes


def test_plot_remove(qtbot: QtBot, plot: PlotsTableWidget) -> None:
    plot._plots.remove_plot_items(["1"])
    qtbot.waitUntil(lambda: plot._plots.count() == 2)  # plot removed

    plot._plots._merge_data_into_item(["2"], 0)  # merge all into top
    qtbot.waitUntil(lambda: plot._plots.count() == 1)
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 2

    plot._plots.remove_plot_items(["0"])
    qtbot.waitUntil(
        lambda: len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 1
    )

    plot._plots.remove_plot_items(["2"])  # delete the last plot, the empty plot should appear
    qtbot.waitUntil(
        lambda: len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 0
    )


def test_plot_save(qtbot: QtBot, plot: PlotsTableWidget) -> None:
    qtbot.waitUntil(
        lambda: cast(MultiPlotStateModel, plot._plots._dump_model([])).plot_widgets
        == [
            PlotWidgetModel(data_items=["0"], y_range="auto"),
            PlotWidgetModel(data_items=["1"], y_range="auto"),
            PlotWidgetModel(data_items=["2"], y_range="auto"),
        ]
    )

    plot._plots._merge_data_into_item(["0"], 1)  # merge
    qtbot.waitUntil(
        lambda: cast(MultiPlotStateModel, plot._plots._dump_model([])).plot_widgets
        == [PlotWidgetModel(data_items=["1", "0"], y_range="auto"), PlotWidgetModel(data_items=["2"], y_range="auto")]
    )

    plot._plots._merge_data_into_item(["2"], 0)  # merge
    qtbot.waitUntil(
        lambda: cast(MultiPlotStateModel, plot._plots._dump_model([])).plot_widgets
        == [PlotWidgetModel(data_items=["1", "0", "2"], y_range="auto")]
    )


def test_plot_restore(qtbot: QtBot, plot: PlotsTableWidget) -> None:
    model = cast(MultiPlotStateModel, plot._plots._dump_model([]))
    model.plot_widgets = [PlotWidgetModel(data_items=["0", "1", "2"])]
    plot._plots._load_model(model)
    plot._plots.set_data(plot._plots._data)  # bulk update that happens at top level
    qtbot.waitUntil(lambda: plot._plots.count() == 1)
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 3

    model.plot_widgets = [PlotWidgetModel(data_items=["0"]), PlotWidgetModel(data_items=["2"])]
    plot._plots._load_model(model)
    plot._plots.set_data(plot._plots._data)  # bulk update that happens at top level
    qtbot.waitUntil(lambda: plot._plots.count() == 2)
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 1
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(1)).getPlotItem()).listDataItems()) == 1

    model.plot_widgets = []  # test empty case
    plot._plots._load_model(model)
    plot._plots.set_data(plot._plots._data)  # bulk update that happens at top level
    qtbot.waitUntil(lambda: plot._plots.count() == 1)  # should leave the empty widget intact
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 0


def test_plot_restore_range(qtbot: QtBot, plot: PlotsTableWidget) -> None:
    model = cast(MultiPlotStateModel, plot._plots._dump_model([]))
    model.plot_widgets = [PlotWidgetModel(data_items=["0"])]
    model.x_range = (-10, 42)
    plot._plots._load_model(model)
    qtbot.waitUntil(
        lambda: cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).getViewBox().viewRange()[0]
        == [-10, 42]
    )
    assert (
        not cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem())
        .getViewBox()
        .autoRangeEnabled()[0]
    )

    model.x_range = "auto"
    plot._plots._load_model(model)
    qtbot.waitUntil(
        lambda: cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem())
        .getViewBox()
        .autoRangeEnabled()[0]
        == True
    )


def test_no_excessive_plots(qtbot: QtBot, plot: PlotsTableWidget) -> None:
    # check that the default limit for plot instantiation works
    plot._set_data_items(
        [
            ("A", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
            ("B", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
            ("C", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
            ("D", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
            ("E", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
            ("F", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
            ("G", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
            ("H", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
            ("I", QColor("yellow"), MultiPlotWidget.PlotType.DEFAULT),
        ]
    )

    qtbot.waitUntil(lambda: plot._plots.count() == 1)  # should just create an empty plot
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 0

    plot._plots._merge_data_into_item(["A"], 0)  # check that stuff can be dragged into the default empty plot
    qtbot.waitUntil(lambda: plot._plots.count() == 1)
    assert len(cast(pg.PlotItem, cast(pg.PlotWidget, plot._plots.widget(0)).getPlotItem()).listDataItems()) == 1


def test_export_csv(qtbot: QtBot, plot: PlotsTableWidget) -> None:
    out_io = StringIO()
    plot._write_csv(out_io)
    assert (
        out_io.getvalue().replace("\r", "").replace("\n", "")
        == """# time,0,1,2
0.0,0.01,0.5,0.7
0.1,1.0,,
1.0,1.0,0.25,0.6
2.0,0.0,0.5,0.5""".replace(
            "\r", ""
        ).replace(
            "\n", ""
        )
    )  # ignore newline format

    plot._set_data(
        {  # more comprehensive missing data test
            "0": ([0, 2], [0.01, 0]),
            "1": ([0, 1], [0.25, 0.5]),
            "2": ([1, 2], [0.7, 0.6]),
        }
    )
    out_io = StringIO()
    plot._write_csv(out_io)
    assert (
        out_io.getvalue().replace("\r", "").replace("\n", "")
        == """# time,0,1,2
0,0.01,0.25,
1,,0.5,0.7
2,0.0,,0.6""".replace(
            "\r", ""
        ).replace(
            "\n", ""
        )
    )  # ignore newline format
