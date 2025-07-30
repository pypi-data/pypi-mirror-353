from collections import deque
import asyncio

class AsyncQueue:
    def __init__(self):
        self.queue = deque()
        self.lock = asyncio.Lock()

    async def enqueue(self, item):
        async with self.lock:
            self.queue.append(item)

    async def dequeue(self):
        async with self.lock:
            if self.queue:
                return self.queue.popleft()
            return None

    async def is_empty(self):
        async with self.lock:
            return len(self.queue) == 0

    async def size(self):
        async with self.lock:
            return len(self.queue)

    async def process_queue(self, process_function):
        while not await self.is_empty():
            item = await self.dequeue()
            if item is not None:
                await process_function(item)
