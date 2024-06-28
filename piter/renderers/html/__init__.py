from abc import ABC, abstractmethod
import pathlib as pl
import pydantic as pyd
from jinja2 import Environment, FileSystemLoader, Template
import typing as t


def templates_path() -> pl.Path:
    return pl.Path(__file__).parent / 'templates'


class TemplatesCollection:
    IMAGES_TABLE_SIMPLE = templates_path() / 'images_table_simple.html'


Params = t.TypeVar('Params')


class HTMLRenderer(pyd.BaseModel, t.Generic[Params]):
    template_path: str

    def _build_template(self) -> Template:
        with open(str(self.template_path), 'r') as file:
            content = file.read()
        return Template(content)

    def render(self, data: Params) -> str:
        template = self._build_template()
        return template.render(data.dict())


class ImagesTableSimpleParams(pyd.BaseModel):
    title: str = 'Images Table'
    keys: t.List[str] = []
    images: t.List[t.Dict[str, str]]


class ImagesTableSimple(HTMLRenderer[ImagesTableSimpleParams]):
    template_path: str = TemplatesCollection.IMAGES_TABLE_SIMPLE
