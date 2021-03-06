from pathlib import Path
import unittest

from mapping_walker import __version__
from mapping_walker.pipeline.pipeline import Pipeline
from mapping_walker.pipeline.pipeline_config import PipelineConfiguration, EndpointConfiguration, EndpointEnum

from tests import OUTPUT_DIR, INPUT_DIR

WD = Path(OUTPUT_DIR) / 'tmp'
CURIE = 'UBERON:0013141'

class TestMappingWalker(unittest.TestCase):

    def test_pipeline(self):
        """
        test end to end pipeline, using OxO endpoint
        :return:
        """
        ec = EndpointConfiguration(type=EndpointEnum.OxO)
        conf = PipelineConfiguration(working_directory=str(WD),
                                    stylesheet=str(Path(INPUT_DIR) / 'style.json'),
                                    endpoint_configurations=[ec])
        pipeline = Pipeline(configuration=conf)
        result = pipeline.run(CURIE)
        print(f'PNGS={result.pngs}')
        assert len(result.pngs) == 2

