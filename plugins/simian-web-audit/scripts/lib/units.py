"""Number formatting for Spanish client copy."""


def _es(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def mb_from_kib(kib: float) -> str:
    return f"{_es(kib / 1024)} MB"


def seconds(ms: float) -> str:
    return f"{_es(ms / 1000)} s"
