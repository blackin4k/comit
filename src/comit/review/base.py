from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from comit.commit.context import CommitContext
from comit.review.models import ReviewFinding


class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, context: CommitContext) -> List[ReviewFinding]:
        pass
