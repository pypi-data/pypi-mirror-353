import functools
import itertools
import re
from typing import Optional

import datasets
import pytest
from outlines import Template, generate, models

from doteval import foreach
from doteval.evaluators import exact_match

ANS_RE = re.compile(r"#### (\-?[0-9\.\,]+)")


@pytest.fixture
def template():
    """Build the prompt template with 4 shots taken from the training set."""
    template = Template.from_string(
        """{% for example in examples %}
    Q: {{ example[0] }}
    A: {{ example[1] }}
    {% endfor %}

    Q: {{ question }}
    A:"""
    )
    examples = gsm8k_dataset("train", 4)
    return functools.partial(template, examples=examples)


@pytest.fixture
def generator():
    """Build the generator once."""
    model = models.llamacpp(
        repo_id="M4-ai/TinyMistral-248M-v2-Instruct-GGUF",
        filename="TinyMistral-248M-v2-Instruct.Q4_K_M.gguf",
        model_kwargs={"n_ctx": 2048, "verbose": False},
    )
    generator = generate.regex(model, r"[1-9][0-9]*")

    return generator


def gsm8k_dataset(split: str, limit: Optional[int] = None):
    """Load and prepare the GSM8K dataset."""
    dataset = datasets.load_dataset(
        path="gsm8k",
        name="main",
        split=split,
        streaming=True,
    )
    samples = ((sample["question"], sample["answer"]) for sample in dataset)
    samples = itertools.islice(samples, None, limit)
    for sample in samples:
        match = ANS_RE.search(sample[1])
        if match:
            match_str = match.group(1).strip()
            match_str = match_str.replace(",", "")
            yield (sample[0], match_str)
        else:
            continue

    return samples


@foreach.gsm8k("test")
def eval_gsm8k(question, answer, generator, template):
    prompt = template(question=question)
    result = generator(prompt, max_tokens=10)
    score = exact_match(result, answer)

    return score
