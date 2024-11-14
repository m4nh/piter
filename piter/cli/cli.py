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
    title: str = typer.Option("Images Table", help="Title of the HTML file"),
    folder: Path = typer.Option(..., help="Input Underfolder path"),
    keys: t.List[str] = typer.Option([], help="List of image keys"),
    mkeys: t.List[str] = typer.Option([], help="List of metadata keys"),
    embed: bool = typer.Option(False, help="Embed images in the HTML file"),
    embed_quality: int = typer.Option(50, help="Embed quality"),
    output_file: str = typer.Option("", help="Output HTML file"),
) -> None:
    from piter.renderers.html import ImagesTableSimpleParams, ImagesTableSimple
    from piter.utils.images import numpy_to_base64_url, image_file_to_base64_url
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
        stage = pst.StageKeysFilter(key_list=keys + mkeys)
        dataset = dataset.map(stage)
    else:
        keys = list(sorted(dataset[0].keys()))

    def get_image_url(item: pli.ImageItem):
        if not embed:
            return str(item.local_sources[0])
        else:
            # return numpy_to_base64_url(item(), quality=embed_quality)
            return image_file_to_base64_url(item.local_sources[0], embed_quality)

    def is_valid_image(item):
        return (
            isinstance(item, pli.JpegImageItem)
            or isinstance(item, pli.BmpImageItem)
            or isinstance(item, pli.PngImageItem)
        )

    def is_valid_metadata(item):
        return isinstance(item, pli.MetadataItem)

    def purge_metadata(item):
        output_metadata = {}
        for key, value in item.items():
            if isinstance(value, float):
                output_metadata[key] = f"{value:.4f}"
            else:
                output_metadata[key] = str(value)

        return output_metadata

    batches = []
    mbatches = []
    for sample in track(dataset, total=len(dataset), description="Processing"):

        # Add images in the batch
        batch = {}
        for key in keys:
            if is_valid_image(sample[key]):
                batch[key] = get_image_url(sample[key])
        batches.append(batch)

        # Add metadatas in the batch
        mbatch = {}
        for mkey in mkeys:
            if is_valid_metadata(sample[mkey]):
                mbatch[mkey] = purge_metadata(sample[mkey]())
        mbatches.append(mbatch)

    renderer = ImagesTableSimple()
    output = renderer.render(
        ImagesTableSimpleParams(
            title=title,
            keys=keys,
            images=batches,
            mkeys=mkeys,
            metadatas=mbatches,
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
    title: str = typer.Option("Images Clusters", help="Title of the HTML file"),
    folder: Path = typer.Option(..., help="Input Underfolder path"),
    image_key: str = typer.Option("image", help="Image key"),
    label_key: str = typer.Option(
        "metadata.label", help="Label key [dot notation for nested keys]"
    ),
    color_key: str = typer.Option("", help="Color key"),
    embed: bool = typer.Option(False, help="Embed images in the HTML file"),
    embed_quality: int = typer.Option(50, help="Embed quality"),
    output_file: str = typer.Option("", help="Output HTML file"),
) -> None:
    from piter.renderers.html import ImagesClustersSimpleParams, ImagesClustersSimple
    from piter.utils.images import numpy_to_base64_url, label_to_color, color_rgb_to_hex
    import tempfile
    import pipelime.sequences as pls
    import pipelime.stages as pst
    import pipelime.items as pli
    from rich.progress import track

    dataset = pls.SamplesSequence.from_underfolder(folder)

    # Check if the label key is nested or not
    is_nested_label = "." in label_key
    label_item = label_key.split(".")[0]
    label_subitem = ".".join(label_key.split(".")[1:]) if is_nested_label else None

    is_nested_color = "." in color_key
    color_item = color_key.split(".")[0]
    color_subitem = ".".join(color_key.split(".")[1:]) if is_nested_color else None

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
        if is_nested_label:
            label = label[label_subitem]

        if label not in clusters:
            clusters[label] = []

        if label not in colors:
            if len(color_key) > 0:
                color = sample[color_item]()[color_subitem]
                colors[label] = color_rgb_to_hex(color)
            else:
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
            title=title,
            images_clusters=clusters,
            labels_colors=colors,
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
