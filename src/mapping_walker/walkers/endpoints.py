import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Union

from oaklib.datamodels.vocabulary import IS_A
from oaklib.implementations.ols.ols_implementation import OlsImplementation
from oaklib.implementations.bioportal.bioportal_implementation import BioportalImplementation
from oaklib.implementations.pronto.pronto_implementation import ProntoImplementation
from oaklib.implementations.sparql.sparql_implementation import SparqlImplementation
from oaklib.implementations.sqldb.sql_implementation import SqlImplementation
from oaklib.resource import OntologyResource
from sssom.parsers import parse_sssom_table, to_mapping_set_document
from sssom.util import MappingSetDataFrame
from sssom.sssom_datamodel import Mapping, MappingSet, MatchTypeEnum
from sssom.sssom_document import MappingSetDocument

from mapping_walker.ext_schemas.oxo import OntologyIdentifier, ScopeEnum
from mapping_walker.pipeline.pipeline_config import EndpointConfiguration
from mapping_walker.utils.sssom_utils import curie_to_uri_map


@dataclass
class Endpoint:
    """
    Abstract class for any mapping endpoint
    """
    prefix_map: Dict[str, str] = field(default_factory=lambda: {})
    configuration: EndpointConfiguration = None

    def get_parents(self, term_id: str) -> List[str]:
        raise NotImplementedError(f'Not implemented for {self}')

    def get_ancestors(self, term_id: str) -> List[str]:
        raise NotImplementedError(f'Not implemented for {self}')

    def get_direct_mappings(self, curie: Union[str, OntologyIdentifier]) -> MappingSetDocument:
        raise NotImplementedError(f'Not implemented for {self}')

    def fill_gaps(self, msdoc: MappingSetDocument, confidence: float = 1.0):
        raise NotImplementedError(f'Not implemented for {self}')

    def add_prefix(self, curie: str, uri: str):
        [pfx, local] = curie.split(':', 2)
        if pfx not in self.prefix_map:
            self.prefix_map[pfx] = uri.replace(local, '')


@dataclass
class OxoEndpoint(Endpoint):

    def __post_init__(self):
        self.ols = OlsImplementation()
    
    def get_direct_mappings(self, curie: Union[str, OntologyIdentifier]) -> MappingSetDocument:
        mappings = list(self.ols.get_sssom_mappings_by_curie(curie))
        ms = MappingSet(mapping_set_id=OlsImplementation.base_url,
                          license='http://example.org/mixed',
                          mappings=mappings)
        return MappingSetDocument(mapping_set=ms,
                prefix_map=self.ols.get_prefix_map())

    def get_ancestors(self, term_id: str, ontology: str = None) -> List[str]:
        self.ols.focus_ontology = ontology
        ancs = self.ols.ancestors(term_id, predicates=[IS_A])
        return ancs

    def fill_gaps(self, msdoc: MappingSetDocument, confidence: float = 1.0) -> int:
        curie_map = curie_to_uri_map(msdoc)
        inv_map = {v: k for k, v in curie_map.items()}
        n = 0
        for curie, uri in curie_map.items():
            pfx, _ = curie.split(':', 2)
            ancs = self.get_ancestors(uri, ontology=pfx.lower())
            logging.debug(f'{curie} ANCS = {ancs}')
            for anc in ancs:
                if anc in curie_map:
                    m = Mapping(subject_id=curie,
                                object_id=anc,
                                predicate_id='rdfs:subClassOf',
                                confidence=confidence,
                                match_type=MatchTypeEnum.HumanCurated
                                )
                    logging.info(f'Gap filled link: {m}')
                    msdoc.mapping_set.mappings.append(m)
                    n += 1
        return n


@dataclass
class BioportalEndpoint(Endpoint):
    
    def __post_init__(self):
        self.impl = BioportalImplementation()


    def get_direct_mappings(self, curie: Union[str, OntologyIdentifier]) -> MappingSetDocument:
        # BioPortal API returns a lot of redundant mappings; remove those here
        mappings = []
        for mapping in self.impl.get_sssom_mappings_by_curie(curie):
            if mapping not in mappings:
                mappings.append(mapping)
        ms = MappingSet(mapping_set_id='http://data.bioontology.org/metadata/Mapping',
                          license='http://example.org/mixed',
                          mappings=mappings)
        return MappingSetDocument(mapping_set=ms,
                prefix_map=self.impl.get_prefix_map())


    def fill_gaps(self, msdoc: MappingSetDocument, confidence: float = 1) -> int:
        all_uris = set(
            [m.subject_id for m in msdoc.mapping_set.mappings] + 
            [m.object_id for m in msdoc.mapping_set.mappings])
        n = 0
        for uri in all_uris:
            ancestors = self.impl.ancestors(uri)
            logging.debug(f'{uri} ANCESTORS = {ancestors}')
            for ancestor in ancestors:
                if ancestor in all_uris:
                    m = Mapping(subject_id=uri,
                                object_id=ancestor,
                                predicate_id='rdfs:subClassOf',
                                confidence=confidence,
                                match_type=MatchTypeEnum.HumanCurated
                                )
                    logging.info(f'Gap filled link: {m}')
                    msdoc.mapping_set.mappings.append(m)
                    n += 1
        return n


@dataclass
class LocalEndpoint(Endpoint):

    msdf: MappingSetDataFrame = None

    def __post_init__(self):
        input_path = Path(self.configuration.input)
        if input_path.suffix == '.db':
            resource = OntologyResource(slug=f'sqlite:///{input_path.resolve()}', local=True)
            self.impl = SqlImplementation(resource)
        elif input_path.suffix == '.owl':
            resource = OntologyResource(slug=input_path.resolve(), local=True)
            self.impl = SparqlImplementation(resource)
        elif input_path.suffix == '.obo':
            resource = OntologyResource(slug=input_path.resolve(), local=True)
            self.impl = ProntoImplementation(resource)
        else:
            raise NotImplementedError(f'No OAK implementation available for file type {input_path.suffix}')

        if self.configuration.mappings:
            self.msdf = parse_sssom_table(self.configuration.mappings)
       

    def get_direct_mappings(self, curie: Union[str, OntologyIdentifier]) -> MappingSetDocument:
        # if a SSSOM TSV was provided by the configuration, use that to get mappings. Otherwise,
        # get them from the ontology itself
        if self.msdf:
            filtered_msdf = MappingSetDataFrame(
                df=self.msdf.df[(self.msdf.df['subject_id'] == curie) | (self.msdf.df['object_id'] == curie)],
                prefix_map=self.msdf.prefix_map,
                metadata=self.msdf.metadata
            )
            return to_mapping_set_document(filtered_msdf)
        else:
            mappings = list(m for m in self.impl.get_sssom_mappings_by_curie(curie) if not str(m.object_id).startswith('_:') and not str(m.subject_id).startswith('_:'))
            ms = MappingSet(mapping_set_id='http://example.org/',
                            license='http://example.org/mixed',
                            mappings=mappings)
            return MappingSetDocument(mapping_set=ms,
                    prefix_map=self.impl.get_prefix_map())            


    def fill_gaps(self, msdoc: MappingSetDocument, confidence: float = 1.0) -> int:
        curie_map = curie_to_uri_map(msdoc)
        inv_map = {v: k for k, v in curie_map.items()}
        n = 0
        for curie, uri in curie_map.items():
            pfx, _ = curie.split(':', 2)
            ancs = self.impl.ancestors(uri, predicates=[IS_A])
            logging.debug(f'{curie} ANCS = {ancs}')
            for anc in ancs:
                if anc in curie_map:
                    m = Mapping(subject_id=curie,
                                object_id=anc,
                                predicate_id='rdfs:subClassOf',
                                confidence=confidence,
                                match_type=MatchTypeEnum.HumanCurated
                                )
                    logging.info(f'Gap filled link: {m}')
                    msdoc.mapping_set.mappings.append(m)
                    n += 1
        return n


@dataclass
class UbergraphEndpoint(Endpoint):
    pass ## TODO
