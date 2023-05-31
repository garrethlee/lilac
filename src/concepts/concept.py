"""Defines the concept and the concept models."""
import random
import uuid
from enum import Enum
from typing import Any, Iterable, Literal, Optional, Union, cast

import numpy as np
from pydantic import BaseModel
from scipy.interpolate import interp1d
from sklearn.exceptions import NotFittedError
from sklearn.linear_model import LogisticRegression

from ..data.dataset import Column, UnaryOp, val
from ..db_manager import get_dataset
from ..embeddings.embedding import get_embed_fn
from ..schema import (
  TEXT_SPAN_END_FEATURE,
  TEXT_SPAN_START_FEATURE,
  UUID_COLUMN,
  VALUE_KEY,
  Path,
  RichData,
  SignalInputType,
)
from ..signals.signal import TextEmbeddingSignal, get_signal_cls
from ..signals.splitters.text_splitter_spacy import SentenceSplitterSpacy
from ..utils import DebugTimer

LOCAL_CONCEPT_NAMESPACE = 'local'

# Number of randomly sampled negative examples to use for training. This is used to obtain a more
# balanced model that works with a specific dataset.
DEFAULT_NUM_NEG_EXAMPLES = 100


class ConceptColumnInfo(BaseModel):
  """Information about a dataset associated with a concept."""
  # Namespace of the dataset.
  namespace: str
  # Name of the dataset.
  name: str
  # Path holding the text to use for negative examples.
  path: Path

  num_negative_examples = DEFAULT_NUM_NEG_EXAMPLES


class ExampleOrigin(BaseModel):
  """The origin of an example."""
  # The namespace that holds the dataset.
  dataset_namespace: str

  # The name of the dataset.
  dataset_name: str

  # The id of row in the dataset that the example was added from.
  dataset_row_id: str


DraftId = Union[Literal['main'], str]
DRAFT_MAIN = 'main'


class ExampleIn(BaseModel):
  """An example in a concept without the id (used for adding new examples)."""
  label: bool
  text: Optional[str]
  img: Optional[bytes]
  origin: Optional[ExampleOrigin]
  # The name of the draft to put the example in. If None, puts it in the main draft.
  draft: Optional[DraftId] = DRAFT_MAIN


class Example(ExampleIn):
  """A single example in a concept used for training a concept model."""
  id: str


class Concept(BaseModel):
  """A concept is a collection of examples."""
  # The namespace of the concept.
  namespace: str = LOCAL_CONCEPT_NAMESPACE
  # The name of the concept.
  concept_name: str
  # The type of the data format that this concept represents.
  type: SignalInputType
  data: dict[str, Example]
  version: int = 0

  def drafts(self) -> list[DraftId]:
    """Gets all the drafts for the concept."""
    drafts: set[DraftId] = set([DRAFT_MAIN])  # Always return the main draft.
    for example in self.data.values():
      if example.draft:
        drafts.add(example.draft)
    return list(sorted(drafts))


class Sensitivity(str, Enum):
  """Sensitivity levels of a concept.

  The sensitivity of concept models vary as a function of how powerful the embedding is, and how
  complicated or subtle the concept is. Therefore, we provide a way to control the sensitivity of
  the concept model.

  - `VERY_SENSITIVE` will fire "True" more often and therefore introduce more false positives
  (will add things that don't fit in the concept).
  - `NOT_SENSITIVE` will fire "True" less often and therefore introduce more false negatives
  (misses things that fit in the concept).

  """
  NOT_SENSITIVE = 'not sensitive'
  BALANCED = 'balanced'
  SENSITIVE = 'sensitive'
  VERY_SENSITIVE = 'very sensitive'

  def __repr__(self) -> str:
    return self.value


# Assuming random text will likely not be in the concept, these percentiles control how likely a
# random text will be classified as "True".
SENSITIVITY_PERCENTILES: dict[Sensitivity, float] = {
  Sensitivity.NOT_SENSITIVE: 1,  # 1% of random negative text will be classified as "True".
  Sensitivity.BALANCED: 3,  # Likewise, but for 3%.
  Sensitivity.SENSITIVE: 10,  # Likewise, but for 10%.
  Sensitivity.VERY_SENSITIVE: 20,  # Likewise, but for 20%.
}


class LogisticEmbeddingModel(BaseModel):
  """A model that uses logistic regression with embeddings."""

  class Config:
    arbitrary_types_allowed = True
    underscore_attrs_are_private = True

  version: int = -1

  # The following fields are excluded from JSON serialization, but still pickleable.
  # See `notebooks/Toxicity.ipynb` for an example of training a concept model.
  _model: LogisticRegression = LogisticRegression(
    class_weight='balanced', C=30, tol=1e-5, warm_start=True, max_iter=1_000, n_jobs=-1)
  _thresholds: dict[Sensitivity, float] = {}

  def score_embeddings(self, embeddings: np.ndarray, sensitivity: Sensitivity) -> np.ndarray:
    """Get the scores for the provided embeddings."""
    try:
      scores = self._model.predict_proba(embeddings)[:, 1]
      threshold = self._thresholds[sensitivity]
      # Map [0, threshold, 1] to [0, 0.5, 1].
      interpolate_fn = interp1d([0, threshold, 1], [0, 0.4999, 1])
      return interpolate_fn(scores)
    except NotFittedError:
      return np.random.rand(len(embeddings))

  def fit(self, embeddings: np.ndarray, labels: list[bool]) -> None:
    """Fit the model to the provided embeddings and labels."""
    if len(set(labels)) < 2:
      return
    self._model.fit(embeddings, labels)
    scores = self._model.predict_proba(embeddings)[:, 1]
    negative_scores = [score for label, score in zip(labels, scores) if not label]
    thresholds = np.percentile(negative_scores, [100 - p for p in SENSITIVITY_PERCENTILES.values()])
    self._thresholds = dict(zip(SENSITIVITY_PERCENTILES.keys(), thresholds))  # type: ignore


def draft_examples(concept: Concept, draft: DraftId) -> dict[str, Example]:
  """Get the examples in the provided draft by overriding the main draft."""
  draft_examples: dict[str, dict[str, Example]] = {}
  for id, example in concept.data.items():
    draft_examples.setdefault(example.draft or DRAFT_MAIN, {})[example.id] = example

  if draft == DRAFT_MAIN:
    return draft_examples.get(DRAFT_MAIN, {})

  if draft not in draft_examples:
    raise ValueError(
      f'Draft {draft} not found in concept. Found drafts: {list(draft_examples.keys())}')

  # Map the text of the draft to its id so we can dedup with main.
  draft_text_ids = {example.text: id for id, example in draft_examples[draft].items()}

  # Write each of examples from main to the draft examples only if the text does not appear in the
  # draft.
  for id, example in draft_examples[DRAFT_MAIN].items():
    if example.text not in draft_text_ids:
      draft_examples[draft][id] = example

  return draft_examples[draft]


class ConceptModel(BaseModel):
  """A concept model. Stores all concept model drafts and manages syncing."""
  # The concept that this model is for.
  namespace: str
  concept_name: str

  # The name of the embedding for this model.
  embedding_name: str
  version: int = -1

  column_info: Optional[ConceptColumnInfo] = None

  class Config:
    arbitrary_types_allowed = True
    underscore_attrs_are_private = True

  def __init__(self, **kwargs: Any):
    super().__init__(**kwargs)
    self._generate_random_negatives()

  def _generate_random_negatives(self) -> None:
    if not self.column_info:
      return

    # Sorting by UUID column will return examples with random order.
    db = get_dataset(self.column_info.namespace, self.column_info.name)
    docs = db.select_rows([Column(val(self.column_info.path), alias='text')],
                          filters=[(self.column_info.path, UnaryOp.EXISTS)],
                          sort_by=[UUID_COLUMN],
                          limit=self.column_info.num_negative_examples)
    docs = docs.df()['text']
    sentences = _split_docs_into_sentences(docs)
    # Choose a random unique subset of sentences.
    num_samples = min(self.column_info.num_negative_examples, len(sentences))
    negatives = random.sample(sentences, num_samples)
    for text in negatives:
      ex = Example(label=False, text=text, id=uuid.uuid4().hex)
      self._negative_examples[ex.id] = ex

  # The following fields are excluded from JSON serialization, but still pickleable.
  # Maps a concept id to the embeddings.
  _embeddings: dict[str, np.ndarray] = {}
  _logistic_models: dict[DraftId, LogisticEmbeddingModel] = {}
  _negative_examples: dict[str, Example] = {}

  def score_embeddings(self, draft: DraftId, embeddings: np.ndarray,
                       sensitivity: Sensitivity) -> np.ndarray:
    """Get the scores for the provided embeddings."""
    return self._get_logistic_model(draft).score_embeddings(embeddings, sensitivity)

  def score(self, draft: DraftId, examples: Iterable[RichData],
            sensitivity: Sensitivity) -> list[float]:
    """Get the scores for the provided examples."""
    embedding_signal = get_signal_cls(self.embedding_name)()
    if not isinstance(embedding_signal, TextEmbeddingSignal):
      raise ValueError(f'Only text embedding signals are currently supported for concepts. '
                       f'"{self.embedding_name}" is a {type(embedding_signal)}.')

    embed_fn = get_embed_fn(self.embedding_name)
    embeddings = np.array(embed_fn(examples))
    return self._get_logistic_model(draft).score_embeddings(embeddings, sensitivity).tolist()

  def coef(self, draft: DraftId) -> np.ndarray:
    """Get the coefficients of the underlying ML model."""
    return self._get_logistic_model(draft)._model.coef_.flatten()

  def _get_logistic_model(self, draft: DraftId) -> LogisticEmbeddingModel:
    """Get the logistic model for the provided draft."""
    if draft not in self._logistic_models:
      self._logistic_models[draft] = LogisticEmbeddingModel(
        namespace=self.namespace,
        concept_name=self.concept_name,
        embedding_name=self.embedding_name,
        version=-1)
    return self._logistic_models[draft]

  def sync(self, concept: Concept) -> bool:
    """Update the model with the latest labeled concept data."""
    if concept.version == self.version:
      # The model is up to date.
      return False

    self._compute_embeddings(concept)

    # Fit each of the drafts, sort by draft name for deterministic behavior.
    for draft in concept.drafts():
      examples = draft_examples(concept, draft)
      all_examples = {**examples, **self._negative_examples}
      embeddings = np.array([self._embeddings[id] for id in all_examples.keys()])
      labels = [example.label for example in all_examples.values()]

      model = self._get_logistic_model(draft)
      model.fit(embeddings, labels)

      # Synchronize the model version with the concept version.
      model.version = concept.version

    # Synchronize the model version with the concept version.
    self.version = concept.version

    return True

  def _compute_embeddings(self, concept: Concept) -> None:
    embedding_signal = get_signal_cls(self.embedding_name)()
    if not isinstance(embedding_signal, TextEmbeddingSignal):
      raise ValueError(f'Only text embedding signals are currently supported for concepts. '
                       f'"{self.embedding_name}" is a {type(embedding_signal)}.')

    embed_fn = get_embed_fn(self.embedding_name)
    concept_embeddings: dict[str, np.ndarray] = {}

    # Compute the embeddings for the examples with cache miss.
    texts_of_missing_embeddings: dict[str, str] = {}
    all_examples = {**concept.data, **self._negative_examples}
    for id, example in all_examples.items():
      if id in self._embeddings:
        # Cache hit.
        concept_embeddings[id] = self._embeddings[id]
      else:
        # Cache miss.
        # TODO(smilkov): Support images.
        texts_of_missing_embeddings[id] = example.text or ''

    missing_ids = texts_of_missing_embeddings.keys()
    with DebugTimer('Computing embeddings for examples in concept '
                    f'"{self.namespace}/{self.concept_name}/{self.embedding_name}"'):
      missing_embeddings = embed_fn(list(texts_of_missing_embeddings.values()))

    for id, embedding in zip(missing_ids, missing_embeddings):
      concept_embeddings[id] = embedding
    self._embeddings = concept_embeddings


def _split_docs_into_sentences(docs: Iterable[str]) -> list[str]:
  splitter = SentenceSplitterSpacy()
  doc_spans = list(splitter.compute(docs))
  sentences: list[str] = []
  for sentence_spans, text in zip(doc_spans, docs):
    for span in cast(Iterable[Any], sentence_spans):
      start = span[VALUE_KEY][TEXT_SPAN_START_FEATURE]
      end = span[VALUE_KEY][TEXT_SPAN_END_FEATURE]
      sentences.append(text[start:end])
  return sentences
