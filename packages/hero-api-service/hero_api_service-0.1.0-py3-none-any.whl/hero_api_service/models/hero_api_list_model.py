from typing import Optional

from .hero_api_model import HeroApiModel


class HeroApiListModel(HeroApiModel):
    page: int
    size: int
    last_page: bool
    total: Optional[int] = None
