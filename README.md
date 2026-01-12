# PITER - PIpelime TEmplate Rendering 

<img src='docs/images/logo.jpg' height=256 />

Create stunning interactive HTML reports from Pipelime datasets with minimal effort.

## Installation

```console
pip install -e .
```

## Examples

### Images Table

Given a Pipelime dataset (***$INPUT_DATASET***) with several image items (***image***, ***image1***), and metadata (***meta1***, ***meta2***) launch:

```
piter images_table_simple --folder $INPUT_DATASET --embed --keys image --keys image1 --mkeys meta1 --mkeys meta2 --title "My Cool Report!" --output-file /tmp/myreport.html
```

NB: 

* ***keys*** is for images and ***mkeys*** is for metadata
* `embed` is to bake images into HTML as base64 (this is portable version of the report)

### Images Clusters

Given a Pipelime dataset (***$INPUT_DATASET***) with images item (***image***)  and a cluster label nested inside a metadata (***metadata.cluster***) launch:

```
piter images_clusters_simple --folder $INPUT_DATASET --embed --output-file /tmp/myreport.html --label-key metadata.cluster
```