---
key: pypi/pytorch-clip-interrogator
source: pypi
name: pytorch-clip-interrogator
package: pytorch-clip-interrogator
description: Prompt engineering tool using BLIP 1/2 + CLIP Interrogate approach.
registry_url: https://pypi.org/project/pytorch-clip-interrogator/
version: 2023.5.30.0
last_release: '2023-06-01'
repository_url: null
repository_declared_in_metadata: false
license_stated: null
author: Sergei Belousov aka BeS
probes:
- pypi:simple-index-sweep
probe_class: domain-specific
found_by:
- search
first_seen: '2026-08-28'
---

# pytorch_clip_interrogator: Image-To-Promt.
[![Downloads](https://pepy.tech/badge/pytorch_clip_interrogator)](https://pepy.tech/project/pytorch_clip_interrogator)
[![Downloads](https://pepy.tech/badge/pytorch_clip_interrogator/month)](https://pepy.tech/project/pytorch_clip_interrogator)
[![Downloads](https://pepy.tech/badge/pytorch_clip_interrogator/week)](https://pepy.tech/project/pytorch_clip_interrogator)


## Install package

```bash
pip install pytorch_clip_interrogator
```

## Install the latest version

```bash
pip install --upgrade git+https://github.com/bes-dev/pytorch_clip_interrogator.git
```

## Features
- Fully compatible with models from Huggingface.
- Supports BLIP 1/2 model.
- Support batch processing.

## Usage

### Simple code

```python
import torch
import requests
from PIL import Image
from pytorch_clip_interrogator import PromptEngineer

# build pipeline
pipe = PromptEngineer(
    blip_model="Salesforce/blip2-opt-2.7b",
    clip_model="openai/clip-vit-base-patch32",
    device="cuda",
    torch_dtype=torch.float16
)

# load image
img_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg'
image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')


# generate caption
print(pipe(image))
```
