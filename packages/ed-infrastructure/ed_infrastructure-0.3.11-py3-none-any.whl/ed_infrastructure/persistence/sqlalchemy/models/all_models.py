from datetime import datetime
from uuid import UUID

from ed_domain.core.aggregate_roots.delivery_job import DeliveryJobStatus
from ed_domain.core.aggregate_roots.order import OrderStatus
from ed_domain.core.aggregate_roots.waypoint import (WaypointStatus,
                                                     WaypointType)
from ed_domain.core.entities.bill import BillStatus
from ed_domain.core.entities.notification import NotificationType
from ed_domain.core.entities.otp import OtpType
from ed_domain.core.entities.parcel import ParcelSize
from sqlalchemy import (Boolean, DateTime, Double, Enum, Float, ForeignKey,
                        Integer, String, Uuid)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ed_infrastructure.persistence.sqlalchemy.models.base_model import \
    BaseModel


class AuthUserModel(BaseModel):
    __tablename__ = "auth_user"

    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String)
    verified: Mapped[bool] = mapped_column(Boolean)
    logged_in: Mapped[bool] = mapped_column(Boolean)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    # One-to-many: AuthUser has many Notifications
    notifications: Mapped[list["NotificationModel"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    # One-to-many: AuthUser has many Otps
    otps: Mapped[list["OtpModel"]] = relationship(
        back_populates="user", lazy="selectin"
    )


class AdminModel(BaseModel):
    __tablename__ = "admin"

    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("auth_user.id"), nullable=False
    )
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    # Many-to-one: Admin belongs to one AuthUser
    user: Mapped[AuthUserModel] = relationship(
        "AuthUserModel", uselist=False, lazy="joined"
    )


class BillModel(BaseModel):
    __tablename__ = "bill"

    amount_in_birr: Mapped[float] = mapped_column(Double, nullable=False)
    bill_status: Mapped[BillStatus] = mapped_column(
        Enum(BillStatus), nullable=False)
    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    # Relationship
    order_id: Mapped[UUID] = mapped_column(ForeignKey("order.id"))
    # Many-to-one: Bill belongs to one Order
    order: Mapped["OrderModel"] = relationship(
        "OrderModel", uselist=False, back_populates="bill", lazy="joined"
    )


class BusinessModel(BaseModel):
    __tablename__ = "business"

    business_name: Mapped[str] = mapped_column(String, nullable=False)
    owner_first_name: Mapped[str] = mapped_column(String, nullable=False)
    owner_last_name: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    user_id: Mapped[UUID] = mapped_column(ForeignKey("auth_user.id"))
    # Many-to-one: Business belongs to one AuthUser
    user: Mapped["AuthUserModel"] = relationship(
        "AuthUserModel", uselist=False, lazy="joined"
    )

    location_id: Mapped[UUID] = mapped_column(ForeignKey("location.id"))
    # Many-to-one: Business has one Location
    location: Mapped["LocationModel"] = relationship(
        "LocationModel", uselist=False, lazy="joined"
    )

    # One-to-many: Business has many Orders
    orders: Mapped[list["OrderModel"]] = relationship(
        "OrderModel", back_populates="business", lazy="selectin"
    )


class CarModel(BaseModel):
    __tablename__ = "car"

    make: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    registration_number: Mapped[str] = mapped_column(String, nullable=False)
    license_plate_number: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, nullable=False)
    seats: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    driver_id: Mapped[UUID] = mapped_column(ForeignKey("driver.id"))
    # Many-to-one: Car belongs to one Driver (assuming a driver has only one car)
    driver: Mapped["DriverModel"] = relationship(
        "DriverModel", uselist=False, back_populates="car", lazy="joined"
    )


class ConsumerModel(BaseModel):
    __tablename__ = "consumer"

    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("auth_user.id"), nullable=False
    )
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    profile_image_url: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    location_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("location.id"), nullable=False
    )

    # Relationships
    # Many-to-one: Consumer belongs to one AuthUser
    user: Mapped["AuthUserModel"] = relationship(
        "AuthUserModel", uselist=False, lazy="joined"
    )
    # Many-to-one: Consumer has one Location
    location: Mapped["LocationModel"] = relationship(
        "LocationModel", uselist=False, lazy="joined"
    )
    # One-to-many: Consumer has many Orders
    orders: Mapped[list["OrderModel"]] = relationship(
        "OrderModel", back_populates="consumer", lazy="selectin"
    )


class DeliveryJobModel(BaseModel):
    __tablename__ = "delivery_job"

    estimated_payment_in_birr: Mapped[float] = mapped_column(
        Float, nullable=False)
    estimated_completion_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    estimated_distance_in_kms: Mapped[float] = mapped_column(
        Double, nullable=False)
    estimated_time_in_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False)
    status: Mapped[DeliveryJobStatus] = mapped_column(
        String(50), nullable=False)

    # Relationships
    driver_id: Mapped[UUID] = mapped_column(ForeignKey("driver.id"))
    # Many-to-one: DeliveryJob belongs to one Driver
    driver: Mapped["DriverModel"] = relationship(
        uselist=False, back_populates="delivery_jobs", lazy="joined"
    )
    # One-to-many: DeliveryJob has many Waypoints
    waypoints: Mapped[list["WaypointModel"]] = relationship(
        back_populates="delivery_job", lazy="selectin"
    )


class DriverModel(BaseModel):
    __tablename__ = "driver"

    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    profile_image: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    email: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    user_id: Mapped[UUID] = mapped_column(ForeignKey("auth_user.id"))
    # Many-to-one: Driver belongs to one AuthUser
    user: Mapped["AuthUserModel"] = relationship(
        "AuthUserModel", uselist=False, lazy="joined"
    )

    current_location_id: Mapped[UUID] = mapped_column(
        ForeignKey("location.id"))
    # Many-to-one: Driver has one current Location
    current_location: Mapped["LocationModel"] = relationship(
        "LocationModel", uselist=False, lazy="joined"
    )
    # One-to-one: Driver has one Car
    car: Mapped["CarModel"] = relationship(
        "CarModel", uselist=False, back_populates="driver", lazy="joined"
    )
    # One-to-many: Driver has many Orders
    orders: Mapped[list["OrderModel"]] = relationship(
        "OrderModel", back_populates="driver", lazy="selectin"
    )
    # One-to-many: Driver has many DeliveryJobs
    delivery_jobs: Mapped[list["DeliveryJobModel"]] = relationship(
        "DeliveryJobModel", back_populates="driver", lazy="selectin"
    )


class LocationModel(BaseModel):
    __tablename__ = "location"

    address: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    postal_code: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)
    last_used: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )


class NotificationModel(BaseModel):
    __tablename__ = "notification"

    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("auth_user.id"), nullable=False
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType), nullable=False
    )
    message: Mapped[str] = mapped_column(String, nullable=False)
    read_status: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Relationships
    # Many-to-one: Notification belongs to one AuthUser
    user: Mapped["AuthUserModel"] = relationship(
        "AuthUserModel", uselist=False, back_populates="notifications", lazy="joined"
    )


class OrderModel(BaseModel):
    __tablename__ = "order"

    latest_time_of_delivery: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    order_status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), nullable=False)

    # Relationships
    business_id: Mapped[UUID] = mapped_column(ForeignKey("business.id"))
    # Many-to-one: Order belongs to one Business
    business: Mapped["BusinessModel"] = relationship(
        "BusinessModel", uselist=False, back_populates="orders", lazy="joined"
    )
    consumer_id: Mapped[UUID] = mapped_column(ForeignKey("consumer.id"))
    # Many-to-one: Order belongs to one Consumer
    consumer: Mapped["ConsumerModel"] = relationship(
        "ConsumerModel", uselist=False, back_populates="orders", lazy="joined"
    )
    # One-to-one: Order has one Bill
    bill: Mapped["BillModel"] = relationship(
        "BillModel", uselist=False, back_populates="order", lazy="joined"
    )
    # One-to-one: Order has one Parcel
    parcel: Mapped["ParcelModel"] = relationship(
        "ParcelModel", uselist=False, back_populates="order", lazy="joined"
    )
    driver_id: Mapped[UUID] = mapped_column(ForeignKey("driver.id"))
    # Many-to-one: Order belongs to one Driver
    driver: Mapped["DriverModel"] = relationship(
        "DriverModel",
        uselist=False,
        back_populates="orders",
        lazy="joined",  # Added back_populates to driver
    )


class OtpModel(BaseModel):
    __tablename__ = "otp"

    otp_type: Mapped[OtpType] = mapped_column(Enum(OtpType), nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)
    expiry_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationship
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("auth_user.id"))
    # Many-to-one: Otp belongs to one AuthUser
    user: Mapped["AuthUserModel"] = relationship(  # Added this relationship
        "AuthUserModel", uselist=False, back_populates="otps", lazy="joined"
    )


class ParcelModel(BaseModel):
    __tablename__ = "parcel"

    size: Mapped[ParcelSize] = mapped_column(Enum(ParcelSize), nullable=False)
    length: Mapped[float] = mapped_column(Float, nullable=False)
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    fragile: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Relationship
    order_id: Mapped[UUID] = mapped_column(ForeignKey("order.id"))
    # Many-to-one: Parcel belongs to one Order
    order: Mapped["OrderModel"] = relationship(
        "OrderModel", uselist=False, back_populates="parcel", lazy="joined"
    )


class WaypointModel(BaseModel):
    __tablename__ = "waypoint"

    eta: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[WaypointType] = mapped_column(
        Enum(WaypointType), nullable=False)
    waypoint_status: Mapped[WaypointStatus] = mapped_column(
        Enum(WaypointStatus), nullable=False
    )

    # Relationships
    order_id: Mapped[UUID] = mapped_column(ForeignKey("order.id"))
    # Many-to-one: Waypoint belongs to one Order
    order: Mapped["OrderModel"] = relationship(
        "OrderModel", uselist=False, lazy="joined"
    )

    delivery_job_id: Mapped[UUID] = mapped_column(
        ForeignKey("delivery_job.id"))
    # Many-to-one: Waypoint belongs to one DeliveryJob
    delivery_job: Mapped["DeliveryJobModel"] = relationship(
        "DeliveryJobModel", uselist=False, back_populates="waypoints", lazy="joined"
    )
