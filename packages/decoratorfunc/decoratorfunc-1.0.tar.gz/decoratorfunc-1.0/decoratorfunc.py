from typing import Callable, TypeVar, Generic
from decoratorbasic import *

TCallable = TypeVar('TCallable', bound=Callable)
TDecorator = TypeVar('TDecorator', bound=Callable)

class DecoratorFuncBasic(DecoratorBasic[TCallable], Generic[TCallable]):
    def __call__(self, callable:TCallable) -> TCallable:
        self.__checker__(callable)
        if hasattr(self, 'definator_func'):
            definator = self.__definator__(callable, self.definator_func)
        else:
            definator = callable
        if hasattr(self, 'decorator_func'):
            decorator = self.__decorator__(definator, self.decorator_func)
        else:
            decorator = definator
        sing_with_decorator(callable=callable, decorator=decorator, base=self)
        return decorator
    
    def definator(self, func:Callable[[TCallable],TCallable]):
        self.definator_func = func
        return self

    def decorator(self, func:Callable[[TCallable],TCallable]):
        self.decorator_func = func
        return self


def definator(func:TDecorator) -> DecoratorFuncBasic:
    name = ''.join(map(lambda w: w.capitalize(),func.__name__.split('_')))
    return type(name, (DecoratorFuncBasic,), {
        'definator_func': lambda self, callable: func(callable)
    })()

def decorator(func:TDecorator) -> DecoratorFuncBasic:
    name = ''.join(map(lambda w: w.capitalize(),func.__name__.split('_')))
    return type(name, (DecoratorFuncBasic,), {
        'decorator_func': lambda self, callable, *args, **kwargs: func(
            callable, *args, **kwargs
        )
    })()

def is_decoratorfunc(base:DecoratorFuncBasic) -> bool:
    return isinstance(base, DecoratorFuncBasic)


__all__ = [
    'DecoratorFuncBasic',
    'definator',
    'decorator',
    'is_decoratorfunc'
]
