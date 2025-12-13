import base64
from pathlib import Path

import pytest
from PIL import Image
from typer.testing import CliRunner

import piter.cli.cli as cli_module
from piter.cli.cli import piter

pli_items = pytest.importorskip("pipelime.items")
pls_sequences = pytest.importorskip("pipelime.sequences")
pytest.importorskip("pipelime.stages")
pytest.importorskip("rich")


runner = CliRunner()


def test_check_command_outputs_name():
    result = runner.invoke(piter, ["check", "--name", "Alice"])

    assert result.exit_code == 0
    assert "Hello Alice" in result.stdout


def test_image2base64_command(tmp_path, monkeypatch):
    # Minimal image to feed the CLI
    img_path = tmp_path / "sample.png"
    Image.new("RGB", (2, 2), "red").save(img_path)

    result = runner.invoke(piter, ["image2base64", "-i", str(img_path)])

    assert result.exit_code == 0
    output = result.stdout.strip()
    assert output.startswith("data:image/png;base64,")
    # Ensure the payload is valid base64
    base64.b64decode(output.split(",", 1)[1])


def test_images_table_simple_command_writes_html(tmp_path, monkeypatch):
    img1 = tmp_path / "img1.png"
    Image.new("RGB", (2, 2), "blue").save(img1)
    img2 = tmp_path / "img2.png"
    Image.new("RGB", (2, 2), "green").save(img2)

    class DummyImage:
        def __init__(self, path: Path):
            self.local_sources = [path]

        def __call__(self):
            return None

    class DummySequence:
        def __init__(self, samples):
            self.samples = samples

        def __len__(self):
            return len(self.samples)

        def __iter__(self):
            return iter(self.samples)

        def __getitem__(self, idx):
            return self.samples[idx]

        def map(self, *_args, **_kwargs):
            return self

    dataset = [
        {"image": DummyImage(img1)},
        {"image": DummyImage(img2)},
    ]

    # Make CLI's image checks accept our dummy class
    monkeypatch.setattr(pli_items, "JpegImageItem", DummyImage)
    monkeypatch.setattr(pli_items, "BmpImageItem", DummyImage)
    monkeypatch.setattr(pli_items, "PngImageItem", DummyImage)

    monkeypatch.setattr(
        pls_sequences.SamplesSequence,
        "from_underfolder",
        staticmethod(lambda _folder: DummySequence(dataset)),
    )
    monkeypatch.setattr(cli_module, "_is_valid_image", lambda _item: True)

    output_file = tmp_path / "report.html"
    result = runner.invoke(
        piter,
        [
            "images_table_simple",
            "--folder",
            str(tmp_path),
            "--keys",
            "image",
            "--output-file",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    html = output_file.read_text()
    assert str(img1) in html and str(img2) in html


def test_images_clusters_simple_command_writes_html(tmp_path, monkeypatch):
    img1 = tmp_path / "img1.png"
    Image.new("RGB", (2, 2), "blue").save(img1)
    img2 = tmp_path / "img2.png"
    Image.new("RGB", (2, 2), "green").save(img2)

    class DummyImage:
        def __init__(self, path: Path):
            self.local_sources = [path]

        def __call__(self):
            return None

    class DummyMetadata:
        def __init__(self, label):
            self._label = label

        def __call__(self):
            return {"label": self._label}

    class DummySequence:
        def __init__(self, samples):
            self.samples = samples

        def __len__(self):
            return len(self.samples)

        def __iter__(self):
            return iter(self.samples)

        def __getitem__(self, idx):
            return self.samples[idx]

        def map(self, *_args, **_kwargs):
            return self

    dataset = [
        {"image": DummyImage(img1), "metadata": DummyMetadata(0)},
        {"image": DummyImage(img2), "metadata": DummyMetadata(1)},
    ]

    # Make CLI's image checks accept our dummy class
    monkeypatch.setattr(pli_items, "JpegImageItem", DummyImage)
    monkeypatch.setattr(pli_items, "BmpImageItem", DummyImage)
    monkeypatch.setattr(pli_items, "PngImageItem", DummyImage)

    monkeypatch.setattr(
        pls_sequences.SamplesSequence,
        "from_underfolder",
        staticmethod(lambda _folder: DummySequence(dataset)),
    )
    monkeypatch.setattr(cli_module, "_is_valid_image", lambda _item: True)

    output_file = tmp_path / "clusters.html"
    result = runner.invoke(
        piter,
        [
            "images_clusters_simple",
            "--folder",
            str(tmp_path),
            "--output-file",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    html = output_file.read_text()
    assert str(img1) in html and str(img2) in html
