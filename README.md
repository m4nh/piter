# PITER - PIpelime TEmplate Rendering 

<img src='docs/images/logo.jpg' height=256 />

Create stunning interactive HTML reports from Pipelime datasets with minimal effort.

## Installation

```console
pip install -e .
```

## Examples

<details>
<summary>Images Table</summary>

Given a Pipelime dataset (***$INPUT_DATASET***) with several image items (***image***, ***image1***), and metadata (***meta1***, ***meta2***) launch:

```
piter images_table_simple --folder $INPUT_DATASET --embed --keys image --keys image1 --mkeys meta1 --mkeys meta2 --title "My Cool Report!" --output-file /tmp/myreport.html
```

NB: 

* ***keys*** is for images and ***mkeys*** is for metadata
* `embed` is to bake images into HTML as base64 (this is portable version of the report)

</details>

<details>
<summary>Images Clusters</summary>

Given a Pipelime dataset (***$INPUT_DATASET***) with images item (***image***)  and a cluster label nested inside a metadata (***metadata.cluster***) launch:

```
piter images_clusters_simple --folder $INPUT_DATASET --embed --output-file /tmp/myreport.html --label-key metadata.cluster
```

</details>

<details>
<summary>Anomaly Interactive</summary>

Given a Pipelime dataset (***$INPUT_DATASET***) with original images (***image***), colored heatmaps (***colored_heatmap***), and anomaly metadata (***debug_metadata***), launch:

```
piter anomaly_interactive_simple --folder $INPUT_DATASET --embed --output-file /tmp/myreport.html --image-key image --heatmap-key colored_heatmap --debug-metadata-key debug_metadata --metadata-key metadata
```

</details>