import json
import logging
from datetime import date

from fastapi import HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from pydantic import PositiveFloat
from tortoise.queryset import Q

from src.core.models import InsuranceRate
from src.core.repository.repository import Repository
from src.core.schemas import (
    InsuranceRateCreate,
    PriceResponse,
    RatesByDate,
    SuccessResponseMessage,
)
from src.utils import get_logger

logger = get_logger(__file__, logging.DEBUG)


class RateRepo(Repository):
    async def __prepare_data(self, loaded_data: dict) -> list[InsuranceRateCreate]:
        """
        Подготовка данных перед загрузкой в БД.

        :param loaded_data: dict - Словарь с данными о тарифах.
        :return: list[InsuranceRateCreate] - Список объектов InsuranceRateCreate.
        """
        data = []

        try:
            for date, rates in loaded_data.items():
                for rate in rates:
                    cargo_type = rate["cargo_type"]
                    rate_value = rate["rate"]
                    data.append(InsuranceRateCreate(cargo_type=cargo_type, rate=rate_value, date=date))

        except KeyError:
            raise HTTPException(status_code=422, detail="Unprocessable Entity")

        return data

    async def __check_insurance_rate(self, data: list[InsuranceRateCreate]) -> None:
        """
        Проверка тарифов перед загрузкой в БД. Если в БД уже есть тарифы с указаной датой и типом груза,
        данные тарифы будут удалены из БД как устаревшие.

        :param data: list[InsuranceRateCreate] - Список объектов InsuranceRateCreate.
        :return: None
        """
        filters = [Q(cargo_type=item.cargo_type, date=item.date) for item in data]
        combined_filter = filters[0]
        for filter in filters[1:]:
            combined_filter |= filter

        rate_objects = await InsuranceRate.filter(combined_filter)
        if rate_objects:
            for rate_object in rate_objects:
                await rate_object.delete()
            logger.info("Obsolete rates have been removed")

    async def __create_insurance_rates(self, data: list[InsuranceRateCreate]) -> None:
        """
        Добавление тарифов в БД.

        :param data: list[InsuranceRateCreate] - Список объектов InsuranceRateCreate.
        :return: None
        """
        insurance_rates = [InsuranceRate(cargo_type=item.cargo_type, rate=item.rate, date=item.date) for item in data]
        await InsuranceRate.bulk_create(insurance_rates)
        logger.info("New rates have been added")

    async def upload_json_file(self, json_file: UploadFile) -> SuccessResponseMessage:
        """
        Загрузка тарифов из JSON файла.

        :param json_file: UploadFile - Загружаемый JSON файл с тарифами.
        :return: SuccessResponseMessage - Ответ об успешной загрузке.
        """
        json_content = await json_file.read()
        loaded_data = json.loads(json_content)
        data = await self.__prepare_data(loaded_data=loaded_data)

        await self.__check_insurance_rate(data=data)
        await self.__create_insurance_rates(data=data)

        return SuccessResponseMessage(message="JSON file uploaded successfully")

    async def upload_insurance_rates(self, obj_in: RatesByDate) -> SuccessResponseMessage:
        """
        Загрузка тарифов из объекта (RatesByDate).

        :param obj_in: RatesByDate - Объект с датами, типами грузов и тарифами.
        :return: SuccessResponseMessage - Ответ об успешной загрузке.
        """
        loaded_data = jsonable_encoder(obj_in)
        data = await self.__prepare_data(loaded_data=loaded_data)

        await self.__check_insurance_rate(data=data)
        await self.__create_insurance_rates(data=data)

        return SuccessResponseMessage(message="Insurance rates uploaded successfully")

    async def get_price(self, date: date, cargo_type: str, declared_value: PositiveFloat) -> PriceResponse:
        """
        Получение стоимости страховки по дате, типу груза и объявленной стоимости.

        :param date: date - Дата, на которую требуется получить тариф.
        :param cargo_type: str - Тип груза, для которого нужен тариф.
        :param declared_value: PositiveFloat - Объявленная стоимость груза.
        :return: PriceResponse - Ответ с информацией о стоимости страховки.
        """
        insurance_rate = await InsuranceRate.filter(cargo_type=cargo_type, date__lte=date).order_by("-date").first()

        if not insurance_rate:
            raise HTTPException(status_code=404, detail="Rate not found")

        current_price = insurance_rate.rate * declared_value
        return PriceResponse(price=current_price)
