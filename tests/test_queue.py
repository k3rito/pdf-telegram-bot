from __future__ import annotations

import unittest

from services.queue.base import QueueTask
from services.queue.memory_queue import MemoryQueueBackend


class QueueTests(unittest.IsolatedAsyncioTestCase):
    async def test_memory_queue_enqueue_and_reserve(self) -> None:
        backend = MemoryQueueBackend()
        await backend.start()
        task = QueueTask(
            id="task-1",
            user_id=1,
            chat_id=1,
            chat_type="private",
            reply_to_message_id=None,
            service="merge",
            file_paths=["/tmp/a.pdf"],
            params={},
            temp_dir="/tmp/task-1",
        )
        await backend.enqueue(task)
        lease = await backend.reserve(timeout=0.1)
        self.assertIsNotNone(lease)
        assert lease is not None
        self.assertEqual(lease.task.id, "task-1")
        await backend.ack("task-1")


if __name__ == "__main__":
    unittest.main()
