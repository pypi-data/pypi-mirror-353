<!--
Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

## HTTPDiscipline: a client to the GEMSEO HTTP webapp

The `HTTPDiscipline` enables to link automatically to a distant GEMSEO HTTP service.
It configures automatically by querying the distant service.
Its execution triggers the execution of a discipline remotely,
and the data (including files),
are automatically transferred back and forth,
and transparently for its user.

The following example shows how to use the `HTTPDiscipline`:

```python
import os
from pathlib import Path

from gemseo.core.chain import MDOChain
from numpy import array

from gemseo_http.http_discipline import HTTPDiscipline
from gemseo_http.sellar1_files import Sellar1XSharedToFile
from gemseo_http.sellar1_files import Sellar1Y1FileToProcess

DIRPATH = Path(os.path.abspath(__file__)).parent

"""Test the execution of the HTTPDiscipline wrapper."""
service_base_url = "https://gaas.pf.irt-saintexupery.com"
port = 443
discipline = HTTPDiscipline(
    name="DistantSellar1WithFile",
    class_name="Sellar1File",
    url=service_base_url,
    port=port,
    user="username",
    password="password",
    inputs_to_upload=["x_shared_file"],
    outputs_to_download=["y_1_file"],
    file_paths_to_upload=[str(DIRPATH / "data" / "test.pdf")],
    file_paths_to_download=["test.pdf"]
)
discipline_xshared_to_file = Sellar1XSharedToFile()
y1_file_to_data = Sellar1Y1FileToProcess()
chain = MDOChain([discipline_xshared_to_file, discipline, y1_file_to_data])
data = {"x_shared": array([1.0, 2.0]), "x_local": 0.0, "y_2": 0.0}
out = chain.execute(data)
```

Other examples can be found in the [examples](/gemseo-http/generated/examples/remote_discipline) folder.
