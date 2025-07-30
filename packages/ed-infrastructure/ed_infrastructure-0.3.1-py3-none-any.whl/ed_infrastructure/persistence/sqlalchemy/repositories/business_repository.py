from ed_domain.core.aggregate_roots.business import Business
from ed_domain.persistence.async_repositories.abc_async_business_repository import \
    ABCAsyncBusinessRepository

from ed_infrastructure.persistence.sqlalchemy.models import BusinessModel
from ed_infrastructure.persistence.sqlalchemy.repositories.generic_repository import \
    AsyncGenericRepository


class BusinessRepository(
    ABCAsyncBusinessRepository, AsyncGenericRepository[Business, BusinessModel]
):
    def __init__(self) -> None:
        super().__init__(BusinessModel)

    @classmethod
    def _to_entity(cls, model: BusinessModel) -> Business:
        return Business(
            id=model.id,
            user_id=model.user.id,
            business_name=model.business_name,
            owner_first_name=model.owner_first_name,
            owner_last_name=model.owner_last_name,
            phone_number=model.phone_number,
            email=model.email,
            location_id=model.location.id,
            create_datetime=model.create_datetime,
            update_datetime=model.update_datetime,
            deleted=model.deleted,
            deleted_datetime=model.deleted_datetime,
        )

    @classmethod
    def _to_model(cls, entity: Business) -> BusinessModel:
        return BusinessModel(
            id=entity.id,
            user_id=entity.user_id,
            business_name=entity.business_name,
            owner_first_name=entity.owner_first_name,
            owner_last_name=entity.owner_last_name,
            phone_number=entity.phone_number,
            email=entity.email,
            location_id=entity.location_id,
            create_datetime=entity.create_datetime,
            update_datetime=entity.update_datetime,
            deleted=entity.deleted,
            deleted_datetime=entity.deleted_datetime,
        )
