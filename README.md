# PITER - PIpelime TEmplate Rendering

<img src='docs/images/logo.jpg' height=256 />

PIPELIME -> HTML Pages

## Installation

```console
pip install -e .
```

## Examples

Given a Pipelime dataset (***$INPUT_DATASET***) with several image items (***image***, ***image1***, ***image2***), launch:

```
piter images_table_simple --folder $INPUT_DATASET --keys image --keys image1 --keys image2 --title "My Cool Report!" --output-file /tmp/myreport.html
```