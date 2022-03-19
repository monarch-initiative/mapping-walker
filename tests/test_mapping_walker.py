from pathlib import Path

from mapping_walker import __version__
from mapping_walker.pipeline.pipeline import Pipeline
from mapping_walker.pipeline.pipeline_config import PipelineConfiguration, EndpointConfiguration, EndpointEnum

from tests import OUTPUT_DIR, INPUT_DIR

WD = Path(OUTPUT_DIR) / 'tmp'
CURIE = 'UBERON:0013141'

def test_pipeline():
    """
    test end to end pipeline
    :return:
    """
    ec = EndpointConfiguration(type=EndpointEnum.OxO)
    conf = PipelineConfiguration(working_directory=str(WD),
                                 stylesheet=str(Path(INPUT_DIR) / 'style.json'),
                                 endpoint_configurations=[ec])
    pipeline = Pipeline(configuration=conf)
    result = pipeline.run(CURIE)
    print(f'PNGS={result.pngs}')

