import logging
import os
import subprocess
import sys
from dataclasses import field, dataclass
from pathlib import Path
from typing import TextIO, Union, List

import click
import yaml
from mapping_walker.utils.sssom_utils import get_iri_from_curie, save_mapping_set_doc, fix_prefixes
from mapping_walker.walkers.endpoints import OxoEndpoint
from mapping_walker.walkers.mapping_walker import MappingWalker
from rdflib import Graph, URIRef, RDFS, Literal
from sssom import MappingSet
from sssom.sssom_document import MappingSetDocument
from sssom.util import to_mapping_set_dataframe, dataframe_to_ptable, collapse
from mapping_walker.pipeline.pipeline_config import PipelineConfiguration, EndpointConfiguration, EndpointEnum


PTABLE = 'ptable.tsv'
ONTOLOGY = 'ontology.ttl'
PREFIXES = 'prefixes.yaml'
SSSOM = 'sssom.yaml'


@dataclass
class BoomerResult:
    pngs: List[str] = None

@dataclass
class Pipeline:
    """
    End-to-end pipeline
    """
    configuration: PipelineConfiguration = None
    mappings_file: str = None

    def run(self, curies: Union[str, List[str]]) -> BoomerResult:
        """
        Queries endpoints to walk mapping graph, then
        runs boomer

        :param curies: one or more CURIEs to use as seed in search
        :return:
        """
        wd = self._workdir
        wd.mkdir(exist_ok=True, parents=True)
        walker = MappingWalker()
        for ec in self.configuration.endpoint_configurations:
            if str(ec.type) == str(EndpointEnum.OxO.text):
                endpoint = OxoEndpoint(configuration=ec)
            else:
                raise NotImplementedError(f'Not implemented; {ec.type}')
            walker.endpoints.append(endpoint)
        logging.info(f'Endpoints = {walker.endpoints}')
        msdoc = walker.walk(curies)
        fix_prefixes(msdoc)
        walker.fill_gaps(msdoc)
        return self.prep_boomer(msdoc)

    def prep_boomer(self, msdoc: MappingSetDocument):
        wd = Path(self.configuration.working_directory)
        save_mapping_set_doc(msdoc, str(self._sssom_path))
        self.write_ptable(msdoc, self._ptable)
        self.write_ontology(msdoc, str(self._ontology_path))
        self.write_prefixmap(msdoc, self._prefixes_path)
        return self.run_boomer()

    @property
    def _workdir(self) -> Path:
        return Path(self.configuration.working_directory)

    @property
    def _ptable(self) -> Path:
        return self._workdir / PTABLE

    @property
    def _ontology_path(self) -> Path:
        return self._workdir / ONTOLOGY

    @property
    def _sssom_path(self) -> Path:
        return self._workdir / SSSOM

    @property
    def _prefixes_path(self) -> Path:
        return self._workdir / PREFIXES

    @property
    def _boomer_output(self) -> Path:
        return self._workdir / 'output'

    def run_boomer(self) -> BoomerResult:
        # cleanup any previous runs
        if self._boomer_output.exists():
            for file in os.listdir(self._boomer_output):
                path = Path(self._boomer_output) / file
                path.unlink()
        #output_dir = str(Path(self.configuration.working_directory) / 'output')
        cmd = ['boomer',
               '-t', self._ptable,
               '-a', self._ontology_path,
               '-p', self._prefixes_path,
               '-o', self._boomer_output,
               '-r', 20,
               '-w', 10]
        cmd = [str(x) for x in cmd]
        self._run(cmd)
        pngs = []
        for file in os.listdir(self._boomer_output):
            if file.endswith('.json'):
                print(f'CONVERTING {file}')
                path = Path(self._boomer_output) / file
                png = f'{path}.png'
                result = self._run(['og2dot.js',
                                     '-s', self.configuration.stylesheet,
                                     str(path),
                                     '-t', 'png',
                                     '-o', png])
                pngs.append(png)
        return BoomerResult(pngs=pngs)

    def _run(self, cmd: List[str]):
        print(f'CMD={" ".join(cmd)}')
        result = subprocess.run(cmd, capture_output=True)
        logging.info("R:", result.returncode)
        logging.info("stdout:", result.stdout)
        if result.returncode != 0:
            logging.error("stderr:", result.stderr)
            raise ValueError(f'Code {result.returncode} for {cmd}')


    def load_mappings_and_write_ptable(self):
        mapping_set = yaml_loader.load(self.mappings_file, target_class=MappingSet)
        self.write_ptable(mapping_set)


    def write_ptable(self, doc: MappingSetDocument, output: Union[Path, str, TextIO] = sys.stdout):
        if not isinstance(output, TextIO):
            output = open(str(output), 'w', encoding='utf-8')
        for mapping in doc.mapping_set.mappings:
            if not mapping.confidence:
                mapping.confidence = 0.8
            # TODO: fix bug
            if mapping.predicate_id == 'rdfs:subClassOf':
                mapping.predicate_id = 'skos:broadMatch'
        msdf = to_mapping_set_dataframe(doc)
        df = collapse(msdf.df)
        rows = dataframe_to_ptable(df)
        for row in rows:
            output.write('\t'.join(row) + '\n')


    def write_ontology(self, doc: MappingSetDocument, output: str):
        """
        Will update prefix_map as a side-effect

        :param doc:
        :param output:
        :return:
        """
        g = Graph()
        mapping_set = doc.mapping_set
        def add_label(curie: str, label: str):
            iri = get_iri_from_curie(curie, doc)
            if label:
                g.add((iri, RDFS.label, Literal(label)))
        for mapping in mapping_set.mappings:
            add_label(mapping.subject_id, mapping.subject_label)
            add_label(mapping.object_id, mapping.object_label)
        g.serialize(destination=output)

    def write_prefixmap(self, doc: MappingSetDocument, output: Union[str, Path, TextIO] = sys.stdout):
        if isinstance(output, TextIO):
            yaml.dump(doc.prefix_map, stream=output)
        else:
            with open(output, 'w', encoding='utf-8') as stream:
                yaml.dump(doc.prefix_map, stream=stream)

@click.command()
@click.option("-v", "--verbose", count=True)
@click.option('--stylesheet',
              '-C',
              default='conf/style.json',
              help="path to stylesheet")
@click.option('--working-directory',
              '-d',
              show_default=True,
              help="directory in which to store intermediate and result files"
              )
@click.argument('curies', nargs=-1)
def main(curies, verbose: int, working_directory, stylesheet):
    """
    Crawls one or more endpoints from a seed set of CURIEs, walking the mapping graph,
    then run boomer on results
    """
    if verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    curies = list(curies)
    if working_directory is None:
        working_directory = Path('output') / '-'.join(curies)
    ec = EndpointConfiguration(type=EndpointEnum.OxO)
    conf = PipelineConfiguration(working_directory=working_directory,
                                 stylesheet=stylesheet,
                                 endpoint_configurations=[ec])
    pipeline = Pipeline(configuration=conf)
    result = pipeline.run(curies)
    print('To examine results:')
    for png in result.pngs:
        print(f'open {png}')


if __name__ == "__main__":
    main()
