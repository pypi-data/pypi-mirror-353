# masked_prosody_model

[![PyPI version](https://badge.fury.io/py/masked-prosody-model.svg)](https://badge.fury.io/py/masked-prosody-model)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/minixc/masked_prosody_model/actions/workflows/tests.yml/badge.svg)](https://github.com/minixc/masked_prosody_model/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/minixc/masked_prosody_model/branch/main/graph/badge.svg)](https://codecov.io/gh/minixc/masked_prosody_model)

[![Model on HF](https://huggingface.co/datasets/huggingface/badges/resolve/main/model-on-hf-xl-dark.svg)](https://huggingface.co/cdminix/masked_prosody_model)

A transformer-based model for prosody prediction with masked inputs. This model processes pitch, energy, and voice activity detection features to predict prosodic patterns in speech.

## Installation

```bash
pip install masked_prosody_model
```

Note: `torch` and `torchaudio` need to be installed separately.

## Usage

```python
from masked_prosody_model import MaskedProsodyModel

# Load the pretrained model
model = MaskedProsodyModel.from_pretrained("cdminix/masked_prosody_model")

# Process an audio file and get representations
representation = model.process_audio("some_audio.wav", layer=7)  # layer between 0 and 15, 7 was used in the paper
```

## Acknowledgments

This model was trained using Cloud TPUs supplied by Google's TPU Research Cloud (TRC). We thank them for their support.

