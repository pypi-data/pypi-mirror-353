from datetime import UTC, datetime, timedelta
from uuid import UUID

from ed_domain.common.exceptions import (EXCEPTION_NAMES, ApplicationException,
                                         Exceptions)
from ed_domain.core.aggregate_roots import Business, Consumer, Order, Waypoint
from ed_domain.core.entities import Otp
from ed_domain.core.entities.notification import NotificationType
from ed_domain.core.entities.otp import OtpType
from ed_domain.persistence.async_repositories import ABCAsyncUnitOfWork
from ed_domain.utils.otp import ABCOtpGenerator
from ed_notification.application.features.notification.dtos import \
    NotificationDto
from ed_notification.documentation.api.notification_api_client import \
    ABCNotificationApiClient

from ed_core.application.contracts.infrastructure.api.abc_api import ABCApi
from ed_core.application.features.common.dtos.create_consumer_dto import \
    CreateConsumerDto
from ed_core.common.generic_helpers import get_new_id


async def create_otp(
    user_id: UUID, otp_type: OtpType, uow: ABCAsyncUnitOfWork, otp: ABCOtpGenerator
) -> str:
    new_otp = otp.generate()
    await uow.otp_repository.create(
        Otp(
            id=get_new_id(),
            user_id=user_id,
            value=new_otp,
            otp_type=otp_type,
            expiry_datetime=datetime.now(UTC) + timedelta(minutes=5),
            create_datetime=datetime.now(UTC),
            update_datetime=datetime.now(UTC),
            deleted=False,
            deleted_datetime=None,
        )
    )

    return new_otp


async def send_notification(
    user_id: UUID,
    message: str,
    notification_api: ABCNotificationApiClient,
    error_message: str,
) -> NotificationDto:
    notification_response = await notification_api.send_notification(
        {
            "user_id": user_id,
            "notification_type": NotificationType.EMAIL,
            "message": message,
        }
    )

    if not notification_response["is_success"]:
        raise ApplicationException(
            Exceptions.InternalServerException,
            error_message,
            [
                f"Failed to send notification to user with id {user_id}.",
                notification_response["message"],
            ],
        )

    return notification_response["data"]


async def get_order(
    order_id: UUID,
    uow: ABCAsyncUnitOfWork,
    error_message: str,
) -> Order:
    order = await uow.order_repository.get(id=order_id)
    if not order:
        raise ApplicationException(
            Exceptions.NotFoundException,
            error_message,
            [f"Order with id {order_id} not found."],
        )

    return order


async def get_business(
    business_id: UUID,
    uow: ABCAsyncUnitOfWork,
    error_message: str,
) -> Business:
    business = await uow.business_repository.get(id=business_id)
    if not business:
        raise ApplicationException(
            Exceptions.NotFoundException,
            error_message,
            [f"Business with id {business_id} not found."],
        )

    return business


async def get_consumer(
    consumer_id: UUID,
    uow: ABCAsyncUnitOfWork,
    error_message: str,
) -> Consumer:
    consumer = await uow.consumer_repository.get(id=consumer_id)
    if not consumer:
        raise ApplicationException(
            Exceptions.NotFoundException,
            error_message,
            [f"Consumer with id {consumer_id} not found."],
        )

    return consumer


async def get_order_waypoint(
    delivery_job_id: UUID,
    order_id: UUID,
    uow: ABCAsyncUnitOfWork,
    error_message: str,
) -> Waypoint:
    waypoint = await uow.waypoint_repository.get(
        order_id=order_id, delivery_job_id=delivery_job_id
    )

    if waypoint is None:
        raise ApplicationException(
            Exceptions.BadRequestException,
            error_message,
            [f"Order with id {order_id} is not in the delivery job waypoints."],
        )

    return waypoint


async def create_or_get_consumer(
    consumer: CreateConsumerDto, uow: ABCAsyncUnitOfWork, api: ABCApi
) -> Consumer:
    if existing_consumer := await uow.consumer_repository.get(
        phone_number=consumer.phone_number
    ):
        return existing_consumer

    create_user_response = await api.auth_api.create_get_otp(
        {
            "first_name": consumer.first_name,
            "last_name": consumer.last_name,
            "phone_number": consumer.phone_number,
            "email": consumer.email,
        }
    )

    if not create_user_response["is_success"]:
        raise ApplicationException(
            EXCEPTION_NAMES[create_user_response["http_status_code"]],
            "Failed to create orders",
            ["Could not create consumers."],
        )

    user_id = create_user_response["data"]["id"]
    return await consumer.create_consumer(uow, user_id)
