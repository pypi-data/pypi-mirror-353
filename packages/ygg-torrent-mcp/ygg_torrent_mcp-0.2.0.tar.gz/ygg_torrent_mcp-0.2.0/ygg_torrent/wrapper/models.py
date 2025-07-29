from pydantic import BaseModel


class Torrent(BaseModel):
    id: int
    title: str
    category: str
    size: str
    seeders: int
    leechers: int
    downloads: int | str
    uploaded_at: str
    magnet_link: str | None
