import inspect
from types import FunctionType
from typing import *

__all__ = ["slotdata"]


def getinit(keys: list) -> FunctionType:
    "This function returns __init__ for the class."

    def __init__(self: Self, **kwargs: Any) -> None:
        "This magic method initializes self."
        self._data = dict()
        k: Any
        v: Any
        for k, v in kwargs.items():
            setattr(self, k, v)
        for k in keys:
            getattr(self, k)

    return __init__


def getfdel(name: str, *, default: Any) -> FunctionType:
    def fdel(self: Self) -> Any:
        "This function is the deleter of the property."
        self._data[name] = default

    return fdel


def getfget(name: str) -> FunctionType:
    def fget(self: Self) -> Any:
        "This function is the getter of the property."
        return self._data[name]

    return fget


def getfset(name: str, *, func: FunctionType) -> FunctionType:
    def fset(self: Self, value: Any) -> Any:
        "This function is the setter of the property."
        self._data[name] = func(value)

    return fset


def getproperty(
    *,
    default: Any,
    defaultdict: dict,
    func: FunctionType,
    name: str,
):
    "This function creates and returns a new property."
    p: property
    try:
        defaultdict[name] = func(default)
    except:
        p = getpropertywithoutdefault(func=func, name=name)
    else:
        p = getpropertywithdefault(
            func=func,
            name=name,
            default=defaultdict[name],
        )
    return p


def getpropertywithdefault(
    *,
    default: Any,
    func: FunctionType,
    name: str,
):
    "This function creates and returns a new property."
    fdel: FunctionType = getfdel(name, default=default)
    fget: FunctionType = getfget(name)
    fset: FunctionType = getfset(name, func=func)
    ans: property = property(doc=func.__doc__, fdel=fdel, fget=fget, fset=fset)
    return ans


def getpropertywithoutdefault(
    *,
    func: FunctionType,
    name: str,
):
    "This function creates and returns a new property."
    fget: FunctionType = getfget(name)
    fset: FunctionType = getfset(name, func=func)
    ans: property = property(doc=func.__doc__, fget=fget, fset=fset)
    return ans


def gettodict(keys: list) -> FunctionType:
    def todict(self: Self) -> dict[str, Any]:
        "This method returns a dict representing the current instance."
        return dict(self._data)

    return todict


def slotdata(cls: type, *, default: Any = None) -> type:
    keys: list = list()
    defaultdict: dict = dict()
    k: Any
    v: Any
    p: property
    for k, v in cls.__dict__.items():
        if not inspect.isfunction(v):
            continue
        keys.append(k)
        p = getproperty(
            default=default,
            defaultdict=defaultdict,
            func=v,
            name=k,
        )
        setattr(cls, k, p)
    cls.__init__ = getinit(keys)
    cls.__slots__ = ("_data",)
    cls.todict = gettodict(keys)
