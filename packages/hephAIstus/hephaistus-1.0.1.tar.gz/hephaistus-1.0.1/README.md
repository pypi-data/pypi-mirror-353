[![PyPI](https://img.shields.io/pypi/v/hephaistus.svg)](https://pypi.python.org/pypi/hephAIstus)

# Hephaestus - God of the Forge

`hephaestus` is a Python package that has a variety of different AI models to assist DevOps Engineers. All of these models run on your local
computer and do not get saved online at all. This will allow the user to safely and securely discuss any topic with the AI bot without any
potential data leak.

These models use `gpt4all` and `ollama`.

## Install

To install this package, run `pip install hephAIstus`.

## Hephaestus' Forge

The first AI model is `forge()` and it uses `gpt4all`. To use it, simply run the following commands in a Python terminal.

```python
from hephaistus import Hephaestus

heph = Hephaestus()
heph.forge()
```

This will then start a conversation with an AI bot. You can specify the AI model to use with the `model_version` parameter in `forge`. If no
model is specified, then it will use the default.

After the conversation is finished, the user can save the results to a text file.

## Hephaestus' Hammer

Alternatively, you can use `ollama` with `hammer()`. To use it, simply run the following commands in a Python terminal.

```python
from hephaistus import Hephaestus

heph = Hephaestus()
heph.hammer()
```

This will then start a conversation with an AI bot. You can specify the AI model to use with the `model_version` parameter in `forge`. If no
model is specified, then it will use the default.

To use one of the provided AI models (found in `src/hephaestus/models`), run `make create_models` and all relevant models will be
initialized.

After the conversation is finished, the user can save the results to a text file.

### Continue chat

You can continue a previous conversation, from either `forge()` or `hammer()`, by running `load_save(file_name)`. This will then load a
previously saved conversation to be used by `hammer()`. 

Note, `forge()` does not allow a conversation to be continued like this. 