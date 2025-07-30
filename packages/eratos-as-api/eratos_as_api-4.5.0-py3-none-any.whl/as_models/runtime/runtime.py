
from abc import ABC, abstractmethod
import logging
import os


class ModelRuntime(ABC):
    def __init__(self, model_dir, manifest):
        self.model_dir = os.path.abspath(model_dir)
        self.manifest = manifest
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def is_valid(self):
        pass

    @abstractmethod
    def execute_model(self, job_request, args, updater):
        pass

    @property
    def entrypoint(self):
        return self.manifest.entrypoint

    @property
    def entrypoint_path(self):
        return os.path.join(self.model_dir, self.entrypoint)

    @property
    def manifest_path(self):
        return os.path.join(self.model_dir, 'manifest.json')
