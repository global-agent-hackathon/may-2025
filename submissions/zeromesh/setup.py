"""
ZeroMesh setup configuration
"""
from setuptools import setup, find_packages

setup(
    name="zeromesh",
    version="0.1.0",
    description="A zero-trust security layer for agent communication",
    author="ZeroMesh Team",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.2",
        "python-jose[cryptography]>=3.3.0",
        "python-multipart>=0.0.5",
        "python-dotenv>=0.19.0",
        "PyJWT>=2.3.0",
        "cryptography>=37.0.0",
        "passlib>=1.7.4",
        "bcrypt>=3.2.0",
        "networkx>=2.6.3",
        "matplotlib>=3.4.3",
        "sqlalchemy>=1.4.23",
        "alembic>=1.7.3",
        "aiosqlite>=0.17.0",
        "aiohttp>=3.8.1",
        "asyncio>=3.4.3",
        "websockets>=10.1",
        "structlog>=21.1.0",
        "prometheus-client>=0.11.0"
    ],
    python_requires=">=3.7",
) 