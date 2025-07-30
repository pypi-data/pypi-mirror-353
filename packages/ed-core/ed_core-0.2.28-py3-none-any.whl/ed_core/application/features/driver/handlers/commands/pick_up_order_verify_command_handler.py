from datetime import UTC, datetime
from uuid import UUID

from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.core.aggregate_roots import DeliveryJob, Driver, Order
from ed_domain.core.aggregate_roots.order import OrderStatus
from ed_domain.core.aggregate_roots.waypoint import (Waypoint, WaypointStatus,
                                                     WaypointType)
from ed_domain.core.entities.notification import NotificationType
from ed_domain.core.entities.otp import OtpType
from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.contracts.infrastructure.api.abc_api import ABCApi
from ed_core.application.features.driver.requests.commands import \
    PickUpOrderVerifyCommand


@request_handler(PickUpOrderVerifyCommand, BaseResponse[None])
class PickUpOrderVerifyCommandHandler(RequestHandler):
    def __init__(self, uow: ABCAsyncUnitOfWork, api: ABCApi):
        self._uow = uow
        self._api = api

    async def handle(self, request: PickUpOrderVerifyCommand) -> BaseResponse[None]:
        async with self._uow.transaction():
            # Get entities
            delivery_job = await self._validate_delivery_job(request.delivery_job_id)
            driver = await self._validate_driver(request.driver_id, delivery_job)
            order = await self._validate_order(request.order_id)

            # Validate otp
            await self._validate_otp(driver.user_id, request.dto.otp)

            # Update db
            waypoint_index = self._get_order_waypoint(
                order.id, delivery_job.waypoints)
            delivery_job.waypoints[waypoint_index][
                "waypoint_status"
            ] = WaypointStatus.DONE
            await self._uow.delivery_job_repository.update(
                delivery_job.id, delivery_job
            )
            order.update_status(OrderStatus.PICKED_UP)

            # Send notifications
            await self._api.notification_api.send_notification(
                {
                    "user_id": order.consumer.id,
                    "notification_type": NotificationType.IN_APP,
                    "message": f"Order {order.id} has been dropped off by driver {driver.id}.",
                }
            )

        return BaseResponse[None].success(
            "Delivery job dropped off successfully.",
            None,
        )

    def _get_order_waypoint(self, order_id: UUID, waypoints: list[Waypoint]) -> int:
        for index, waypoint in enumerate(waypoints):
            if (
                waypoint.order.id == order_id
                and waypoint.waypoint_type == WaypointType.DROP_OFF
            ):
                return index

        raise ApplicationException(
            Exceptions.BadRequestException,
            "Order not found in waypoints.",
            [f"Order with id {order_id} is not in the delivery job waypoints."],
        )

    async def _validate_delivery_job(self, delivery_job_id: UUID) -> DeliveryJob:
        delivery_job = await self._uow.delivery_job_repository.get(id=delivery_job_id)

        if not delivery_job or delivery_job.driver is None:
            raise ApplicationException(
                Exceptions.NotFoundException,
                "Delivery job not found.",
                [f"Delivery job with id {delivery_job_id} not found."],
            )
        return delivery_job

    async def _validate_driver(
        self, driver_id: UUID, delivery_job: DeliveryJob
    ) -> Driver:
        driver = await self._uow.driver_repository.get(id=driver_id)
        if driver is None:
            raise ApplicationException(
                Exceptions.NotFoundException,
                "Driver not found.",
                [f"Driver with id {driver_id} not found."],
            )

        assert delivery_job.driver is not None

        if driver.id != delivery_job.driver:
            raise ApplicationException(
                Exceptions.BadRequestException,
                "Driver mismatch.",
                [
                    "Driver ID is different from the one registered for the delivery job."
                ],
            )

        return driver

    async def _validate_otp(self, user_id: UUID, otp_value: str) -> None:
        otp = await self._uow.otp_repository.get(user_id=user_id)
        if not otp or otp.otp_type != OtpType.PICK_UP:
            raise ApplicationException(
                Exceptions.BadRequestException,
                "Invalid OTP.",
                ["OTP is not valid or has expired. Please request a new OTP."],
            )

        if otp.expiry_datetime < datetime.now(UTC):
            raise ApplicationException(
                Exceptions.BadRequestException,
                "Expired OTP.",
                ["OTP has expired. Please request a new OTP."],
            )

        if otp.value != otp_value:
            raise ApplicationException(
                Exceptions.BadRequestException,
                "Invalid OTP.",
                ["OTP is not valid. Please request a new OTP."],
            )

    async def _validate_order(self, order_id: UUID) -> Order:
        order = await self._uow.order_repository.get(id=order_id)
        if not order:
            raise ApplicationException(
                Exceptions.NotFoundException,
                "Order not found.",
                [f"Order with id {order_id} not found."],
            )

        return order
