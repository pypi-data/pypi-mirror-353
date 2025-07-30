import re
from typing import Iterator

import datasets

from doteval.datasets.base import Dataset


class GSM8K(Dataset):
    """GSM8K dataset iterator"""

    name = "gsm8k"
    splits = ["train", "test"]
    columns = ["question", "answer"]

    def __init__(self, split: str, **kwargs):
        # Load streaming dataset and get metadata
        self.dataset = datasets.load_dataset(
            "gsm8k", "main", split=split, streaming=True
        )
        self.num_rows = self.dataset.info.splits[split].num_examples

        # Answer extraction regex
        self.answer_rx = re.compile(r"#### (\-?[0-9\.\,]+)")

    def __iter__(self) -> Iterator[tuple[str, str]]:
        for item in self.dataset:
            question = item["question"]
            answer = item["answer"]

            match = self.answer_rx.search(answer)
            if match:
                answer = match.group(1).strip().replace(",", "")
                yield (question, answer)


from doteval.datasets.base import _registry  # noqa: E402

_registry.register(GSM8K)
