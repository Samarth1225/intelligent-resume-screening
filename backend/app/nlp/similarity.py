"""
Semantic similarity engine — deliberately behind a small interface so the
implementation can be swapped later (per spec section 2 & 22: "Keep the
architecture modular so the AI/NLP component can later be replaced with an
LLM API if required").

Default implementation: TF-IDF vectorization + cosine similarity
(scikit-learn), computed fully offline with no model download. This was
chosen over `sentence-transformers` for this MVP because downloading
pretrained transformer weights requires outbound access to the Hugging Face
Hub, which is unavailable in locked-down / offline deployment environments —
exactly the "cannot be implemented reliably" case the spec calls out. TF-IDF
still rewards resumes that use related vocabulary to the job description
(e.g. shared domain terms), just without deep contextual embeddings.

To upgrade later: implement `SimilarityEngine` with a `SentenceTransformer`
(or an LLM embeddings API call) and swap the `get_similarity_engine()`
factory below — nothing else in the codebase needs to change.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimilarityEngine(ABC):
    @abstractmethod
    def score(self, text_a: str, text_b: str) -> float:
        """Return a 0-1 similarity score between two pieces of text."""
        raise NotImplementedError


class TfidfSimilarityEngine(SimilarityEngine):
    """Lightweight, fully-local semantic similarity via TF-IDF + cosine sim."""

    def score(self, text_a: str, text_b: str) -> float:
        text_a = (text_a or "").strip()
        text_b = (text_b or "").strip()
        if not text_a or not text_b:
            return 0.0
        try:
            vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
            matrix = vectorizer.fit_transform([text_a, text_b])
            if matrix.shape[1] == 0:
                return 0.0
            sim = cosine_similarity(matrix[0], matrix[1])[0][0]
            return float(max(0.0, min(1.0, sim)))
        except ValueError:
            # e.g. both texts are pure stop-words -> empty vocabulary
            return 0.0


_ENGINE: SimilarityEngine | None = None


def get_similarity_engine() -> SimilarityEngine:
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = TfidfSimilarityEngine()
    return _ENGINE
