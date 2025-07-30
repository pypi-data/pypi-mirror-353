from typing import Optional, TypeVar, Callable, Any, Generic, List
import functools

from callabletype import is_class, is_function, is_callable

__version__ = '1.0.1'

TCallable = TypeVar('TCallable', bound=Callable)
TDecorator = TypeVar('TDecorator', bound=Callable)

DECORATOR_KEY = '__decorator__'


class DecoratorContext(Generic[TCallable]):
    def __init__(self, callable:TCallable):
        self.callable = callable
        self.decorators:List[DecoratorBasic] = []

    def is_empty(self) -> bool:
        return not bool(self.decorators)


class DecoratorBasic(Generic[TCallable]):
    @classmethod
    def __checker__(cls, callable:TCallable):
        if not is_callable(callable): 
            raise TypeError("'{}' object is not callable.".format(callable))
    
    @classmethod
    def __decorator__(cls, callable:TCallable, decorator:TDecorator) -> TCallable:
        if is_class(callable):
            decorator_adapter = create_decorator_for_class
        elif is_function(callable):
            decorator_adapter = create_decorator_for_function
        else:
            raise TypeError(
                "'{}' object is neither a function nor a class.".format(callable)
            )
        return decorator_adapter(callable, decorator)
    
    @classmethod
    def __definator__(cls, callable:TCallable, definator:TDecorator) -> TCallable:
        definator_method = definator(callable)
        if definator_method is None:
            raise TypeError(
                "The definator method defined inside the decoratorbase named '{}' should return a callable value.".format(cls.__name__)
            )
        return definator_method

    def __call__(self, callable:TCallable) -> TCallable:
        self.__checker__(callable)          
        definator = self.__definator__(callable, self.definator)
        decorator = self.__decorator__(definator, self.decorator)
        sing_with_decorator(callable=callable, decorator=decorator, base=self)
        return decorator 

    def definator(self, callable:TCallable) -> TCallable:
        return callable
        
    def decorator(self, callable:TCallable, *args, **kwargs) -> Any:
        return callable(*args, **kwargs)


# Decorator Functions
def create_decorator_for_function(
    callable:TCallable, 
    decorator:TDecorator
) -> TCallable:
    @functools.wraps(callable)
    def wrapper(*args, **kwargs):
        result = decorator(callable, *args,**kwargs)
        if 'return' in callable.__annotations__:
            if callable.__annotations__['return'] is not None: 
                return result
    return wrapper

def create_decorator_for_class(
    callable:TCallable, 
    decorator:TDecorator,
) -> TCallable:
    constructor = callable.__init__
    decoratorfunc = create_decorator_for_function(constructor, decorator)
    setattr(callable, "__init__", decoratorfunc)
    return callable


# Decorator Mark Functions
def is_decorator(base:DecoratorBasic) -> bool:
    return DecoratorBasic in base.__mro__

def get_decorator_context(decorator:TDecorator) -> Optional[DecoratorContext]:
    if not hasattr(decorator, DECORATOR_KEY):
        return None
    return getattr(decorator, DECORATOR_KEY)

def get_decorator_callable(decorator:TDecorator) -> Optional[TCallable]:
    context = get_decorator_context(decorator)
    if context is None:
        return None
    return context.callable

def get_decorators(decorator:TDecorator) -> List[DecoratorBasic]:
    context = get_decorator_context(decorator)
    if context is None:
        return []
    return context.decorators.copy()

def sing_with_decorator(callable:TCallable, decorator:TDecorator, base:DecoratorBasic):
    context = get_decorator_context(decorator)
    if context is None:
        context = DecoratorContext(callable)
        setattr(decorator, DECORATOR_KEY, context)     
    context.decorators.append(base)


__all__ = [
    'DecoratorBasic',
    'DecoratorContext',
    'create_decorator_for_function',
    'create_decorator_for_class',
    'is_decorator',
    'get_decorator_context',
    'get_decorator_callable',
    'get_decorators',
    'sing_with_decorator'
]
