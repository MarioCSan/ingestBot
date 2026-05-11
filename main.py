#!/usr/bin/env python3
"""Vicus Analytics — Ingest Bot.

Consumes events from RabbitMQ exchange `vicus.events` and persists
signals and positions to PostgreSQL.

Required environment variables (see .env.example):
    RABBITMQ_URL   amqp://user:pass@host:5672/
    POSTGRES_DSN   postgresql://user:pass@host:5432/dbname
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

from src.consumer import IngestConsumer
from src.persistence.postgres_repository import PostgresRepository

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","src":"%(name)s","msg":%(message)s}',
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    stream=sys.stdout,
)
logger = logging.getLogger("ingestBot")


async def main() -> None:
    rabbitmq_url = os.environ["RABBITMQ_URL"]
    postgres_dsn = os.environ["POSTGRES_DSN"]

    logger.info('"IngestBot starting"')

    repo = PostgresRepository(postgres_dsn)
    await repo.initialize()

    consumer = IngestConsumer(rabbitmq_url, repo)
    try:
        await consumer.start()
    finally:
        await repo.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('"Shutdown requested"')
