from __future__ import annotations

import asyncio
import json
import logging

from aio_pika import connect_robust, ExchangeType
from aio_pika.abc import AbstractIncomingMessage
from tenacity import retry, stop_after_attempt, wait_exponential

from .models import SignalMessage, PositionMessage
from .persistence.postgres_repository import PostgresRepository

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "vicus.events"
SIGNALS_QUEUE = "ingest.signals"
POSITIONS_QUEUE = "ingest.positions"


class IngestConsumer:
    def __init__(self, rabbitmq_url: str, repository: PostgresRepository) -> None:
        self._url = rabbitmq_url
        self._repo = repository

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    async def start(self) -> None:
        logger.info("Connecting to RabbitMQ…")
        connection = await connect_robust(self._url)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=20)

        exchange = await channel.declare_exchange(
            EXCHANGE_NAME, ExchangeType.TOPIC, durable=True
        )

        signals_queue = await channel.declare_queue(SIGNALS_QUEUE, durable=True)
        await signals_queue.bind(exchange, routing_key="signal.#")

        positions_queue = await channel.declare_queue(POSITIONS_QUEUE, durable=True)
        await positions_queue.bind(exchange, routing_key="position.#")

        await signals_queue.consume(self._handle_signal)
        await positions_queue.consume(self._handle_position)

        logger.info(
            f"IngestBot listening | exchange={EXCHANGE_NAME} "
            f"queues={SIGNALS_QUEUE},{POSITIONS_QUEUE}"
        )
        await asyncio.Future()  # run forever

    async def _handle_signal(self, message: AbstractIncomingMessage) -> None:
        async with message.process(requeue_on_error=True):
            try:
                payload = json.loads(message.body)
                signal = SignalMessage.model_validate(payload)
                await self._repo.upsert_signal(signal)
                logger.debug(f"Signal ingested | id={signal.signal_id} status={signal.status}")
            except Exception as exc:
                logger.error(f"Signal ingest failed | error={exc!r} body={message.body[:200]}")
                raise

    async def _handle_position(self, message: AbstractIncomingMessage) -> None:
        async with message.process(requeue_on_error=True):
            try:
                payload = json.loads(message.body)
                position = PositionMessage.model_validate(payload)
                await self._repo.upsert_position(position)
                logger.debug(f"Position ingested | id={position.position_id} status={position.status}")
            except Exception as exc:
                logger.error(f"Position ingest failed | error={exc!r} body={message.body[:200]}")
                raise
