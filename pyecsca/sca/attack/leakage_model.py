import abc
import sys
from typing import Literal, ClassVar

from numpy.random import default_rng
from public import public

if sys.version_info[0] < 3 or sys.version_info[0] == 3 and sys.version_info[1] < 10:
    def hw(i):
        return bin(i).count("1")
else:
    def hw(i):
        return i.bit_count()


@public
class NormalNoice:
    """
    https://www.youtube.com/watch?v=SAfq55aiqPc
    """

    def __init__(self, mean: float, sdev: float):
        self.rng = default_rng()
        self.mean = mean
        self.sdev = sdev

    def __call__(self, *args, **kwargs) -> float:
        return args[0] + self.rng.normal(self.mean, self.sdev)


@public
class LeakageModel(abc.ABC):
    num_args: ClassVar[int]

    @abc.abstractmethod
    def __call__(self, *args, **kwargs) -> int:
        raise NotImplementedError


@public
class Identity(LeakageModel):
    num_args = 1

    def __call__(self, *args, **kwargs) -> int:
        return int(args[0])


@public
class Bit(LeakageModel):
    num_args = 1

    def __init__(self, which: int):
        if which < 0:
            raise ValueError("which must be >= 0.")
        self.which = which
        self.mask = 1 << which

    def __call__(self, *args, **kwargs) -> Literal[0, 1]:
        return (int(args[0]) & self.mask) >> self.which  # type: ignore


@public
class Slice(LeakageModel):
    num_args = 1

    def __init__(self, begin: int, end: int):
        if begin > end:
            raise ValueError("begin must be <= than end.")
        self.begin = begin
        self.end = end
        self.mask = 0
        for i in range(begin, end):
            self.mask |= 1 << i

    def __call__(self, *args, **kwargs) -> int:
        return (int(args[0]) & self.mask) >> self.begin


@public
class HammingWeight(LeakageModel):
    num_args = 1

    def __call__(self, *args, **kwargs) -> int:
        return hw(int(args[0]))


@public
class HammingDistance(LeakageModel):
    num_args = 2

    def __call__(self, *args, **kwargs) -> int:
        return hw(int(args[0]) ^ int(args[1]))


@public
class BitLength(LeakageModel):
    num_args = 1

    def __call__(self, *args, **kwargs) -> int:
        return int(args[0]).bit_length()