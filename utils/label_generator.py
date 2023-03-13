from dataclasses import dataclass


@dataclass
class Labels:
    """Label generator to ensure uniqueness.
    """

    count: int = -1

    def next(self, s: str) -> str:
        """Outputs unique label with descriptive string `s` as postfix.
        """

        self.count += 1
        return "custom" + str(self.count) + "_" + s
