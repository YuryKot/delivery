class CreateCourierCommand:
    def __init__(self, name: str, speed: int) -> None:
        self._name = name
        self._speed = speed

    @property
    def name(self) -> str:
        return self._name

    @property
    def speed(self) -> int:
        return self._speed
