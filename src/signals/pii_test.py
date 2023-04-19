"""Test the PII signal."""

from ..schema import DataType, Field
from .pii import EMAILS_FEATURE_NAME, PIISignal
from .splitters.text_splitter_test_utils import text_to_expected_spans


def test_pii_fields() -> None:
  signal = PIISignal()
  assert signal.fields(('fake', 'path')) == Field(
      fields={
          EMAILS_FEATURE_NAME:
              Field(repeated_field=Field(dtype=DataType.STRING_SPAN, refers_to=('fake', 'path')))
      })


def test_pii_compute() -> None:
  signal = PIISignal()

  text = 'This is an email nik@test.com. pii@gmail.com are where emails are read.'
  emails = list(signal.compute(data=[text]))

  expected_spans = text_to_expected_spans(text, ['nik@test.com', 'pii@gmail.com'])

  assert emails == [{EMAILS_FEATURE_NAME: expected_spans}]