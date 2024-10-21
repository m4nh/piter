from abc import ABC, abstractmethod
import pathlib as pl
import pydantic as pyd
from jinja2 import Environment, FileSystemLoader, Template
import typing as t


def templates_path() -> pl.Path:
    return pl.Path(__file__).parent / 'templates'


class TemplatesCollection:
    IMAGES_TABLE_SIMPLE = 'images_table_simple.html'
    IMAGES_CLUSTERS_SIMPLE = 'images_clusters_simple.html'


Params = t.TypeVar('Params')


class HTMLRenderer(pyd.BaseModel, t.Generic[Params]):
    template_path: str

    def _build_template(self) -> Template:
        with open(str(self.template_path), 'r') as file:
            content = file.read()
        return Template(content)
    
    def render(self, data: Params) -> str:
        env = Environment(loader=FileSystemLoader(templates_path()))
        return env.get_template(self.template_path).render(data.dict())
        # template = self._build_template()
        # return template.render(data.dict())


class ImagesTableSimpleParams(pyd.BaseModel):
    title: str = 'Images Table'
    keys: t.List[str] = []
    images: t.List[t.Dict[str, str]]


class ImagesTableSimple(HTMLRenderer[ImagesTableSimpleParams]):
    template_path: str = TemplatesCollection.IMAGES_TABLE_SIMPLE


class ImagesClustersSimpleParams(pyd.BaseModel):
    title: str = 'Images Clusters'
    images_clusters: t.Dict[int, t.List[str]]
    labels_colors: t.Optional[t.Dict[int, str]] = None

class ImagesClustersSimple(HTMLRenderer[ImagesClustersSimpleParams]):
    template_path: str = TemplatesCollection.IMAGES_CLUSTERS_SIMPLE