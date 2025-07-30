from typing import Annotated

from ed_auth.documentation.api.auth_api_client import AuthApiClient
from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from ed_domain.utils.otp.abc_otp_generator import ABCOtpGenerator
from ed_infrastructure.persistence.sqlalchemy.unit_of_work import UnitOfWork
from ed_infrastructure.utils.otp.otp_generator import OtpGenerator
from ed_notification.documentation.api.notification_api_client import \
    NotificationApiClient
from fastapi import Depends
from rmediator.mediator import Mediator

from ed_core.application.contracts.infrastructure.abc_rabbitmq_producers import \
    ABCRabbitMQProducers
from ed_core.application.contracts.infrastructure.api.abc_api import ABCApi
from ed_core.application.features.business.handlers.commands import (
    CreateBusinessCommandHandler, CreateOrderCommandHandler,
    UpdateBusinessCommandHandler)
from ed_core.application.features.business.handlers.queries import (
    GetAllBusinessesQueryHandler, GetBusinessByUserIdQueryHandler,
    GetBusinessOrdersQueryHandler, GetBusinessQueryHandler)
from ed_core.application.features.business.requests.commands import (
    CreateBusinessCommand, CreateOrderCommand, UpdateBusinessCommand)
from ed_core.application.features.business.requests.queries import (
    GetAllBusinessQuery, GetBusinessByUserIdQuery, GetBusinessOrdersQuery,
    GetBusinessQuery)
from ed_core.application.features.consumer.handlers.commands import (
    CreateConsumerCommandHandler, UpdateConsumerCommandHandler)
from ed_core.application.features.consumer.handlers.queries import (
    GetConsumerByUserIdQueryHandler, GetConsumerOrdersQueryHandler,
    GetConsumerQueryHandler, GetConsumersQueryHandler)
from ed_core.application.features.consumer.requests.commands import (
    CreateConsumerCommand, UpdateConsumerCommand)
from ed_core.application.features.consumer.requests.queries import (
    GetConsumerByUserIdQuery, GetConsumerOrdersQuery, GetConsumerQuery,
    GetConsumersQuery)
from ed_core.application.features.delivery_job.handlers.commands import (
    CancelDeliveryJobCommandHandler, ClaimDeliveryJobCommandHandler,
    CreateDeliveryJobCommandHandler)
from ed_core.application.features.delivery_job.handlers.queries import (
    GetDeliveryJobQueryHandler, GetDeliveryJobsQueryHandler)
from ed_core.application.features.delivery_job.requests.commands import (
    CancelDeliveryJobCommand, ClaimDeliveryJobCommand,
    CreateDeliveryJobCommand)
from ed_core.application.features.delivery_job.requests.queries import (
    GetDeliveryJobQuery, GetDeliveryJobsQuery)
from ed_core.application.features.driver.handlers.commands import (
    CreateDriverCommandHandler, DropOffOrderCommandHandler,
    DropOffOrderVerifyCommandHandler, PickUpOrderCommandHandler,
    PickUpOrderVerifyCommandHandler, UpdateDriverCommandHandler,
    UpdateDriverCurrentLocationCommandHandler)
from ed_core.application.features.driver.handlers.queries import (
    GetAllDriversQueryHandler, GetDriverByUserIdQueryHandler,
    GetDriverDeliveryJobsQueryHandler, GetDriverOrdersQueryHandler,
    GetDriverPaymentSummaryQueryHandler, GetDriverQueryHandler)
from ed_core.application.features.driver.requests.commands import (
    CreateDriverCommand, DropOffOrderCommand, DropOffOrderVerifyCommand,
    PickUpOrderCommand, PickUpOrderVerifyCommand, UpdateDriverCommand,
    UpdateDriverCurrentLocationCommand)
from ed_core.application.features.driver.requests.queries import (
    GetAllDriversQuery, GetDriverByUserIdQuery, GetDriverDeliveryJobsQuery,
    GetDriverOrdersQuery, GetDriverPaymentSummaryQuery, GetDriverQuery)
from ed_core.application.features.notification.handlers.queries import \
    GetNotificationsQueryHandler
from ed_core.application.features.notification.requests.queries import \
    GetNotificationsQuery
from ed_core.application.features.order.handlers.commands import \
    CancelOrderCommandHandler
from ed_core.application.features.order.handlers.queries import (
    GetOrderQueryHandler, GetOrdersQueryHandler, TrackOrderQueryHandler)
from ed_core.application.features.order.requests.commands import \
    CancelOrderCommand
from ed_core.application.features.order.requests.queries import (
    GetOrderQuery, GetOrdersQuery, TrackOrderQuery)
from ed_core.common.generic_helpers import get_config
from ed_core.common.typing.config import Config, Environment
from ed_core.infrastructure.api.api_handler import ApiHandler
from ed_core.webapi.dependency_setup.message_queues import get_rabbitmq_handler


def get_otp_generator(
    config: Annotated[Config, Depends(get_config)],
) -> ABCOtpGenerator:
    return OtpGenerator(dev_mode=config["environment"] == Environment.DEV)


def get_api(config: Annotated[Config, Depends(get_config)]) -> ABCApi:
    return ApiHandler(
        AuthApiClient(config["auth_api"]),
        NotificationApiClient(config["notification_api"]),
    )


def get_uow(config: Annotated[Config, Depends(get_config)]) -> ABCAsyncUnitOfWork:
    return UnitOfWork(config["db"])


def mediator(
    uow: Annotated[ABCAsyncUnitOfWork, Depends(get_uow)],
    api: Annotated[ABCApi, Depends(get_api)],
    otp: Annotated[ABCOtpGenerator, Depends(get_otp_generator)],
    rabbitmq_handler: Annotated[ABCRabbitMQProducers, Depends(get_rabbitmq_handler)],
) -> Mediator:
    mediator = Mediator()

    handlers = [
        # Delivery job handler
        (CreateDeliveryJobCommand, CreateDeliveryJobCommandHandler(uow)),
        (ClaimDeliveryJobCommand, ClaimDeliveryJobCommandHandler(uow)),
        (GetDeliveryJobsQuery, GetDeliveryJobsQueryHandler(uow)),
        (GetDeliveryJobQuery, GetDeliveryJobQueryHandler(uow)),
        # Driver handlers
        (CreateDriverCommand, CreateDriverCommandHandler(uow)),
        (GetAllDriversQuery, GetAllDriversQueryHandler(uow)),
        (GetDriverOrdersQuery, GetDriverOrdersQueryHandler(uow)),
        (GetDriverDeliveryJobsQuery, GetDriverDeliveryJobsQueryHandler(uow)),
        (GetDriverQuery, GetDriverQueryHandler(uow)),
        (GetDriverByUserIdQuery, GetDriverByUserIdQueryHandler(uow)),
        (GetDriverPaymentSummaryQuery, GetDriverPaymentSummaryQueryHandler(uow)),
        (DropOffOrderCommand, DropOffOrderCommandHandler(uow, api, otp)),
        (DropOffOrderVerifyCommand, DropOffOrderVerifyCommandHandler(uow, api)),
        (PickUpOrderCommand, PickUpOrderCommandHandler(uow, api, otp)),
        (PickUpOrderVerifyCommand, PickUpOrderVerifyCommandHandler(uow, api)),
        (UpdateDriverCommand, UpdateDriverCommandHandler(uow)),
        (
            UpdateDriverCurrentLocationCommand,
            UpdateDriverCurrentLocationCommandHandler(uow),
        ),
        (CancelDeliveryJobCommand, CancelDeliveryJobCommandHandler(uow)),
        # Business handlers
        (CreateBusinessCommand, CreateBusinessCommandHandler(uow)),
        (CreateOrderCommand, CreateOrderCommandHandler(uow, api, rabbitmq_handler)),
        (GetBusinessQuery, GetBusinessQueryHandler(uow)),
        (GetBusinessByUserIdQuery, GetBusinessByUserIdQueryHandler(uow)),
        (GetBusinessOrdersQuery, GetBusinessOrdersQueryHandler(uow)),
        (GetAllBusinessQuery, GetAllBusinessesQueryHandler(uow)),
        (UpdateBusinessCommand, UpdateBusinessCommandHandler(uow)),
        (TrackOrderQuery, TrackOrderQueryHandler(uow)),
        # Order handlers
        (GetOrdersQuery, GetOrdersQueryHandler(uow)),
        (GetOrderQuery, GetOrderQueryHandler(uow)),
        (CancelOrderCommand, CancelOrderCommandHandler(uow)),
        # Consumer handlers
        (CreateConsumerCommand, CreateConsumerCommandHandler(uow)),
        (UpdateConsumerCommand, UpdateConsumerCommandHandler(uow)),
        (GetConsumersQuery, GetConsumersQueryHandler(uow)),
        (GetConsumerQuery, GetConsumerQueryHandler(uow)),
        (GetConsumerByUserIdQuery, GetConsumerByUserIdQueryHandler(uow)),
        (GetConsumerOrdersQuery, GetConsumerOrdersQueryHandler(uow)),
        # Notification handlers
        (GetNotificationsQuery, GetNotificationsQueryHandler(uow)),
    ]

    for command, handler in handlers:
        mediator.register_handler(command, handler)

    return mediator
