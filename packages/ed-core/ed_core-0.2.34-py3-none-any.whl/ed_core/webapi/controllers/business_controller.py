from typing import Annotated
from uuid import UUID

from ed_domain.common.logging import get_logger
from fastapi import APIRouter, Depends
from rmediator.mediator import Mediator

from ed_core.application.features.business.dtos import (CreateBusinessDto,
                                                        CreateOrderDto,
                                                        UpdateBusinessDto)
from ed_core.application.features.business.requests.commands import (
    CreateBusinessCommand, CreateOrderCommand, UpdateBusinessCommand)
from ed_core.application.features.business.requests.queries import (
    GetAllBusinessQuery, GetBusinessByUserIdQuery, GetBusinessOrdersQuery,
    GetBusinessQuery)
from ed_core.application.features.common.dtos import BusinessDto, OrderDto
from ed_core.webapi.common.helpers import GenericResponse, rest_endpoint
from ed_core.webapi.dependency_setup import mediator

LOG = get_logger()
router = APIRouter(prefix="/businesses", tags=["Business Feature"])


@router.post("/", response_model=GenericResponse[BusinessDto])
@rest_endpoint
async def create_business(
    request_dto: CreateBusinessDto,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    return await mediator.send(CreateBusinessCommand(dto=request_dto))


@router.get("/", response_model=GenericResponse[list[BusinessDto]])
@rest_endpoint
async def get_all_businesses(
    mediator: Annotated[Mediator, Depends(mediator)],
):
    return await mediator.send(GetAllBusinessQuery())


@router.put("/{business_id}", response_model=GenericResponse[BusinessDto])
@rest_endpoint
async def update_business(
    business_id: UUID,
    dto: UpdateBusinessDto,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    return await mediator.send(UpdateBusinessCommand(id=business_id, dto=dto))


@router.get("/{business_id}", response_model=GenericResponse[BusinessDto])
@rest_endpoint
async def get_business(
    business_id: UUID,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    return await mediator.send(GetBusinessQuery(business_id=business_id))


@router.get("/users/{user_id}", response_model=GenericResponse[BusinessDto])
@rest_endpoint
async def get_business_by_user_id(
    user_id: UUID,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    return await mediator.send(GetBusinessByUserIdQuery(user_id=user_id))


@router.get("/{business_id}/orders", response_model=GenericResponse[list[OrderDto]])
@rest_endpoint
async def get_business_orders(
    business_id: UUID,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    return await mediator.send(GetBusinessOrdersQuery(business_id=business_id))


@router.post("/{business_id}/orders", response_model=GenericResponse[OrderDto])
@rest_endpoint
async def create_order(
    business_id: UUID,
    request_dto: CreateOrderDto,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    LOG.info(f"Satisfying request {request_dto}")
    return await mediator.send(
        CreateOrderCommand(business_id=business_id, dto=request_dto)
    )
