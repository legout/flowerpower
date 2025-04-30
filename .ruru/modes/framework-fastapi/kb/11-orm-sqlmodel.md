# 11. ORM Integration (SQLModel)

## Core Concept

While FastAPI doesn't include a built-in ORM, it integrates seamlessly with various Python ORMs. **SQLModel**, created by the same author as FastAPI, is a popular choice because it combines Pydantic models (for validation and serialization) with SQLAlchemy Core/ORM (for database interaction) using standard Python type hints.

-   **Single Source of Truth:** Define your data structure once using a SQLModel class, and it serves as both your Pydantic model (for API validation/serialization) and your SQLAlchemy table model (for database operations).
-   **Async Support:** SQLModel works well with asynchronous database drivers (like `asyncpg` for PostgreSQL) and FastAPI's `async def` path operations.
-   **Type Safety:** Leverages Python type hints for better editor support and reduced errors.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install sqlmodel sqlalchemy "asyncpg" # Or other async driver like "aiomysql"
    # Also ensure FastAPI and Uvicorn are installed
    pip install fastapi uvicorn[standard]
    ```
2.  **Database Connection (Async SQLAlchemy):** Create an async SQLAlchemy engine (e.g., in `database.py`).
    ```python
    # database.py (example)
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlmodel import SQLModel # Import SQLModel base class
    import os

    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://user:password@host:port/db") # Load from env vars!

    engine = create_async_engine(DATABASE_URL, echo=True, future=True) # echo=True for logging SQL

    # Async session factory
    AsyncSessionLocal = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    # Function to create all tables (run once, e.g., in startup event or via Alembic)
    async def create_db_and_tables():
        async with engine.begin() as conn:
            # await conn.run_sync(SQLModel.metadata.drop_all) # Use drop_all carefully
            await conn.run_sync(SQLModel.metadata.create_all)
    ```
3.  **Define SQLModel Models:** Create classes inheriting from `SQLModel` and `table=True` (e.g., in `models.py`). Use type hints for fields. Define relationships using `Relationship`.
    ```python
    # models.py (example)
    from typing import List, Optional
    from sqlmodel import Field, Relationship, SQLModel

    class HeroTeamLink(SQLModel, table=True): # Association table for Many-to-Many
        team_id: Optional[int] = Field(default=None, foreign_key="team.id", primary_key=True)
        hero_id: Optional[int] = Field(default=None, foreign_key="hero.id", primary_key=True)

    class Team(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str = Field(index=True)
        headquarters: str

        heroes: List["Hero"] = Relationship(back_populates="teams", link_model=HeroTeamLink)

    class Hero(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str = Field(index=True)
        secret_name: str
        age: Optional[int] = Field(default=None, index=True)

        teams: List[Team] = Relationship(back_populates="heroes", link_model=HeroTeamLink)
    ```
4.  **Define Pydantic Schemas (Optional but Recommended):** Define separate Pydantic schemas (`BaseModel`) for API input (`Create`, `Update`) and output (`Read`) to decouple the API contract from the database model (e.g., in `schemas.py`). SQLModel classes can inherit from these Pydantic schemas.
    ```python
    # schemas.py (example)
    from pydantic import BaseModel
    from typing import Optional, List

    # --- Pydantic Schemas ---
    class HeroBase(BaseModel):
        name: str
        secret_name: str
        age: Optional[int] = None

    class HeroCreate(HeroBase): pass
    class HeroRead(HeroBase): id: int

    class TeamBase(BaseModel):
        name: str
        headquarters: str

    class TeamCreate(TeamBase): pass
    class TeamRead(TeamBase): id: int

    # Schemas including relationships for response
    class HeroReadWithTeams(HeroRead): teams: List[TeamRead] = []
    class TeamReadWithHeroes(TeamRead): heroes: List[HeroRead] = []

    # --- Update SQLModel Models to inherit ---
    # models.py (continued)
    # from .schemas import HeroBase, TeamBase # Import Pydantic schemas

    # class Team(TeamBase, SQLModel, table=True): # Inherit from TeamBase AND SQLModel
    #     id: Optional[int] = Field(default=None, primary_key=True)
    #     heroes: List["Hero"] = Relationship(back_populates="teams", link_model=HeroTeamLink)

    # class Hero(HeroBase, SQLModel, table=True): # Inherit from HeroBase AND SQLModel
    #     id: Optional[int] = Field(default=None, primary_key=True)
    #     teams: List[Team] = Relationship(back_populates="heroes", link_model=HeroTeamLink)
    ```
5.  **Dependency for DB Session:** Create an async dependency function using `yield` to provide and manage database sessions (e.g., in `dependencies.py`).
    ```python
    # dependencies.py (example)
    from typing import AsyncGenerator, Annotated
    from fastapi import Depends
    from sqlmodel.ext.asyncio.session import AsyncSession
    from .database import AsyncSessionLocal # Import async session factory

    async def get_session() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit() # Commit transaction if no exceptions
            except Exception:
                await session.rollback() # Rollback on error
                raise
            finally:
                await session.close() # Close session

    SessionDep = Annotated[AsyncSession, Depends(get_session)]
    ```

## CRUD Operations in Path Operations

Use the injected async session (`db: SessionDep`) and SQLModel/SQLAlchemy methods within `async def` path operations. Define CRUD logic in separate functions (e.g., `crud.py`) for better organization.

```python
# crud.py (example CRUD functions)
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from . import models, schemas # Assuming models and schemas exist

async def create_hero(session: AsyncSession, hero: schemas.HeroCreate) -> models.Hero:
    # Create SQLModel instance from Pydantic schema
    # Pydantic V2: db_hero = models.Hero.model_validate(hero)
    # Pydantic V1: db_hero = models.Hero.from_orm(hero)
    db_hero = models.Hero.model_validate(hero)
    session.add(db_hero)
    # await session.commit() # Commit handled by dependency
    await session.refresh(db_hero)
    return db_hero

async def get_hero(session: AsyncSession, hero_id: int) -> models.Hero | None:
    # Use select() for querying
    statement = select(models.Hero).where(models.Hero.id == hero_id)
    result = await session.exec(statement)
    return result.first() # Use .first(), .all(), .one(), .one_or_none()

# main.py or routers/heroes.py (example path operations)
from fastapi import FastAPI, HTTPException, status
from .dependencies import SessionDep
from . import crud, schemas, models

app = FastAPI() # Add lifespan for table creation if needed

@app.post("/heroes/", response_model=schemas.HeroRead, status_code=status.HTTP_201_CREATED)
async def create_new_hero(hero: schemas.HeroCreate, db: SessionDep):
    # Check if hero exists etc. (omitted for brevity)
    return await crud.create_hero(session=db, hero=hero)

@app.get("/heroes/{hero_id}", response_model=schemas.HeroReadWithTeams) # Response includes teams
async def read_single_hero(hero_id: int, db: SessionDep):
    # Use options for eager loading relationships if needed
    # statement = select(models.Hero).options(selectinload(models.Hero.teams)).where(models.Hero.id == hero_id)
    # result = await db.exec(statement)
    # db_hero = result.first()
    db_hero = await crud.get_hero(session=db, hero_id=hero_id) # Simple load
    if db_hero is None:
        raise HTTPException(status_code=404, detail="Hero not found")
    # SQLModel instance automatically serialized via Pydantic response_model
    # Ensure HeroReadWithTeams has orm_mode=True / from_attributes=True in its Config/model_config
    return db_hero
```

SQLModel provides a modern, type-safe way to interact with databases in FastAPI, especially well-suited for async applications. Remember to handle database sessions correctly using dependencies with `yield`.