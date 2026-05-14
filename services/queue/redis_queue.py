from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import asdict
from time import time
from typing import Any

from services.queue.base import QueueBackend, QueueLease, QueueTask


class RedisQueueBackend(QueueBackend):
    name = "redis"

    def __init__(self, redis_url: str, key_prefix: str = "pdfbot:queue") -> None:
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self._redis = None
        self._scheduler_task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        try:
            import redis.asyncio as redis
        except Exception as exc:
            raise RuntimeError("redis.asyncio is not installed") from exc

        self._redis = redis.from_url(self.redis_url, decode_responses=True)
        self._stop_event.clear()
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())

    async def stop(self) -> None:
        self._stop_event.set()
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except Exception:
                pass
            self._scheduler_task = None
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None

    async def enqueue(self, task: QueueTask) -> str:
        redis = self._require_redis()
        payload = task.to_dict()
        payload["status"] = "pending"
        payload["updated_at"] = time()
        await redis.hset(self._task_key(task.id), mapping={"payload": json.dumps(payload, ensure_ascii=False)})
        if task.run_at > time():
            await redis.zadd(self._delayed_key, {task.id: task.run_at})
        else:
            await redis.lpush(self._ready_key(task.priority), task.id)
        return task.id

    async def reserve(self, timeout: float | None = None) -> QueueLease | None:
        redis = self._require_redis()
        wait = 0 if timeout is None else max(0, int(timeout))
        priority_keys = [self._ready_key(level) for level in range(9, -1, -1)]
        if not priority_keys:
            return None
        result = await redis.blpop(priority_keys, timeout=wait)
        if not result:
            return None
        _, task_id = result
        payload = await redis.hget(self._task_key(task_id), "payload")
        if not payload:
            return None
        task = QueueTask.from_dict(json.loads(payload))
        lease_token = uuid.uuid4().hex
        task = QueueTask.from_dict({**asdict(task), "correlation_id": task.correlation_id or lease_token})
        await redis.hset(self._task_key(task.id), mapping={"status": "reserved", "lease_token": lease_token, "updated_at": time()})
        return QueueLease(task=task, backend_name=self.name, lease_token=lease_token)

    async def ack(self, task_id: str) -> None:
        redis = self._require_redis()
        await redis.hset(self._task_key(task_id), mapping={"status": "success", "updated_at": time()})
        await redis.zrem(self._delayed_key, task_id)

    async def nack(self, task_id: str, delay_seconds: int = 0) -> None:
        redis = self._require_redis()
        payload = await redis.hget(self._task_key(task_id), "payload")
        if not payload:
            return
        task = QueueTask.from_dict(json.loads(payload))
        retries_left = max(0, task.retries_left - 1)
        task = QueueTask.from_dict({**asdict(task), "retries_left": retries_left, "run_at": time() + max(0, delay_seconds)})
        await redis.hset(self._task_key(task.id), mapping={"payload": json.dumps(asdict(task), ensure_ascii=False), "status": "delayed", "updated_at": time()})
        await redis.zadd(self._delayed_key, {task.id: task.run_at})

    async def cancel(self, task_id: str) -> bool:
        redis = self._require_redis()
        removed = await redis.zrem(self._delayed_key, task_id)
        await redis.hset(self._task_key(task_id), mapping={"status": "canceled", "updated_at": time()})
        return bool(removed)

    def qsize(self) -> int:
        return 0

    def snapshot(self) -> dict[str, int]:
        return {"pending": 0, "leased": 0, "delayed": 0, "canceled": 0}

    async def _scheduler_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                await self._promote_delayed()
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(2)

    async def _promote_delayed(self) -> None:
        redis = self._require_redis()
        now = time()
        task_ids = await redis.zrangebyscore(self._delayed_key, min="-inf", max=now)
        for task_id in task_ids:
            payload = await redis.hget(self._task_key(task_id), "payload")
            if not payload:
                continue
            task = QueueTask.from_dict(json.loads(payload))
            await redis.zrem(self._delayed_key, task_id)
            await redis.lpush(self._ready_key(task.priority), task.id)

    def _require_redis(self):
        if self._redis is None:
            raise RuntimeError("Redis queue is not started")
        return self._redis

    def _task_key(self, task_id: str) -> str:
        return f"{self.key_prefix}:task:{task_id}"

    def _ready_key(self, priority: int) -> str:
        return f"{self.key_prefix}:ready:{priority}"

    @property
    def _delayed_key(self) -> str:
        return f"{self.key_prefix}:delayed"
