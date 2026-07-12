from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class NewsItem:

    id: int
    title: str
    content: str
    published_date: str
    created_by: Optional[str]
    attachment_path: Optional[str]

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            title=data.get("title") or data.get("news_title") or "",
            content=data.get("content") or data.get("news_description") or "",
            published_date=data.get("published_date") or data.get("created_on") or "",
            created_by=data.get("created_by") or data.get("addby"),
            attachment_path=data.get("attachment_path") or data.get("file_path")
        )

    def __str__(self):
        return f"{self.title} ({self.published_date})"
