
from typing import List, Dict, Union, Callable
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from typing import Union

class FunctionType(IntEnum):
    gt = 0
    visualizer = 1
    input = 2
    metric = 3
    loss = 4
    model_input = 5
    model_output = 6

@dataclass(frozen=True)
class TLFunction:
    FuncType: FunctionType
    FuncName: str

MappingList = List[Dict[TLFunction, Dict[str, Union[Callable, int]]]]

def leap_input(idx):
    def dummy():
        return None
    dummy.tl_func = TLFunction(FunctionType.model_input, idx)
    return dummy

def leap_output(idx):
    def dummy():
        return None
    dummy.tl_func = TLFunction(FunctionType.model_output, idx)
    return dummy

