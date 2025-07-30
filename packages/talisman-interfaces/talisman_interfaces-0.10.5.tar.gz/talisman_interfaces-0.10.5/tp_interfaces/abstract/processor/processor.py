import asyncio
from abc import ABCMeta
from functools import partial
from typing import AsyncIterator, Protocol, Sequence, Tuple, Type, TypeVar, runtime_checkable

from tdm import TalismanDocument

from tp_interfaces.abstract.model import AsyncModel
from tp_interfaces.abstract.schema import ImmutableBaseModel
from tp_interfaces.logging.context import with_log_extras
from tp_interfaces.serializable import Serializable

_Config = TypeVar('_Config', bound=ImmutableBaseModel)


@runtime_checkable
class AbstractDocumentProcessor(AsyncModel, Protocol[_Config]):

    async def process_doc(self, document: TalismanDocument, config: _Config) -> TalismanDocument:
        pass

    async def process_docs(self, documents: Sequence[TalismanDocument], config: _Config) -> Tuple[TalismanDocument, ...]:
        log_extras = with_log_extras(doc_id=lambda kwargs: kwargs['document'].id)
        return tuple(await asyncio.gather(*map(partial(log_extras(self.process_doc), config=config), documents)))

    async def process_stream(
            self,
            documents: AsyncIterator[TalismanDocument],
            config: _Config,
            batch_size: int,
            concurrency: int = 1,
            results_queue_max_size: int = 0
    ) -> AsyncIterator[TalismanDocument]:
        """
        Asynchronously processes a stream of documents in batches and yields results as they become available.

        This method consumes an asynchronous stream of `TalismanDocument` objects, groups them into batches of the specified size,
        and processes the batches concurrently using `process_docs` method. Results are streamed back as they are processed.

        Notes:
        - Output order is **not guaranteed** to match input order due to concurrent batch processing.
        - Exceptions during processing are skipped silently.
        - Processing begins immediately and continues as input documents are streamed in.

        :param documents: asynchronous stream of input documents
        :param config: configuration object for processing (same for all document batches)
        :param batch_size: number of documents per batch
        :param concurrency: number of concurrent workers. Defaults to 1
        :param results_queue_max_size: maximum size of the results queue. Defaults to 0 (unbounded)
        :return: asynchronous iterator over processed documents
        """

        batches_queue: asyncio.Queue[Sequence[TalismanDocument]] = asyncio.Queue(maxsize=concurrency)
        results_queue: asyncio.Queue[TalismanDocument | Exception | None] = asyncio.Queue(maxsize=results_queue_max_size)

        async def batcher():
            batch = []
            async for doc in documents:
                batch.append(doc)
                if len(batch) >= batch_size:
                    await batches_queue.put(tuple(batch))
                    batch = []
            if batch:
                await batches_queue.put(tuple(batch))

        async def worker():
            while True:
                batch = await batches_queue.get()
                try:
                    result = await self.process_docs(batch, config)
                    for doc in result:
                        await results_queue.put(doc)
                except Exception as e:
                    await results_queue.put(e)
                finally:
                    batches_queue.task_done()  # mark batch processed after adding results in queue

        batcher_task = asyncio.create_task(batcher())
        worker_tasks = [asyncio.create_task(worker()) for _ in range(concurrency)]

        async def finalizer():
            await batcher_task  # no more batches will be added to batches queue
            await batches_queue.join()  # all added tasks are processed
            for worker_task in worker_tasks:
                worker_task.cancel()  # interrupt workers (they are blocked with input_queue.get method)
            await asyncio.gather(*worker_tasks, return_exceptions=True)  # all workers now awaited
            await results_queue.put(None)  # end of results signal

        asyncio.create_task(finalizer())

        while True:
            result = await results_queue.get()
            if result is None:
                break
            if isinstance(result, Exception):
                continue  # TODO: add logging
            yield result

    @property
    def config_type(self) -> Type[_Config]:
        raise NotImplementedError


class AbstractSerializableDocumentProcessor(AbstractDocumentProcessor, Serializable, metaclass=ABCMeta):
    pass
