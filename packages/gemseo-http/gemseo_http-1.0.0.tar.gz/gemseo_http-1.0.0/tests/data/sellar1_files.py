# noqa: INP001
# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""Sellar disciplines with files."""

from __future__ import annotations

import json
import time
from pathlib import Path

from gemseo.core.discipline import MDODiscipline
from numpy import array
from numpy import sqrt


class Sellar1XSharedToFile(MDODiscipline):
    """A discipline writing `x_shared` to file."""

    def __init__(self) -> None:  # noqa :D107
        super().__init__()
        input_data = {"x_shared": array([0.0, 0.0])}
        output_data = {"x_shared_file": "input_file.json"}
        self.input_grammar.update_from_data(input_data)
        self.output_grammar.update_from_data(output_data)
        self.default_inputs = input_data

    def _run(self) -> None:
        output_filename = "input_file.json"
        input_data_converted = {"x_shared": self.local_data["x_shared"].tolist()}
        with Path(output_filename).open("w") as json_file:
            json.dump(input_data_converted, json_file)
        self.local_data["x_shared_file"] = Path(output_filename).resolve().as_posix()


class Sellar1Y1FileToProcess(MDODiscipline):
    """A discipline reading a file and putting the value into `local_data`."""

    def __init__(self) -> None:  # noqa :D107
        super().__init__()
        input_data = {"y_1_file": "output_file.json"}
        output_data = {"y_1": 0.0}
        self.input_grammar.update_from_data(input_data)
        self.output_grammar.update_from_data(output_data)
        self.default_inputs = input_data

    def _run(self) -> None:
        with Path(self.local_data["y_1_file"]).open() as json_file:
            data = json.load(json_file)
        self.local_data["y_1"] = data["y_1"]


class Sellar1File(MDODiscipline):
    """A Sellar1 Discipline taking as inputs files."""

    def __init__(self, sleep_time: float = 0.0, is_failing: bool = False) -> None:  # noqa :D107
        """
        Args:
            sleep_time: Time to sleep before starting the computation.
            is_failing: Whether to fail the computation.
        """
        super().__init__()
        self._sleep_time = sleep_time
        self._is_failing = is_failing
        input_data = {"x_shared_file": "input_file.json", "x_local": 0.0, "y_2": 0.0}
        self.input_grammar.update_from_data(input_data)
        output_data = {"y_1_file": "output_file.json"}
        self.output_grammar.update_from_data(output_data)
        # self.default_inputs = input_data
        # self.default_outputs = output_data

    def _run(self) -> None:
        if self._is_failing:
            msg = "Sellar1Remote discipline has failed."
            raise RuntimeError(msg)

        time.sleep(self._sleep_time)

        with Path(self.local_data["x_shared_file"]).open() as json_file:
            file_content = json_file.read()
            input_data = json.loads(file_content)
        z = input_data["x_shared"]
        x = self.local_data["x_local"]
        y_2 = self.local_data["y_2"]

        y_1 = sqrt(z[0] ** 2 + z[1] + x - 0.2 * y_2)

        self.local_data["y_1"] = y_1

        out = {}
        for k, v in self.local_data.items():
            if isinstance(v, (str, float)):
                out[k] = v
            else:
                out[k] = v.tolist()
        output_filename = "output_file.json"
        with Path(output_filename).open("w") as outfile:
            json.dump(out, outfile)
        self.local_data["y_1_file"] = output_filename

        workdir = Path()
        sub_data_dir = workdir / "data" / "sub_data"
        sub_data_dir_empty = workdir / "data" / "sub_data" / "empty_dir"
        file0 = workdir / "file0.txt"
        file1 = workdir / "data" / "file1.txt"
        file2 = workdir / "data" / "sub_data" / "file2.txt"
        Path(sub_data_dir).mkdir(parents=True)
        Path(sub_data_dir_empty).mkdir(parents=True)
        for file in [file0, file1, file2]:
            Path(file).write_text("Hello\n")


class Sellar1FileMultipleFile(Sellar1File):
    """A Sellar1 Discipline which takes multiple files in the y_1_file."""

    def __init__(self) -> None:  # noqa :D107
        super().__init__()
        self._output_data = {"y_1_file": ["output_file.json", "output_file.json"]}
        self.output_grammar.update_from_data(self._output_data)

    def _run(self):
        super()._run()
        self.local_data = self._output_data


class Sellar1FileWrongOutput(Sellar1File):
    """A Sellar1 Discipline with wrong types in output."""

    def __init__(self) -> None:  # noqa :D107
        super().__init__()
        output_data = {"y_1_file": "output_file.json", "y_1": 0.0}
        self.output_grammar.update_from_data(output_data)

    def _run(self):
        super()._run()
        self.local_data["y_1"] = 1.0
