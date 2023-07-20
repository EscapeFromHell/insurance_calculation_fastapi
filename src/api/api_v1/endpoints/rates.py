from datetime import date

from fastapi import APIRouter, Depends, Query, UploadFile
from pydantic import PositiveFloat

from src.core.repository import RateRepo
from src.core.schemas import PriceResponse, RatesByDate, SuccessResponseMessage
from src.deps import rate_repo as deps_rate_repo

router = APIRouter()


@router.post("/upload_json", status_code=201, response_model=SuccessResponseMessage)
async def upload_json_file(
    *, json_file: UploadFile, rate_repo: RateRepo = Depends(deps_rate_repo)
) -> SuccessResponseMessage:
    """
    Загрузка тарифов из JSON файла.

    :param json_file: UploadFile - Загружаемый JSON файл с тарифами.
    :param rate_repo: RateRepo - Репозиторий для работы с тарифами.
    :return: SuccessResponseMessage - Ответ об успешной загрузке.
    """
    return await rate_repo.upload_json_file(json_file=json_file)


@router.post("/upload_insurance_rates", status_code=201, response_model=SuccessResponseMessage)
async def upload_insurance_rates(
    *, obj_in: RatesByDate, rate_repo: RateRepo = Depends(deps_rate_repo)
) -> SuccessResponseMessage:
    """
    Загрузка тарифов из объекта (RatesByDate).

    :param obj_in: RatesByDate - Объект с датами, типами грузов и тарифами.
    :param rate_repo: RateRepo - Репозиторий для работы с тарифами.
    :return: SuccessResponseMessage - Ответ об успешной загрузке.
    """
    return await rate_repo.upload_insurance_rates(obj_in=obj_in)


@router.get("/get_price", status_code=200, response_model=PriceResponse)
async def get_price(
    *,
    date: date = Query(example=f"{date.today()}"),
    cargo_type: str = Query(example="Glass"),
    declared_value: PositiveFloat = Query(example=10000),
    rate_repo: RateRepo = Depends(deps_rate_repo),
) -> PriceResponse:
    """
    Получение стоимости страховки по дате, типу груза и объявленной стоимости.

    :param date: date - Дата, на которую требуется получить тариф.
    :param cargo_type: str - Тип груза, для которого нужен тариф.
    :param declared_value: PositiveFloat - Объявленная стоимость груза.
    :param rate_repo: RateRepo - Репозиторий для работы с тарифами.
    :return: PriceResponse - Ответ с информацией о стоимости страховки.
    """
    return await rate_repo.get_price(date=date, cargo_type=cargo_type, declared_value=declared_value)
