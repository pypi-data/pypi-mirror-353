import asyncio

from ed_infrastructure.persistence.sqlalchemy.db_engine import DbConfig
from ed_infrastructure.persistence.sqlalchemy.unit_of_work import UnitOfWork


async def main():
    db_config = DbConfig(
        {
            "db": "easy_drop",
            "user": "postgres",
            "password": "df,oT2d)7ZGGcCMa",
            "host": "34.86.43.9",
        }
    )

    uow = UnitOfWork(db_config)

    async with uow.transaction():
        users = await uow.auth_user_repository.get_all()
        print("USERS", users)

        for user in users:
            print(user)


asyncio.run(main())
