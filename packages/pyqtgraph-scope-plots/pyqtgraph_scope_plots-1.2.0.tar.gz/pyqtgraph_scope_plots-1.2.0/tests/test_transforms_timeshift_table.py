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

from typing import List, Tuple, Dict, Any, cast
from unittest import mock

import numpy as np
import numpy.typing as npt
import pytest
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QInputDialog
from pytestqt.qtbot import QtBot

from pyqtgraph_scope_plots.timeshift_signals_table import TimeshiftSignalsTable, TimeshiftDataStateModel
from pyqtgraph_scope_plots.transforms_signal_table import TransformsSignalsTable, TransformsDataStateModel
from pyqtgraph_scope_plots.util import not_none
from .test_util import context_menu, menu_action_by_name


@pytest.fixture()
def transforms_table(qtbot: QtBot) -> TransformsSignalsTable:
    """Creates a signals plot with multiple data items"""
    table = TransformsSignalsTable()
    table.set_data_items([("0", QColor("yellow")), ("1", QColor("orange")), ("2", QColor("blue"))])
    qtbot.addWidget(table)
    table.show()
    qtbot.waitExposed(table)
    return table


@pytest.fixture()
def timeshifts_table(qtbot: QtBot) -> TimeshiftSignalsTable:
    """Creates a signals plot with multiple data items"""
    table = TimeshiftSignalsTable()
    table.set_data_items([("0", QColor("yellow")), ("1", QColor("orange")), ("2", QColor("blue"))])
    qtbot.addWidget(table)
    table.show()
    qtbot.waitExposed(table)
    return table


def np_immutable(x: List[float]) -> npt.NDArray[np.float64]:
    """Creates a np.array with immutable set (writable=False)"""
    arr = np.array(x)
    arr.flags.writeable = False
    return arr


DATA: Dict[str, Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]] = {
    "0": (np_immutable([0, 0.1, 1, 2]), np_immutable([0.01, 1, 1, 0])),
    "1": (np_immutable([0, 1, 2]), np_immutable([0.5, 0.25, 0.5])),
    "2": (np_immutable([0, 1, 2]), np_immutable([0.7, 0.6, 0.5])),
}


def test_transform_empty(qtbot: QtBot, transforms_table: TransformsSignalsTable) -> None:
    """Tests empty transforms, should return the input"""
    assert transforms_table.apply_transform("0", DATA).tolist() == [0.01, 1, 1, 0]
    assert transforms_table.apply_transform("1", DATA).tolist() == [0.5, 0.25, 0.5]
    assert transforms_table.apply_transform("2", DATA).tolist() == [0.7, 0.6, 0.5]


def test_transform_x(qtbot: QtBot, transforms_table: TransformsSignalsTable) -> None:
    """Tests transforms that only reference x"""
    transforms_table.set_transform(["0"], "x + 1")
    qtbot.waitUntil(lambda: transforms_table.apply_transform("0", DATA).tolist() == [1.01, 2, 2, 1])

    transforms_table.set_transform(["1"], "x * 2")
    qtbot.waitUntil(lambda: transforms_table.apply_transform("1", DATA).tolist() == [1, 0.5, 1])
    assert transforms_table.apply_transform("0", DATA).tolist() == [1.01, 2, 2, 1]  # should not affect 0

    transforms_table.set_transform(["0"], "")
    qtbot.waitUntil(lambda: transforms_table.apply_transform("0", DATA).tolist() == [0.01, 1, 1, 0])
    assert transforms_table.apply_transform("1", DATA).tolist() == [1, 0.5, 1]


def test_transform_multiple(qtbot: QtBot, transforms_table: TransformsSignalsTable) -> None:
    """Tests transforms that reference other data objects"""
    transforms_table.set_transform(["1"], "x + data['2']")
    qtbot.waitUntil(lambda: transforms_table.apply_transform("1", DATA).tolist() == [1.2, 0.85, 1])

    transforms_table.set_transform(["1"], "x + data['0']")  # allow getting with longer data
    qtbot.waitUntil(lambda: transforms_table.apply_transform("1", DATA).tolist() == [0.51, 1.25, 0.5])

    transforms_table.set_transform(["0"], "x + data.get('1', 0)")  # test .get with missing values
    qtbot.waitUntil(lambda: transforms_table.apply_transform("0", DATA).tolist() == [0.51, 1, 1.25, 0.5])


def test_transform_ui(qtbot: QtBot, transforms_table: TransformsSignalsTable) -> None:
    """Basic test of transforms driven from the UI"""
    target = transforms_table.visualItemRect(
        not_none(transforms_table.item(1, transforms_table.COL_TRANSFORM))
    ).center()
    with mock.patch.object(QInputDialog, "getText") as mock_input:  # allow getting with longer data
        mock_input.return_value = ("x + data['0']", True)
        menu_action_by_name(context_menu(qtbot, transforms_table, target), "set function").trigger()
        qtbot.waitUntil(lambda: transforms_table.apply_transform("1", DATA).tolist() == [0.51, 1.25, 0.5])


def test_transform_ui_syntaxerror(qtbot: QtBot, transforms_table: TransformsSignalsTable) -> None:
    """Tests that syntax errors repeatedly prompt"""
    target = transforms_table.visualItemRect(
        not_none(transforms_table.item(0, transforms_table.COL_TRANSFORM))
    ).center()
    with mock.patch.object(QInputDialog, "getText") as mock_input:  # test error on missing values
        mock_value = ("is", True)  # Python keyword, invalid syntax

        def mock_value_update(*args: Any, **kwargs: Any) -> Tuple[str, bool]:
            nonlocal mock_value
            prev_mock_value = mock_value
            mock_value = ("1", True)
            return prev_mock_value

        mock_input.side_effect = mock_value_update
        menu_action_by_name(context_menu(qtbot, transforms_table, target), "set function").trigger()
        qtbot.waitUntil(lambda: transforms_table.apply_transform("0", DATA).tolist() == [1, 1, 1, 1])


def test_transform_ui_error(qtbot: QtBot, transforms_table: TransformsSignalsTable) -> None:
    target = transforms_table.visualItemRect(
        not_none(transforms_table.item(0, transforms_table.COL_TRANSFORM))
    ).center()
    with mock.patch.object(QInputDialog, "getText") as mock_input:  # test error on missing values
        mock_input.return_value = ("ducks", True)
        menu_action_by_name(context_menu(qtbot, transforms_table, target), "set function").trigger()
        qtbot.waitUntil(lambda: isinstance(transforms_table.apply_transform("0", DATA), Exception))  # must evaluate
        qtbot.waitUntil(lambda: "NameNotDefined" in transforms_table.item(0, transforms_table.COL_TRANSFORM).text())

    with mock.patch.object(QInputDialog, "getText") as mock_input:  # test error on missing values
        mock_input.return_value = ("x + data['1']", True)
        menu_action_by_name(context_menu(qtbot, transforms_table, target), "set function").trigger()
        qtbot.waitUntil(lambda: isinstance(transforms_table.apply_transform("0", DATA), Exception))  # must evaluate
        qtbot.waitUntil(lambda: "KeyError" in transforms_table.item(0, transforms_table.COL_TRANSFORM).text())

    with mock.patch.object(QInputDialog, "getText") as mock_input:  # test error on missing values
        mock_input.return_value = ("'ducks'", True)
        menu_action_by_name(context_menu(qtbot, transforms_table, target), "set function").trigger()
        qtbot.waitUntil(lambda: isinstance(transforms_table.apply_transform("0", DATA), Exception))  # must evaluate
        qtbot.waitUntil(lambda: "TypeError" in transforms_table.item(0, transforms_table.COL_TRANSFORM).text())


def test_transform_save(qtbot: QtBot, transforms_table: TransformsSignalsTable) -> None:
    assert cast(TransformsDataStateModel, transforms_table._dump_model(["0", "1"]).data["0"]).transform == ""
    assert cast(TransformsDataStateModel, transforms_table._dump_model(["0", "1"]).data["1"]).transform == ""

    transforms_table.set_transform(["1"], "x + data['0']")  # allow getting with longer data
    qtbot.waitUntil(
        lambda: cast(TransformsDataStateModel, transforms_table._dump_model(["0", "1"]).data["1"]).transform
        == "x + data['0']"
    )
    assert (
        cast(TransformsDataStateModel, transforms_table._dump_model(["0", "1"]).data["0"]).transform == ""
    )  # unchanged


def test_transform_load(qtbot: QtBot, transforms_table: TransformsSignalsTable) -> None:
    """Tests transforms that only reference x"""
    model = transforms_table._dump_model(["0"])

    cast(TransformsDataStateModel, model.data["0"]).transform = "x + 1"
    transforms_table._load_model(model)
    qtbot.waitUntil(lambda: transforms_table.apply_transform("0", DATA).tolist() == [1.01, 2, 2, 1])

    cast(TransformsDataStateModel, model.data["0"]).transform = ""
    transforms_table._load_model(model)
    qtbot.waitUntil(lambda: transforms_table.apply_transform("0", DATA).tolist() == [0.01, 1, 1, 0])


def test_timeshift(qtbot: QtBot, timeshifts_table: TimeshiftSignalsTable) -> None:
    # test empty
    qtbot.waitUntil(lambda: timeshifts_table.apply_timeshifts("0", DATA).tolist() == [0.0, 0.1, 1.0, 2.0])
    timeshifts_table.set_timeshift(["0"], 1)
    qtbot.waitUntil(lambda: timeshifts_table.apply_timeshifts("0", DATA).tolist() == [1.0, 1.1, 2.0, 3.0])
    assert timeshifts_table.item(0, timeshifts_table.COL_TIMESHIFT).text() == "1"
    timeshifts_table.set_timeshift(["0"], -0.5)  # test negative and noninteger
    qtbot.waitUntil(lambda: timeshifts_table.apply_timeshifts("0", DATA).tolist() == [-0.5, -0.4, 0.5, 1.5])
    assert timeshifts_table.item(0, timeshifts_table.COL_TIMESHIFT).text() == "-0.5"
    timeshifts_table.set_timeshift(["0"], 0)  # revert to empty
    qtbot.waitUntil(lambda: timeshifts_table.apply_timeshifts("0", DATA).tolist() == [0.0, 0.1, 1.0, 2.0])
    assert timeshifts_table.item(0, timeshifts_table.COL_TIMESHIFT).text() == ""


def test_timeshift_save(qtbot: QtBot, timeshifts_table: TimeshiftSignalsTable) -> None:
    qtbot.waitUntil(lambda: cast(TimeshiftDataStateModel, timeshifts_table._dump_model(["0"]).data["0"]).timeshift == 0)
    timeshifts_table.set_timeshift(["0"], -0.5)
    qtbot.waitUntil(
        lambda: cast(TimeshiftDataStateModel, timeshifts_table._dump_model(["0"]).data["0"]).timeshift == -0.5
    )


def test_timeshift_load(qtbot: QtBot, timeshifts_table: TimeshiftSignalsTable) -> None:
    model = timeshifts_table._dump_model(["0"])
    cast(TimeshiftDataStateModel, model.data["0"]).timeshift = -0.5
    timeshifts_table._load_model(model)
    qtbot.waitUntil(lambda: timeshifts_table.apply_timeshifts("0", DATA).tolist() == [-0.5, -0.4, 0.5, 1.5])

    cast(TimeshiftDataStateModel, model.data["0"]).timeshift = 0
    timeshifts_table._load_model(model)
    qtbot.waitUntil(lambda: timeshifts_table.apply_timeshifts("0", DATA).tolist() == [0.0, 0.1, 1.0, 2.0])
