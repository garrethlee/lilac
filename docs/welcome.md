<h3 align="center" style="font-size: 20px; margin-bottom: 4px">Curate better data for LLMs</h3>
<p align="center">
  <a style="padding: 4px;"  href="https://lilacai-lilac.hf.space/">
    <span style="margin-right: 4px; font-size: 12px">🔗</span> <span style="font-size: 14px">Try the Lilac web demo!</span>
  </a>
  <br/><br/>
  <a href="https://lilacml.com/">
        <img alt="Site" src="https://img.shields.io/badge/Site-lilacml.com-ed2dd0?link=https%3A%2F%2Flilacml.com"/>
    </a>
    <a href="https://discord.gg/jNzw9mC8pp">
        <img alt="Discord" src="https://img.shields.io/badge/Join-important.svg?color=ed2dd0&label=Discord&logo=slack" />
    </a>
    <a href="https://github.com/lilacai/lilac/blob/main/LICENSE">
          <img alt="License Apache 2.0" src="https://img.shields.io/badge/License-Apache 2.0-blue.svg?style=flat&color=ed2dd0" height="20" width="auto">
    </a>
    <br/>
    <a href="https://github.com/lilacai/lilac">
      <img src="https://img.shields.io/github/stars/lilacai/lilac?style=social" />
    </a>
    <a href="https://twitter.com/lilac_ai">
      <img src="https://img.shields.io/twitter/follow/lilac_ai" alt="Follow on Twitter" />
    </a>
</p>

Lilac helps you **curate data** for LLMs, from RAGs to fine-tuning datasets.

Lilac runs **on-device** using open-source LLMs with a UI and Python API for:

- **Exploring** datasets with natural language (documents)
- **Annotating & structuring** data (e.g. PII detection, profanity, text statistics)
- **Semantic search** to find similar results to a query
- **Conceptual search** to find and tag results that match a fuzzy concept (e.g. low command of
  English language)
- **Clustering** data semantically for understanding & deduplication
- **Labeling** and **Bulk Labeling** to curate data <br>

<div align="center">
  <iframe width="672" height="378" src="https://www.youtube.com/embed/RrcvVC3VYzQ?si=K-qRY2fZ_RAjFfMw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>
<br>
<br>
<h3>Core features</h3>
<table style="border-spacing:0">
  <tr>
    <td style="width:200px;padding-right:10px;">
      <h4>Semantic and keyword search</h4>
      <p style="color:rgb(75,75,75)">Query large datasets instantaneously</p>
      <p><a href="https://lilacai-lilac.hf.space/datasets#lilac/OpenOrca-100k&query=%7B%22searches%22%3A%5B%7B%22path%22%3A%5B%22response%22%5D%2C%22type%22%3A%22semantic%22%2C%22query%22%3A%22hacking%20a%20computer%22%2C%22embedding%22%3A%22gte-small%22%7D%5D%7D">Try it →</a></p>
    </td>
    <td><video loop muted autoplay controls src="_static/welcome/semantic-search.mp4"></video></td>
  </tr>
</table>

<br/>
<br/>

<table style="border-spacing:0">
  <tr>
    <td style="width:200px;padding-left:10px;">
      <h4>Dataset insights</h4>
      <p style="color:rgb(75,75,75)">See a mile-high overview of the dataset</p>
      <p><a href="https://lilacai-lilac.hf.space/datasets#lilac/OpenOrca-100k&insightsOpen=true">Try it →</a></p>
    </td>
    <td><video loop muted autoplay controls src="_static/welcome/insights.mp4"></video></td>
  </tr>
</table>

<br/>
<br/>

<table style="border-spacing:0">
  <tr>
    <td style="width:200px;padding-left:10px;">
      <h4>PII, duplicates, language detection, or add your own signal</h4>
      <p style="color:rgb(75,75,75)">Enrich natural language with structured metadata</p>
      <p><a href="https://lilacai-lilac.hf.space/datasets#lilac/OpenOrca-100k&query=%7B%22filters%22%3A%5B%7B%22path%22%3A%5B%22question%22%2C%22pii%22%2C%22emails%22%2C%22*%22%5D%2C%22op%22%3A%22exists%22%7D%5D%7D">Find emails →</a></p>
    </td>
    <td><video loop muted autoplay controls src="_static/welcome/signals.mp4"></video></td>
  </tr>
</table>

<br/>
<br/>

<table style="border-spacing:0">
  <tr>
    <td style="width:200px;padding-left:10px;">
      <h4>Make your own concepts</h4>
      <p style="color:rgb(75,75,75)">Curate a set of concepts for your business needs</p>
      <p><a href="https://lilacai-lilac.hf.space/concepts#lilac/profanity">Try a concept→</a></p>
    </td>
    <td><video loop muted autoplay controls src="_static/welcome/concepts.mp4"></video></td>
  </tr>
</table>

<br/>
<br/>

<table style="border-spacing:0">
  <tr>
    <td style="width:200px;padding-left:10px;">
      <h4>Download the enriched data</h4>
      <p style="color:rgb(75,75,75)">Continue working in your favorite data stack</p>
    </td>
    <td><video loop muted autoplay controls src="_static/welcome/download.mp4"></video></td>
  </tr>
</table>

## 🔥 Getting started

### 💻 Install

```sh
pip install lilac[all]
```

If you prefer no local installation, you can fork the
[fork the HuggingFace Spaces demo](https://lilacai-lilac.hf.space/). Documentation
[here](https://lilacml.com/huggingface/huggingface_spaces.html).

### 🌐 Start a webserver

Start a Lilac webserver from the CLI:

```sh
lilac start ~/my_project
```

Or start the Lilac webserver from Python:

```py
import lilac as ll

ll.start_server(project_dir='~/my_project')
```

This will open start a webserver at http://localhost:5432/ where you can now load datasets and
explore them.

### Run via Docker

Build the image after cloning the repo:

```sh
docker build -t lilac .
```

The container runs on the virtual port `8000`, this command maps it to the host machine port `5432`.

If you have an existing lilac project, mount it and set the `LILAC_PROJECT_DIR` environment
variable:

```sh
docker run -it \
  -p 5432:8000 \
  --volume /host/path/to/data:/data \
  -e LILAC_PROJECT_DIR="/data" \
  lilac
```

### 📊 Load data

Datasets can be loaded directly from HuggingFace, CSV, JSON,
[LangSmith from LangChain](https://www.langchain.com/langsmith), SQLite,
[LLamaHub](https://llamahub.ai/), Pandas, Parquet, and more. More documentation
[here](https://lilacml.com/datasets/dataset_load.html).

```python
import lilac as ll

ll.set_project_dir('~/my_project')

config = ll.DatasetConfig(
  namespace='local',
  name='imdb',
  source=ll.HuggingFaceSource(dataset_name='imdb'))

dataset = ll.create_dataset(config)
```

If you prefer, you can load datasets directly from the UI without writing any Python:

<img width="600" alt="image" src="https://github.com/lilacai/lilac/assets/1100749/d5d385ce-f11c-47e6-9c00-ea29983e24f0">

### 🔎 Explore

> [🔗 Try OpenOrca-100K before installing!](https://lilacai-lilac.hf.space/datasets#lilac/OpenOrca-100k)

Once we've loaded a dataset, we can explore it from the UI and get a sense for what's in the data.
More documentation [here](https://lilacml.com/datasets/dataset_explore.html).

<img alt="image" src="_static/dataset/dataset_explore.png">

### ⚡ Annotate with Signals (PII, Text Statistics, Language Detection, Neardup, etc)

Annotating data with signals will produce another column in your data.

```python
import lilac as ll

ll.set_project_dir('~/my_project')

dataset = ll.get_dataset('local', 'imdb')

# [Language detection] Detect the language of each document.
dataset.compute_signal(ll.LangDetectionSignal(), 'text')

# [PII] Find emails, phone numbers, ip addresses, and secrets.
dataset.compute_signal(ll.PIISignal(), 'text')

# [Text Statistics] Compute readability scores, number of chars, TTR, non-ascii chars, etc.
dataset.compute_signal(ll.PIISignal(), 'text')

# [Near Duplicates] Computes clusters based on minhash LSH.
dataset.compute_signal(ll.NearDuplicateSignal(), 'text')

# Print the resulting manifest, with the new field added.
print(dataset.manifest())
```

We can also compute signals from the UI:

<img width="600" alt="image" src="_static/dataset/dataset_compute_signal_modal.png">

### 🔎 Search

Semantic and conceptual search requires computing an embedding first:

```python
dataset.compute_embedding('gte-small', path='text')
```

#### Semantic search

In the UI, we can search by semantic similarity or by classic keyword search to find chunks of
documents similar to a query:

<img width="600" alt="image" src="https://github.com/lilacai/lilac/assets/1100749/4adb603e-8dca-43a3-a492-fd862e194a5a">

<img width="600" alt="image" src="https://github.com/lilacai/lilac/assets/1100749/fdee2127-250b-4e06-9ff9-b1023c03b72f">

We can run the same search in Python:

```python
rows = dataset.select_rows(
  columns=['text', 'label'],
  searches=[
    ll.SemanticSearch(
      path='text',
      embedding='gte-small')
  ],
  limit=1)

print(list(rows))
```

#### Conceptual search

Conceptual search is a much more controllable and powerful version of semantic search, where
"concepts" can be taught to Lilac by providing positive and negative examples of that concept.

Lilac provides a set of built-in concepts, but you can create your own for very specif

<img width="600" alt="image" src="https://github.com/lilacai/lilac/assets/1100749/9941024b-7c24-4d87-ae46-925f8da435e1">

We can create a concept in Python with a few examples, and search by it:

```python
concept_db = ll.DiskConceptDB()
db.create(namespace='local', name='spam')
# Add examples of spam and not-spam.
db.edit('local', 'spam', ll.concepts.ConceptUpdate(
  insert=[
    ll.concepts.ExampleIn(label=False, text='This is normal text.'),
    ll.concepts.ExampleIn(label=True, text='asdgasdgkasd;lkgajsdl'),
    ll.concepts.ExampleIn(label=True, text='11757578jfdjja')
  ]
))

# Search by the spam concept.
rows = dataset.select_rows(
  columns=['text', 'label'],
  searches=[
    ll.ConceptSearch(
      path='text',
      concept_namespace='lilac',
      concept_name='spam',
      embedding='gte-small')
  ],
  limit=1)

print(list(rows))
```

### 🏷️ Labeling

Lilac allows you to label individual points, or slices of data:
<img width="600" alt="image" src="_static/dataset/dataset_add_label_tag.png">

We can also label all data given a filter. In this case, adding the label "short" to all text with a
small amount of characters. This field was produced by the automatic `text_statistics` signal.

<img width="600" alt="image" src="_static/dataset/dataset_add_label_all_short.png">

We can do the same in Python:

```python
dataset.add_labels(
  'short',
  filters=[
    (('text', 'text_statistics', 'num_characters'), 'less', 1000)
  ]
)
```

Labels can be exported for downstream tasks. Detailed documentation
[here](https://lilacml.com/datasets/dataset_labels.html).

## 💬 Contact

For bugs and feature requests, please
[file an issue on GitHub](https://github.com/lilacai/lilac/issues).

For general questions, please [visit our Discord](https://discord.com/invite/jNzw9mC8pp).
