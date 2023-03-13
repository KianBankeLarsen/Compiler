from dataclasses import dataclass


@dataclass
class Labels:
    count: int = -1

    def next(self, s: str) -> str:
        self.count += 1
        return "custom" + str(self.count) + "_" + s
