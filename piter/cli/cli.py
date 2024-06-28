import typing as t
from pathlib import Path
import typer

piter = typer.Typer(name="piter", pretty_exceptions_enable=False, no_args_is_help=True)
context_settings = {"allow_extra_args": True, "ignore_unknown_options": False}


@piter.command("check", context_settings=context_settings)
def check() -> None:
    print("Check ok!")


@piter.command("images_table_simple", context_settings=context_settings)
def images_table_simple(
    folder: Path = typer.Option(..., help="Input Underfolder path"),
    keys: t.List[str] = typer.Option([], help="List of image keys"),
    embed: bool = typer.Option(False, help="Embed images in the HTML file"),
    embed_quality: int = typer.Option(50, help="Embed quality"),
    output_file: str = typer.Option("", help="Output HTML file"),
) -> None:
    from piter.renderers.html import ImagesTableSimpleParams, ImagesTableSimple
    from piter.utils.images import numpy_to_jpeg_base64_url
    import tempfile
    import pipelime.sequences as pls
    import pipelime.stages as pst
    import pipelime.items as pli
    from rich.progress import track

    dataset = pls.SamplesSequence.from_underfolder(folder)

    if len(dataset) == 0:
        print("No images found in the folder")
        return

    if len(keys) > 0:
        stage = pst.StageKeysFilter(key_list=keys)
        dataset = dataset.map(stage)
    else:
        keys = list(sorted(dataset[0].keys()))

    def get_image_url(item: pli.ImageItem):
        if not embed:
            return str(item.local_sources[0])
        else:
            return numpy_to_jpeg_base64_url(item(), quality=embed_quality)

    def is_valid_image(item):
        return (
            isinstance(item, pli.JpegImageItem)
            or isinstance(item, pli.BmpImageItem)
            or isinstance(item, pli.PngImageItem)
        )

    batches = []
    for sample in track(dataset, total=len(dataset), description="Processing"):
        batch = {}
        for key in keys:
            if is_valid_image(sample[key]):
                batch[key] = get_image_url(sample[key])
        batches.append(batch)

    renderer = ImagesTableSimple()
    output = renderer.render(
        ImagesTableSimpleParams(
            title="Images Table",
            keys=keys,
            images=batches,
        )
    )

    if output_file:
        with open(output_file, "w") as f:
            f.write(output)
        print(f"HTML file saved at {output_file}")
    else:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(output)
            print(f"HTML file saved at {f.name}")
