import multiprocessing

from scaler.object_storage.object_storage_server import ObjectStorageServer
from scaler.utility.object_storage_config import ObjectStorageConfig


class ObjectStorageServerProcess(multiprocessing.get_context("fork").Process):  # type: ignore[misc]
    def __init__(self, storage_address: ObjectStorageConfig):
        multiprocessing.Process.__init__(self, name="ObjectStorageServer")
        self._object_storage_server = ObjectStorageServer(storage_address)

    def wait_until_ready(self) -> None:
        self._object_storage_server.wait_until_ready()

    def run(self) -> None:
        self._object_storage_server.run()
