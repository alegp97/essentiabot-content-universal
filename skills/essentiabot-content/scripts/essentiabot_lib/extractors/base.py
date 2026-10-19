from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractionResult:
    source_type: str
    url: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: str = ""

    def to_dict(self) -> dict:
        return {
            "source_type": self.source_type,
            "url": self.url,
            "text": self.text,
            "metadata": self.metadata,
            "success": self.success,
            "error_message": self.error_message,
        }


class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, url: str) -> dict:
        pass

    def _failure(self, url: str, source_type: str, error: str) -> dict:
        return ExtractionResult(
            source_type=source_type,
            url=url,
            text="",
            success=False,
            error_message=error,
        ).to_dict()
