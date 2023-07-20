from datetime import date

from pydantic import BaseModel, PositiveFloat, PositiveInt, validator


class InsuranceRateBase(BaseModel):
    cargo_type: str
    rate: PositiveFloat


class InsuranceRateCreate(InsuranceRateBase):
    date: date


class InsuranceRateUpdate(InsuranceRateBase):
    pass


class InsuranceRateInDB(InsuranceRateBase):
    id: PositiveInt
    date: date

    class Config:
        orm_mode = True


class InsuranceRate(InsuranceRateInDB):
    pass


class RatesByDate(BaseModel):
    __root__: dict[date, list[InsuranceRateBase]]


class PriceResponse(BaseModel):
    price: PositiveFloat

    @validator("price")
    def round_price(cls, value):
        return round(value, 2)


class SuccessResponseMessage(BaseModel):
    message: str
