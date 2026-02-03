from abc import ABC, abstractmethod
import pathlib as pl
import pydantic as pyd
from pydantic_settings import BaseSettings
from jinja2 import Environment, FileSystemLoader, Template
import typing as t
import datetime


def templates_path() -> pl.Path:
    return pl.Path(__file__).parent / "templates"


class GlobalParams(BaseSettings):
    footnotes: str = "Eyecan ® - " + str(datetime.datetime.now().year)


class TemplatesCollection:
    IMAGES_TABLE_SIMPLE = "images_table_simple.html"
    IMAGES_CLUSTERS_SIMPLE = "images_clusters_simple.html"
    ANOMALY_INTERACTIVE_SIMPLE = "anomaly_interactive.html"


class _HasDict(t.Protocol):
    def dict(self) -> t.Dict[str, t.Any]: ...


Params = t.TypeVar("Params", bound=_HasDict)


class HTMLRenderer(pyd.BaseModel, t.Generic[Params]):
    template_path: str

    def _build_template(self) -> Template:
        with open(str(self.template_path), "r") as file:
            content = file.read()
        return Template(content)

    def render(self, data: Params) -> str:
        env = Environment(loader=FileSystemLoader(templates_path()))
        return env.get_template(self.template_path).render(data.dict(), zip=zip)
        # template = self._build_template()
        # return template.render(data.dict())


class ImagesTableSimpleParams(GlobalParams):
    title: str = "Images Table"
    keys: t.List[str] = []
    images: t.List[t.Dict[str, str]]
    mkeys: t.List[str] = []
    metadatas: t.List[t.Dict[str, t.Mapping[str, t.Any]]] = []
    group_size: t.Optional[int] = None
    show_indices: bool = True


class ImagesTableSimple(HTMLRenderer[ImagesTableSimpleParams]):
    template_path: str = TemplatesCollection.IMAGES_TABLE_SIMPLE


class ImagesClustersSimpleParams(GlobalParams):
    title: str = "Images Clusters"
    images_clusters: t.Dict[int, t.List[str]]
    labels_colors: t.Optional[t.Dict[int, str]] = None


class ImagesClustersSimple(HTMLRenderer[ImagesClustersSimpleParams]):
    template_path: str = TemplatesCollection.IMAGES_CLUSTERS_SIMPLE


class AnomalyInteractiveSample(pyd.BaseModel):
    image_path: str
    heatmap_path: str
    sample_score: float
    heatmap_bounds: t.List[float]
    sample_id: str
    dataset_id: str
    original_filename: str
    file_id: str


class AnomalyInteractiveSimpleParams(GlobalParams):
    title: str = "Anomaly Interactive"
    samples: t.List[AnomalyInteractiveSample]


class AnomalyInteractiveSimple(HTMLRenderer[AnomalyInteractiveSimpleParams]):
    template_path: str = TemplatesCollection.ANOMALY_INTERACTIVE_SIMPLE
