import typing as t
from pathlib import Path
import typer

piter = typer.Typer(name="piter", pretty_exceptions_enable=False, no_args_is_help=True)
context_settings = {"allow_extra_args": True, "ignore_unknown_options": False}


@piter.command("check", context_settings=context_settings)
def check() -> None:
    print("Check ok!")


@piter.command("image2base64", context_settings=context_settings)
def image2base64(
    image_path: str = typer.Option(..., "-i", help="Input image path")
) -> str:
    import rich
    from piter.utils.images import image_file_to_base64_url

    rich.print(image_file_to_base64_url(image_path))


@piter.command("images_table_simple", context_settings=context_settings)
def images_table_simple(
    folder: Path = typer.Option(..., help="Input Underfolder path"),
    keys: t.List[str] = typer.Option([], help="List of image keys"),
    embed: bool = typer.Option(False, help="Embed images in the HTML file"),
    embed_quality: int = typer.Option(50, help="Embed quality"),
    output_file: str = typer.Option("", help="Output HTML file"),
) -> None:
    from piter.renderers.html import ImagesTableSimpleParams, ImagesTableSimple
    from piter.utils.images import numpy_to_base64_url
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
            return numpy_to_base64_url(item(), quality=embed_quality)

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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(output)
            print(f"HTML file saved at {f.name}")


@piter.command("images_clusters_simple", context_settings=context_settings)
def images_clusters_simple(
    folder: Path = typer.Option(..., help="Input Underfolder path"),
    image_key: str = typer.Option("image", help="Image key"),
    label_key: str = typer.Option(
        "metadata.label", help="Label key [dot notation for nested keys]"
    ),
    embed: bool = typer.Option(False, help="Embed images in the HTML file"),
    embed_quality: int = typer.Option(50, help="Embed quality"),
    output_file: str = typer.Option("", help="Output HTML file"),
) -> None:
    from piter.renderers.html import ImagesClustersSimpleParams, ImagesClustersSimple
    from piter.utils.images import numpy_to_base64_url, label_to_color
    import tempfile
    import pipelime.sequences as pls
    import pipelime.stages as pst
    import pipelime.items as pli
    from rich.progress import track

    dataset = pls.SamplesSequence.from_underfolder(folder)

    # Check if the label key is nested or not
    is_label_in_metadata = "." in label_key
    label_item = label_key.split(".")[0]
    label_subitem = ".".join(label_key.split(".")[1:]) if is_label_in_metadata else None

    if len(dataset) == 0:
        print("No images found in the folder")
        return

    def get_image_url(item: pli.ImageItem):
        if not embed:
            return str(item.local_sources[0])
        else:
            return numpy_to_base64_url(item(), quality=embed_quality)

    def is_valid_image(item):
        return (
            isinstance(item, pli.JpegImageItem)
            or isinstance(item, pli.BmpImageItem)
            or isinstance(item, pli.PngImageItem)
        )

    clusters = {}
    colors = {}
    for sample in track(dataset, total=len(dataset), description="Processing"):

        if not is_valid_image(sample[image_key]):
            continue

        image = sample[image_key]
        label = sample[label_item]()
        if is_label_in_metadata:
            label = label[label_subitem]

        if label not in clusters:
            clusters[label] = []

        if label not in colors:
            colors[label] = label_to_color(label, format="hex")

        # assert label is valid number
        try:
            label = int(label)
        except:
            raise ValueError(f"Label {label} is not a valid number")

        clusters[label].append(get_image_url(image))

    renderer = ImagesClustersSimple()
    output = renderer.render(
        ImagesClustersSimpleParams(
            title="Images Clusters", images_clusters=clusters, labels_colors=colors
        )
    )

    if output_file:
        with open(output_file, "w") as f:
            f.write(output)
        print(f"HTML file saved at {output_file}")
    else:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(output)
            print(f"HTML file saved at {f.name}")
