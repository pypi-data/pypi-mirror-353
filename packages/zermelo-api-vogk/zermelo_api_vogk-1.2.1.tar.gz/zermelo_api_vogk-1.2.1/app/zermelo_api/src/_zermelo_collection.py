from dataclasses import dataclass
from ._zermelo_api import zermelo
import inspect
import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def from_zermelo_dict(cls, data: dict, *args, **kwargs):
    [
        logger.debug(f"{k} ({v}) not defined in {cls}")
        for k, v in data.items()
        if k not in inspect.signature(cls).parameters
    ]
    return cls(
        *args,
        **{k: v for k, v in data.items() if k in inspect.signature(cls).parameters},
        **kwargs,
    )


@dataclass
class ZermeloCollection[T](list[T]):
    def __post_init__(self):
        self.type = None
        self.query = ""

    def __repr__(self):
        return ", ".join([f"{item!r}" for item in self])

    def print_list(self):
        return (
            f" = [" + ", ".join([str(item) for item in self]) + "]" if len(self) else ""
        )

    async def get_collection(self, query: str = "") -> list[dict]:
        query = self.get_query(query)
        logger.debug(f"type: {self.type}")
        return await zermelo.load_query(query)

    async def load_collection(self, query: str, *args, **kwargs):
        for row in await self.get_collection(query):
            self.append(from_zermelo_dict(self.type, row, *args, **kwargs))

    def get_query(self, query: str) -> str:
        if not query:
            if not self.query:
                raise Exception(f"No query given")
            return self.query
        return query

    async def _init(self, query: str = ""):
        if not self.type:
            raise Exception(f"No Type set for {self}")
        query = self.get_query(query)
        await self.load_collection(query)
