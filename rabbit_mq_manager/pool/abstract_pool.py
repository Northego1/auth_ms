from abc import ABC, abstractmethod
from typing import Self


class AbstractPool(ABC):
    @abstractmethod
    async def add(self: Self, name: str, **kwargs):
        '''Add to pool'''


    @abstractmethod
    def get(self: Self, name: str):
        '''Get from pool'''