from datetime import datetime
from math import floor, log
from math import pow as pw
from typing import Any

from .categories import (
    get_categories,
    get_category_id,
    get_category_ids,
    get_category_name,
)
from .models import Torrent


def format_size(size_bytes: int | None) -> str:
    """Converts a size in bytes to a human-readable string."""
    if size_bytes is None:
        return "N/A"
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(floor(log(size_bytes, 1024)))
    p = pw(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def format_date(date_str: str) -> str:
    """Converts a date string to a human-readable string."""
    return datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M:%S")


def format_torrent(torrent: dict[str, Any], torrent_id: int | None = None) -> Torrent:
    """Converts a torrent dictionary to a human-readable string."""
    cat_id = torrent.get("category_id")
    return Torrent(
        id=torrent_id or torrent.get("id"),
        title=torrent.get("title"),
        category=get_category_name(cat_id) or cat_id,
        size=format_size(torrent.get("size")),
        seeders=torrent.get("seeders"),
        leechers=torrent.get("leechers"),
        downloads=torrent.get("downloads") or "N/A",
        uploaded_at=format_date(torrent.get("uploaded_at")),
        magnet_link=None,
    )


def check_categories(categories: list[int | str]) -> list[int]:
    """Checks if the categories are valid."""
    processed_category_ids: list[int] = []
    if categories:
        if all(isinstance(cat, int) for cat in categories):
            processed_category_ids = categories
        elif all(isinstance(cat, str) for cat in categories):
            for keyword_val in categories:
                cat_id = get_category_id(str(keyword_val).lower())
                if cat_id is not None:
                    if cat_id not in processed_category_ids:
                        processed_category_ids.append(cat_id)
            if not processed_category_ids and categories:
                print(
                    f"Warning: None of the provided category keywords matched: {categories}."
                    " Proceeding without category filter."
                )
        else:
            raise TypeError(
                "The 'categories' parameter must be a list of"
                f" category IDs {get_category_ids()}"
                f" or keywords {get_categories()}."
            )
    return processed_category_ids
