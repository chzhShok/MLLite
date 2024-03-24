from pydantic import BaseModel


class UserParams(BaseModel):
    region: str
    total_area: float
    kitchen_area: float
    living_area: float
    rooms_count: int
    floor: int
    floors_number: int
    isComplete: bool | None = None
    house_material: str
    balcony: bool | None = None
    passenger_elevator: bool | None = None
    is_apartments: bool | None = None
    is_auction: bool | None = None
    locate: str | None = None
    is_metro: bool | None = None
    m_minute: float | None = None
    m_type: str | None = None
