import json
from pathlib import Path
import unittest

from linkml_runtime.loaders import json_loader
from mapping_walker.utils.oxo_utils import load_oxo_payload

from tests import INPUT_DIR
from mapping_walker import __version__
from mapping_walker.ext_schemas.oxo import Container


class TestSchema(unittest.TestCase):

    def test_schema(self):
        infile = str(Path(INPUT_DIR) / 'oxo-example-uberon.json')
        with open(infile, encoding='utf-8') as stream:
            obj = json.load(stream)
        print(obj)
        container = load_oxo_payload(obj)
        print(container)

