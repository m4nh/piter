import typing as t
from pathlib import Path
import typer

piter = typer.Typer(name="piter", pretty_exceptions_enable=False, no_args_is_help=True)
context_settings = {"allow_extra_args": True, "ignore_unknown_options": False}


@piter.command("check", context_settings=context_settings)
def check(
    name: str = typer.Option(..., help="The name of the person to greet")
) -> None:
    print(f"Hello {name}")


@piter.command("image2base64", context_settings=context_settings)
def image2base64(
    image_path: str = typer.Option(
        ...,
        "-i",
        help="The path to the input image file to be converted to a base64 string",
    )
) -> str:
    import rich
    from piter.utils.images import image_file_to_base64_url

    rich.print(image_file_to_base64_url(image_path))


def _is_valid_image(item):
    import pipelime.items as pli

    return isinstance(item, (pli.JpegImageItem, pli.BmpImageItem, pli.PngImageItem))


def _process_metadata_value(value):
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _purge_metadata(item):
    return {key: _process_metadata_value(value) for key, value in item.items()}


@piter.command("images_table_simple", context_settings=context_settings)
def images_table_simple(
    title: str = typer.Option(
        "Images Table", help="The title of the generated HTML file"
    ),
    folder: Path = typer.Option(
        ..., help="The path to the folder containing the images"
    ),
    keys: t.List[str] = typer.Option(
        [], help="A list of keys to identify images in the dataset"
    ),
    mkeys: t.List[str] = typer.Option(
        [], help="A list of keys to identify metadata in the dataset"
    ),
    embed: bool = typer.Option(
        False, help="Whether to embed images directly in the HTML file"
    ),
    embed_quality: int = typer.Option(
        50, help="The quality of embedded images (0-100)"
    ),
    output_file: str = typer.Option(
        "",
        help="The path to save the generated HTML file. If not provided, a temporary file will be created",
    ),
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

    # If no keys provided, use all keys from first sample
    if not keys:
        keys = sorted(dataset[0].keys())
    elif mkeys:  # Only filter if either keys or mkeys are provided
        dataset = dataset.map(pst.StageKeysFilter(key_list=keys + mkeys))

    def get_image_url(item: pli.ImageItem):
        if not embed:
            return str(item.local_sources[0])
        return image_file_to_base64_url(item.local_sources[0], embed_quality)

    # Process samples more efficiently using list comprehensions
    processed_data = [
        (
            {
                key: get_image_url(sample[key])
                for key in keys
                if _is_valid_image(sample[key])
            },
            {
                mkey: _purge_metadata(sample[mkey]())
                for mkey in mkeys
                if isinstance(sample[mkey], pli.MetadataItem)
            },
        )
        for sample in track(dataset, total=len(dataset), description="Processing")
    ]

    # Unzip the processed data
    batches, mbatches = map(list, zip(*processed_data)) if processed_data else ([], [])

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
    title: str = typer.Option(
        "Images Clusters", help="The title of the generated HTML file"
    ),
    folder: Path = typer.Option(
        ..., help="The path to the folder containing the images"
    ),
    image_key: str = typer.Option(
        "image", help="The key to identify images in the dataset"
    ),
    label_key: str = typer.Option(
        "metadata.label",
        help="The key to identify labels in the dataset (use dot notation for nested keys)",
    ),
    color_key: str = typer.Option(
        "",
        help="The key to identify colors in the dataset (use dot notation for nested keys)",
    ),
    embed: bool = typer.Option(
        False, help="Whether to embed images directly in the HTML file"
    ),
    embed_quality: int = typer.Option(
        50, help="The quality of embedded images (0-100)"
    ),
    output_file: str = typer.Option(
        "",
        help="The path to save the generated HTML file. If not provided, a temporary file will be created",
    ),
) -> None:
    from piter.renderers.html import ImagesClustersSimpleParams, ImagesClustersSimple
    from piter.utils.images import numpy_to_base64_url, label_to_color, color_rgb_to_hex
    import tempfile
    import pipelime.sequences as pls
    import pipelime.stages as pst
    import pipelime.items as pli
    from rich.progress import track

    dataset = pls.SamplesSequence.from_underfolder(folder)

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
