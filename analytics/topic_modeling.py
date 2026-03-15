#!/usr/bin/env python3
"""Compare SERP topic distributions between generative and non-generative result sets.

Input format: CSV/JSONL with columns/keys:
- query: user query identifier
- variant: either "gen"/"generative" or "base"/"baseline"/"organic"
- text: extracted visible text from the result page

Optional fields (used for diagnostics): url, user_id, timestamp.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


RUS_STOPWORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то",
    "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за",
    "бы", "по", "только", "ее", "мне", "было", "вот", "от", "меня", "еще", "нет",
    "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг", "ли", "если", "уже",
    "или", "ни", "быть", "был", "него", "до", "вас", "нибудь", "опять", "уж", "вам",
    "ведь", "там", "потом", "себя", "ничего", "ей", "может", "они", "тут", "где",
    "есть", "надо", "ней", "для", "мы", "тебя", "их", "чем", "была", "сам", "чтоб",
    "без", "будто", "чего", "раз", "тоже", "себе", "под", "будет", "ж", "тогда", "кто",
    "этот", "того", "потому", "этого", "какой", "совсем", "ним", "здесь", "этом", "один",
    "почти", "мой", "тем", "чтобы", "нее", "сейчас", "были", "куда", "зачем", "всех",
    "можно", "при", "наконец", "два", "об", "другой", "хоть", "после", "над", "больше",
    "тот", "через", "эти", "нас", "про", "всего", "них", "какая", "много", "разве",
    "три", "эту", "моя", "впрочем", "хорошо", "свою", "этой", "перед", "иногда", "лучше",
    "чуть", "том", "нельзя", "такой", "им", "более", "всегда", "конечно", "всю", "между",
}

TOKEN_PATTERN = re.compile(r"[a-zA-Zа-яА-ЯёЁ]{3,}")


@dataclass
class SerpRecord:
    query: str
    variant: str
    text: str


def normalize_variant(raw: str) -> str:
    lowered = raw.strip().lower()
    if lowered in {"gen", "generative", "llm", "ai", "gpt"}:
        return "generative"
    if lowered in {"base", "baseline", "organic", "classic", "no_gen", "non_gen"}:
        return "baseline"
    raise ValueError(f"Unknown variant '{raw}'. Use known aliases for generative/baseline")


def tokenize(text: str) -> str:
    words = [w.lower() for w in TOKEN_PATTERN.findall(text)]
    return " ".join(w for w in words if w not in RUS_STOPWORDS)


def load_records(path: Path) -> List[SerpRecord]:
    if path.suffix.lower() == ".jsonl":
        data = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    elif path.suffix.lower() == ".csv":
        import csv

        with path.open("r", encoding="utf-8", newline="") as fh:
            data = list(csv.DictReader(fh))
    else:
        raise ValueError("Supported formats: .csv or .jsonl")

    records: List[SerpRecord] = []
    for row in data:
        query = str(row.get("query", "")).strip()
        variant = str(row.get("variant", "")).strip()
        text = str(row.get("text", "")).strip()
        if not (query and variant and text):
            continue
        records.append(SerpRecord(query=query, variant=normalize_variant(variant), text=text))
    return records


def js_divergence(p: Iterable[float], q: Iterable[float]) -> float:
    p_list = list(p)
    q_list = list(q)
    m = [(a + b) / 2 for a, b in zip(p_list, q_list)]

    def kl(a: List[float], b: List[float]) -> float:
        eps = 1e-12
        s = 0.0
        for ai, bi in zip(a, b):
            ai = max(ai, eps)
            bi = max(bi, eps)
            s += ai * math.log(ai / bi, 2)
        return s

    return (kl(p_list, m) + kl(q_list, m)) / 2


def compare_topics(records: List[SerpRecord], n_topics: int, top_words: int) -> str:
    try:
        from sklearn.decomposition import LatentDirichletAllocation
        from sklearn.feature_extraction.text import CountVectorizer
    except ImportError as exc:
        raise RuntimeError(
            "scikit-learn is required. Install dependencies from requirements.txt first."
        ) from exc

    if len(records) < n_topics * 2:
        raise ValueError("Not enough documents for selected number of topics")

    corpus = [tokenize(r.text) for r in records]
    vectorizer = CountVectorizer(min_df=2, max_df=0.9)
    matrix = vectorizer.fit_transform(corpus)

    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42,
        learning_method="batch",
        max_iter=30,
    )
    doc_topic = lda.fit_transform(matrix)

    gen_idx = [i for i, r in enumerate(records) if r.variant == "generative"]
    base_idx = [i for i, r in enumerate(records) if r.variant == "baseline"]
    if not gen_idx or not base_idx:
        raise ValueError("Both groups must be present: generative and baseline")

    gen_mean = doc_topic[gen_idx].mean(axis=0)
    base_mean = doc_topic[base_idx].mean(axis=0)
    divergence = js_divergence(gen_mean.tolist(), base_mean.tolist())

    feature_names = vectorizer.get_feature_names_out()
    lines = [
        "# Topic modeling comparison",
        "",
        f"Documents total: {len(records)}",
        f"Generative docs: {len(gen_idx)}",
        f"Baseline docs: {len(base_idx)}",
        f"Topics: {n_topics}",
        f"Jensen-Shannon divergence: {divergence:.4f}",
        "",
        "## Top terms by topic",
    ]

    for topic_id, weights in enumerate(lda.components_):
        top_idx = weights.argsort()[::-1][:top_words]
        terms = ", ".join(feature_names[i] for i in top_idx)
        lines.append(f"- Topic {topic_id + 1}: {terms}")

    lines.extend(["", "## Mean topic share by group"])
    for i, (g, b) in enumerate(zip(gen_mean, base_mean), start=1):
        lines.append(f"- Topic {i}: generative={g:.4f}, baseline={b:.4f}, diff={g - b:+.4f}")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Path to CSV or JSONL with query/variant/text fields")
    parser.add_argument("--topics", type=int, default=8, help="Number of LDA topics")
    parser.add_argument("--top-words", type=int, default=10, help="Top words per topic in report")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("topic_comparison_report.md"),
        help="Output markdown report path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = load_records(args.input)
    report = compare_topics(records, n_topics=args.topics, top_words=args.top_words)
    args.output.write_text(report, encoding="utf-8")
    print(f"Done. Report saved to {args.output}")


if __name__ == "__main__":
    main()
