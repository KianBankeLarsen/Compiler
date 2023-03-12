from dataclasses import dataclass


@dataclass
class Labels:
    count: int = -1

    def next(self, s: str) -> str:
        return str(self.count := self.count + 1) + "_" + s
    