from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewsItem:
    source_name: str
    title: str
    url: str
    published_at: datetime  # timezone-aware, UTC
    snippet: str = ""

    @property
    def key(self) -> str:
        return f"{self.source_name}::{self.url}"
