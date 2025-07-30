from datetime import UTC, datetime, timedelta
from uuid import UUID

from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.core.aggregate_roots import Consumer, DeliveryJob, Driver, Order
from ed_domain.core.aggregate_roots.order import OrderStatus
from ed_domain.core.aggregate_roots.waypoint import (Waypoint, WaypointStatus,
                                                     WaypointType)
from ed_domain.core.entities import Otp
from ed_domain.core.entities.notification import NotificationType
from ed_domain.core.entities.otp import OtpType
from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from ed_domain.utils.otp.abc_otp_generator import ABCOtpGenerator
from ed_notification.documentation.api.abc_notification_api_client import \
    NotificationDto
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.contracts.infrastructure.api.abc_api import ABCApi
from ed_core.application.features.driver.dtos import DropOffOrderDto
from ed_core.application.features.driver.requests.commands import \
    DropOffOrderCommand
from ed_core.common.generic_helpers import get_new_id


@request_handler(DropOffOrderCommand, BaseResponse[DropOffOrderDto])
class DropOffOrderCommandHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork, api: ABCApi, otp: ABCOtpGenerator):
        self._uow = uow
        self._api = api
        self._otp = otp

    async def handle(
        self, request: DropOffOrderCommand
    ) -> BaseResponse[DropOffOrderDto]:
        async with self._uow.transaction():
            delivery_job = await self._get_delivery_job(request.delivery_job_id)
            driver = await self._get_driver(request.driver_id, delivery_job)
            order = await self._get_order(request.order_id)

            waypoint_index = self._get_order_waypoint(
                order.id, delivery_job.waypoints)

            # Send otp to consumer
            consumer = await self._get_consumer(order.consumer.id)
            sms_otp = await self._otp.generate()
            await self._send_notification(
                consumer.user_id,
                f"Your OTP for delivery job {delivery_job.id} is {sms_otp}.",
            )

            # Update db
            order.update_status(OrderStatus.IN_PROGRESS)
            delivery_job.waypoints[waypoint_index][
                "waypoint_status"
            ] = WaypointStatus.IN_PROGRESS

            await self._uow.delivery_job_repository.update(
                delivery_job.id, delivery_job
            )
            await self._uow.otp_repository.create(
                Otp(
                    id=get_new_id(),
                    user_id=driver.user_id,
                    value=sms_otp,
                    otp_type=OtpType.DROP_OFF,
                    expiry_datetime=datetime.now(UTC) + timedelta(minutes=5),
                    create_datetime=datetime.now(UTC),
                    update_datetime=datetime.now(UTC),
                    deleted=False,
                    deleted_datetime=None,
                )
            )
            await self._uow.order_repository.update(order.id, order)

        return BaseResponse[DropOffOrderDto].success(
            "Delivery job verification OTP sent to consumer.",
            DropOffOrderDto(
                order_id=order.id, driver_id=driver.id, consumer_id=consumer.id
            ),
        )

    async def _send_notification(self, user_id: UUID, message: str) -> NotificationDto:
        notification_response = await self._api.notification_api.send_notification(
            {
                "user_id": user_id,
                "notification_type": NotificationType.SMS,
                "message": message,
            }
        )

        if not notification_response["is_success"]:
            raise ApplicationException(
                Exceptions.InternalServerException,
                "Delivery job not droped off.",
                [
                    f"Failed to send notification to consumer with id {user_id}.",
                    notification_response["message"],
                ],
            )

        return notification_response["data"]

    def _get_order_waypoint(self, order_id: UUID, waypoints: list[Waypoint]) -> int:
        for index, waypoint in enumerate(waypoints):
            if (
                waypoint.order.id == order_id
                and waypoint.waypoint_type == WaypointType.PICK_UP
            ):
                return index

        raise ApplicationException(
            Exceptions.BadRequestException,
            "Order not found in waypoints.",
            [f"Order with id {order_id} is not in the delivery job waypoints."],
        )

    async def _get_delivery_job(self, delivery_job_id: UUID) -> DeliveryJob:
        delivery_job = await self._uow.delivery_job_repository.get(id=delivery_job_id)
        if not delivery_job or delivery_job.driver is None:
            raise ApplicationException(
                Exceptions.NotFoundException,
                "Delivery job not found.",
                [f"Delivery job with id {delivery_job_id} not found."],
            )

        return delivery_job

    async def _get_driver(self, driver_id: UUID, delivery_job: DeliveryJob) -> Driver:
        driver = await self._uow.driver_repository.get(id=driver_id)
        if not driver:
            raise ApplicationException(
                Exceptions.NotFoundException,
                "Driver not found.",
                [f"Driver with id {driver_id} not found."],
            )

        if driver.id != delivery_job.driver_id:
            raise ApplicationException(
                Exceptions.BadRequestException,
                "Driver mismatch.",
                [
                    "Driver ID is different from the one registered for the delivery job."
                ],
            )

        return driver

    async def _get_order(self, order_id: UUID) -> Order:
        order = await self._uow.order_repository.get(id=order_id)
        if not order:
            raise ApplicationException(
                Exceptions.NotFoundException,
                "Order not found.",
                [f"Order with id {order_id} not found."],
            )

        return order

    async def _get_consumer(self, consumer_id: UUID) -> Consumer:
        consumer = await self._uow.consumer_repository.get(id=consumer_id)
        if not consumer:
            raise ApplicationException(
                Exceptions.NotFoundException,
                "Delivery job not droped off.",
                [f"Consumer with id {consumer_id} not found."],
            )

        return consumer
