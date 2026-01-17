"""
Database Connection Management
PostgreSQL connection handling with async support
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from config import settings

logger = logging.getLogger(__name__)

# Database engine
engine = None
SessionLocal = None

async def init_database():
    """Initialize database connection and create tables"""
    global engine, SessionLocal
    
    try:
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
            echo=settings.DEBUG,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Create session factory
        SessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Test connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        logger.info("✅ Database connection established")
        
        # Create tables
        await create_tables()
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def create_tables():
    """Create database tables"""
    try:
        from database.models import Base
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database tables created/verified")
        
    except Exception as e:
        logger.error(f"❌ Table creation failed: {e}")
        raise

async def close_database():
    """Close database connections"""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("✅ Database connections closed")

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session context manager"""
    if not SessionLocal:
        raise RuntimeError("Database not initialized")
    
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def get_db():
    """Dependency for FastAPI routes"""
    async with get_db_session() as session:
        yield session