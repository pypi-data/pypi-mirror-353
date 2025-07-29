from .hero_api_model import HeroApiModel


class HeroApiErrorModel(HeroApiModel):
    status_code: int
    stack_trace: str
