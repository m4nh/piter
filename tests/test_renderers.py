import datetime

import pytest

from piter.renderers.html import (
    AnomalyInteractiveSample,
    AnomalyInteractiveSimple,
    AnomalyInteractiveSimpleParams,
    HTMLRenderer,
    ImagesClustersSimple,
    ImagesClustersSimpleParams,
    ImagesTableSimple,
    ImagesTableSimpleParams,
    GlobalParams,
    TemplatesCollection,
    templates_path,
)


def test_templates_path_contains_expected_templates():
    path = templates_path()

    assert path.exists()
    assert (path / TemplatesCollection.IMAGES_TABLE_SIMPLE).exists()
    assert (path / TemplatesCollection.IMAGES_CLUSTERS_SIMPLE).exists()
    assert (path / TemplatesCollection.ANOMALY_INTERACTIVE_SIMPLE).exists()


def test_images_table_simple_renders_images_and_metadata():
    params = ImagesTableSimpleParams(
        title="Table Title",
        keys=["image"],
        images=[{"image": "img1.png"}, {"image": "img2.png"}],
        mkeys=["meta"],
        metadatas=[{"meta": {"foo": "bar"}}, {"meta": {"foo": "baz"}}],
        group_size=1,
        show_indices=True,
    )

    html = ImagesTableSimple().render(params)

    assert "Table Title" in html
    assert "img1.png" in html and "img2.png" in html
    assert "foo" in html and "bar" in html and "baz" in html
    assert "group-divider" in html  # group_size forces a divider between rows


def test_images_clusters_simple_renders_clusters_with_colors():
    params = ImagesClustersSimpleParams(
        title="Clusters",
        images_clusters={0: ["a.png", "b.png"], 1: ["c.png"]},
        labels_colors={0: "#ff0000", 1: "#00ff00"},
    )

    html = ImagesClustersSimple().render(params)

    assert "Clusters" in html
    assert "a.png" in html and "c.png" in html
    assert "border-[#ff0000]" in html
    assert "border-[#00ff00]" in html


def test_anomaly_interactive_simple_renders_samples():
    params = AnomalyInteractiveSimpleParams(
        title="Anomaly Report",
        samples=[
            AnomalyInteractiveSample(
                image_path="img1.png",
                heatmap_path="heat1.png",
                sample_score=1.23,
                heatmap_bounds=[0.1, 1.23],
                sample_id="sample-1",
                dataset_id="set-a",
                original_filename="image-a.png",
                file_id="image-a.png",
            ),
            AnomalyInteractiveSample(
                image_path="img2.png",
                heatmap_path="heat2.png",
                sample_score=4.56,
                heatmap_bounds=[0.2, 4.56],
                sample_id="sample-2",
                dataset_id="set-b",
                original_filename="image-b.png",
                file_id="image-b.png",
            ),
        ],
    )

    html = AnomalyInteractiveSimple().render(params)

    assert "Anomaly Report" in html
    assert "img1.png" in html and "heat2.png" in html
    assert "sample-1" in html and "image-b.png" in html


def test_global_params_footer_defaults_to_current_year():
    current_year = str(datetime.datetime.now().year)
    footer = GlobalParams().footnotes

    assert current_year in footer
