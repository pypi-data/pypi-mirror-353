from abc import ABC, abstractmethod
from typing import Optional

from doteval.sessions import Session

__all__ = ["Storage"]


class Storage(ABC):
    """Abstract storage interface"""

    @abstractmethod
    def save(self, session: Session):
        pass

    @abstractmethod
    def load(self, name: str) -> Optional[Session]:
        pass

    @abstractmethod
    def list_names(self) -> list[str]:
        pass

    @abstractmethod
    def rename(self, old_name: str, new_name: str):
        pass

    @abstractmethod
    def delete(self, name: str):
        pass

    @abstractmethod
    def acquire_lock(self, name: str):
        pass

    @abstractmethod
    def release_lock(self, name: str):
        pass

    @abstractmethod
    def is_locked(self, name: str) -> bool:
        pass
