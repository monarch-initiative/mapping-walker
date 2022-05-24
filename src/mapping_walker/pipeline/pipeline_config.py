# Auto generated from pipeline_config.yaml by pythongen.py version: 0.9.0
# Generation date: 2022-05-19T10:16:06
# Schema: walker-confic
#
# id: https://w3id.org/sssom/walker_config
# description: Schema for Walker Config
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import sys
import re
from jsonasobj2 import JsonObj, as_dict
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.linkml_model.types import Integer, String

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
CONFIG = CurieNamespace('config', 'https://w3id.org/sssom/walker_config/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
XSD = CurieNamespace('xsd', 'http://www.w3.org/2001/XMLSchema#')
DEFAULT_ = CONFIG


# Types
class MaximumCount(Integer):
    type_class_uri = XSD.integer
    type_class_curie = "xsd:integer"
    type_name = "MaximumCount"
    type_model_uri = CONFIG.MaximumCount


class Directory(String):
    type_class_uri = XSD.string
    type_class_curie = "xsd:string"
    type_name = "Directory"
    type_model_uri = CONFIG.Directory


class FilePath(String):
    type_class_uri = XSD.string
    type_class_curie = "xsd:string"
    type_name = "FilePath"
    type_model_uri = CONFIG.FilePath


# Class references



@dataclass
class BoomerConfiguration(YAMLRoot):
    """
    A configuration for boomer command line options
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CONFIG.BoomerConfiguration
    class_class_curie: ClassVar[str] = "config:BoomerConfiguration"
    class_name: ClassVar[str] = "BoomerConfiguration"
    class_model_uri: ClassVar[URIRef] = CONFIG.BoomerConfiguration

    runs: Optional[Union[int, MaximumCount]] = None
    window: Optional[Union[int, MaximumCount]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.runs is not None and not isinstance(self.runs, MaximumCount):
            self.runs = MaximumCount(self.runs)

        if self.window is not None and not isinstance(self.window, MaximumCount):
            self.window = MaximumCount(self.window)

        super().__post_init__(**kwargs)


@dataclass
class EndpointConfiguration(YAMLRoot):
    """
    A configuration for a mapping endpoint
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CONFIG.EndpointConfiguration
    class_class_curie: ClassVar[str] = "config:EndpointConfiguration"
    class_name: ClassVar[str] = "EndpointConfiguration"
    class_model_uri: ClassVar[URIRef] = CONFIG.EndpointConfiguration

    type: Optional[Union[str, "EndpointEnum"]] = None
    input: Optional[str] = None
    mappings: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.type is not None and not isinstance(self.type, EndpointEnum):
            self.type = EndpointEnum(self.type)

        if self.input is not None and not isinstance(self.input, str):
            self.input = str(self.input)

        if self.mappings is not None and not isinstance(self.mappings, str):
            self.mappings = str(self.mappings)

        super().__post_init__(**kwargs)


@dataclass
class PipelineConfiguration(YAMLRoot):
    """
    A configuration for a pipeline
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = CONFIG.PipelineConfiguration
    class_class_curie: ClassVar[str] = "config:PipelineConfiguration"
    class_name: ClassVar[str] = "PipelineConfiguration"
    class_model_uri: ClassVar[URIRef] = CONFIG.PipelineConfiguration

    endpoint_configurations: Optional[Union[Union[dict, EndpointConfiguration], List[Union[dict, EndpointConfiguration]]]] = empty_list()
    max_clique_size: Optional[Union[int, MaximumCount]] = None
    max_hops: Optional[Union[int, MaximumCount]] = None
    working_directory: Optional[Union[str, Directory]] = None
    stylesheet: Optional[Union[str, FilePath]] = None
    boomer_configuration: Optional[Union[dict, BoomerConfiguration]] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if not isinstance(self.endpoint_configurations, list):
            self.endpoint_configurations = [self.endpoint_configurations] if self.endpoint_configurations is not None else []
        self.endpoint_configurations = [v if isinstance(v, EndpointConfiguration) else EndpointConfiguration(**as_dict(v)) for v in self.endpoint_configurations]

        if self.max_clique_size is not None and not isinstance(self.max_clique_size, MaximumCount):
            self.max_clique_size = MaximumCount(self.max_clique_size)

        if self.max_hops is not None and not isinstance(self.max_hops, MaximumCount):
            self.max_hops = MaximumCount(self.max_hops)

        if self.working_directory is not None and not isinstance(self.working_directory, Directory):
            self.working_directory = Directory(self.working_directory)

        if self.stylesheet is not None and not isinstance(self.stylesheet, FilePath):
            self.stylesheet = FilePath(self.stylesheet)

        if self.boomer_configuration is not None and not isinstance(self.boomer_configuration, BoomerConfiguration):
            self.boomer_configuration = BoomerConfiguration(**as_dict(self.boomer_configuration))

        super().__post_init__(**kwargs)


# Enumerations
class EndpointEnum(EnumDefinitionImpl):

    OxO = PermissibleValue(text="OxO")
    BioPortal = PermissibleValue(text="BioPortal")
    Local = PermissibleValue(text="Local")

    _defn = EnumDefinition(
        name="EndpointEnum",
    )

# Slots
class slots:
    pass

slots.boomerConfiguration__runs = Slot(uri=CONFIG.runs, name="boomerConfiguration__runs", curie=CONFIG.curie('runs'),
                   model_uri=CONFIG.boomerConfiguration__runs, domain=None, range=Optional[Union[int, MaximumCount]])

slots.boomerConfiguration__window = Slot(uri=CONFIG.window, name="boomerConfiguration__window", curie=CONFIG.curie('window'),
                   model_uri=CONFIG.boomerConfiguration__window, domain=None, range=Optional[Union[int, MaximumCount]])

slots.endpointConfiguration__type = Slot(uri=CONFIG.type, name="endpointConfiguration__type", curie=CONFIG.curie('type'),
                   model_uri=CONFIG.endpointConfiguration__type, domain=None, range=Optional[Union[str, "EndpointEnum"]])

slots.endpointConfiguration__input = Slot(uri=CONFIG.input, name="endpointConfiguration__input", curie=CONFIG.curie('input'),
                   model_uri=CONFIG.endpointConfiguration__input, domain=None, range=Optional[str])

slots.endpointConfiguration__mappings = Slot(uri=CONFIG.mappings, name="endpointConfiguration__mappings", curie=CONFIG.curie('mappings'),
                   model_uri=CONFIG.endpointConfiguration__mappings, domain=None, range=Optional[str])

slots.pipelineConfiguration__endpoint_configurations = Slot(uri=CONFIG.endpoint_configurations, name="pipelineConfiguration__endpoint_configurations", curie=CONFIG.curie('endpoint_configurations'),
                   model_uri=CONFIG.pipelineConfiguration__endpoint_configurations, domain=None, range=Optional[Union[Union[dict, EndpointConfiguration], List[Union[dict, EndpointConfiguration]]]])

slots.pipelineConfiguration__max_clique_size = Slot(uri=CONFIG.max_clique_size, name="pipelineConfiguration__max_clique_size", curie=CONFIG.curie('max_clique_size'),
                   model_uri=CONFIG.pipelineConfiguration__max_clique_size, domain=None, range=Optional[Union[int, MaximumCount]])

slots.pipelineConfiguration__max_hops = Slot(uri=CONFIG.max_hops, name="pipelineConfiguration__max_hops", curie=CONFIG.curie('max_hops'),
                   model_uri=CONFIG.pipelineConfiguration__max_hops, domain=None, range=Optional[Union[int, MaximumCount]])

slots.pipelineConfiguration__working_directory = Slot(uri=CONFIG.working_directory, name="pipelineConfiguration__working_directory", curie=CONFIG.curie('working_directory'),
                   model_uri=CONFIG.pipelineConfiguration__working_directory, domain=None, range=Optional[Union[str, Directory]])

slots.pipelineConfiguration__stylesheet = Slot(uri=CONFIG.stylesheet, name="pipelineConfiguration__stylesheet", curie=CONFIG.curie('stylesheet'),
                   model_uri=CONFIG.pipelineConfiguration__stylesheet, domain=None, range=Optional[Union[str, FilePath]])

slots.pipelineConfiguration__boomer_configuration = Slot(uri=CONFIG.boomer_configuration, name="pipelineConfiguration__boomer_configuration", curie=CONFIG.curie('boomer_configuration'),
                   model_uri=CONFIG.pipelineConfiguration__boomer_configuration, domain=None, range=Optional[Union[dict, BoomerConfiguration]])
