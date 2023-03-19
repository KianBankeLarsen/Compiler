from dataclasses import dataclass

from singleton_decorator import singleton


@singleton
@dataclass
class Labels:
    """Singleton label generator to ensure uniqueness.
    """

    count: int = -1

    def next(self, s: str) -> str:
        """Outputs unique label with descriptive string `s` as prefix.
        """

        self.count += 1
        return s + "_" + str(self.count)
