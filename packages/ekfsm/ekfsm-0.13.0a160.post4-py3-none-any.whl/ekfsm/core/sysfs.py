from pathlib import Path

SYSFS_ROOT = Path("/sys")


def sysfs_root() -> Path:
    return SYSFS_ROOT


def set_sysfs_root(path: Path) -> None:
    global SYSFS_ROOT
    SYSFS_ROOT = path


def file_is_sysfs_attr(path: Path) -> bool:
    return path.is_file() and not path.stat().st_mode & 0o111


class SysFSAttribute:
    """
    A SysFSAttribute is a singular sysfs attribute located somewhere in */sys*.

    Attributes
    ----------
    path : Path
        path to the underlying file for the SysFSAttribute instance
    name : str
        attribute name, or the last part of self.path

    Methods
    -------
    read() -> Optional[str]
        Reads the file attribute if it exists
    write(data: Union[str, int]) -> None
        Writes data to the file attribute

    """

    def __init__(self, path: Path):
        self.path = path
        if not path.exists() or not path.is_file():
            raise FileNotFoundError("Invalid sysfs attribute path")

        self.name: str = path.name

    def read_utf8(self) -> str:
        return self.path.read_text()

    def read_bytes(self) -> bytes:
        return self.path.read_bytes()

    def write(self, data: str | bytes | None, offset: int = 0) -> None:
        if self.is_sysfs_attr() and data is not None:
            mode = 'r+' if isinstance(data, str) else 'rb+'
            with open(self.path, mode) as f:
                f.seek(offset)
                f.write(data)

    def is_sysfs_attr(self) -> bool:
        return file_is_sysfs_attr(self.path)

    def __repr__(self):
        return f"SysFSAttribute: {self.name}"


def list_sysfs_attributes(path: Path) -> list[SysFSAttribute]:
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Invalid sysfs directory: {path}")

    return [SysFSAttribute(item) for item in path.iterdir() if file_is_sysfs_attr(item)]


class SysFSDevice:
    def __init__(self, base_dir: Path):
        self.path: Path = base_dir
        self.attributes: list[SysFSAttribute] = list_sysfs_attributes(self.path)

    def pre(self) -> None:
        pass

    def post(self) -> None:
        pass

    def write_attr(self, attr: str, data: str | bytes, offset: int = 0) -> None:
        next(x for x in self.attributes if x.name == attr).write(data, offset)

    def read_attr_utf8(self, attr: str) -> str:
        return next(x for x in self.attributes if x.name == attr).read_utf8()

    def read_attr_bytes(self, attr: str) -> bytes:
        return next(x for x in self.attributes if x.name == attr).read_bytes()
