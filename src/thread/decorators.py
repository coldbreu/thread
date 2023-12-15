"""
## Decorators

Documentation: https://thread.ngjx.org
"""

from functools import wraps
from .thread import Thread

from ._types import Overflow_In, Data_Out, Data_In
from typing import Callable, Mapping, Sequence, Optional, Union, overload
from typing_extensions import ParamSpec, TypeVar


T = TypeVar('T')
P = ParamSpec('P')
TargetFunction = Callable[P, Data_Out]
NoParamReturn = Callable[P, Thread]
WithParamReturn = Callable[[TargetFunction], NoParamReturn]
FullParamReturn = Callable[P, Thread]
WrappedWithParamReturn = Callable[[TargetFunction], WithParamReturn]


@overload
def threaded(__function: TargetFunction) -> NoParamReturn: ...

@overload
def threaded(
  *,
  args: Sequence[Data_In] = (),
  kwargs: Mapping[str, Data_In] = {},
  ignore_errors: Sequence[type[Exception]] = (),
  suppress_errors: bool = False,
  **overflow_kwargs: Overflow_In
) -> WithParamReturn: ...

@overload
def threaded(
  __function: Callable[P, Data_Out],
  *,
  args: Sequence[Data_In] = (),
  kwargs: Mapping[str, Data_In] = {},
  ignore_errors: Sequence[type[Exception]] = (),
  suppress_errors: bool = False,
  **overflow_kwargs: Overflow_In
) -> FullParamReturn: ...


def threaded(
  __function: Optional[TargetFunction] = None,
  *,
  args: Sequence[Data_In] = (),
  kwargs: Mapping[str, Data_In] = {},
  ignore_errors: Sequence[type[Exception]] = (),
  suppress_errors: bool = False,
  **overflow_kwargs: Overflow_In
) -> Union[NoParamReturn, WithParamReturn, FullParamReturn]:
  """
  Decorate a function to run it in a thread

  Parameters
  ----------
  :param __function: The function to run in a thread
  :param args: Keyword-Only arguments to pass into `thread.Thread`
  :param kwargs: Keyword-Only keyword arguments to pass into `thread.Thread`
  :param ignore_errors: Keyword-Only arguments to pass into `thread.Thread`
  :param suppress_errors: Keyword-Only arguments to pass into `thread.Thread`
  :param **: Keyword-Only arguments to pass into `thread.Thread`

  Returns
  -------
  :return decorator:

  Use Case
  --------
  Now whenever `myfunction` is invoked, it will be executed in a thread and the `Thread` object will be returned

  >>> @thread.threaded
  >>>   def myfunction(*args, **kwargs): ...

  >>> myJob = myfunction(1, 2)
  >>> type(myjob)
  > Thread

  You can also pass keyword arguments to change the thread behaviour, it otherwise follows the defaults of `thread.Thread`
  >>> @thread.threaded(daemon = True)
  >>> def myfunction(): ...

  Args will be ordered infront of function-parsed args parsed into `thread.Thread.args`
  >>> @thread.threaded(args = (1))
  >>> def myfunction(*args):
  >>>   print(args)
  >>>
  >>> myfunction(4, 6).get_return_value()
  1, 4, 6
  """

  if not callable(__function):
    def wrapper(func: TargetFunction) -> FullParamReturn:
      return threaded(
        func,
        args = args,
        kwargs = kwargs,
        ignore_errors = ignore_errors,
        suppress_errors = suppress_errors,
        **overflow_kwargs
      )
    return wrapper

  overflow_kwargs.update({
    'ignore_errors': ignore_errors,
    'suppress_errors': suppress_errors
  })

  kwargs = dict(kwargs)
  
  @wraps(__function)
  def wrapped(*parsed_args: P.args, **parsed_kwargs: P.kwargs) -> Thread:
    kwargs.update(parsed_kwargs)

    processed_args = ( *args, *parsed_args )
    processed_kwargs = { i:v for i,v in parsed_kwargs.items() if i not in ['args', 'kwargs'] }

    job = Thread(
      target = __function,
      args = processed_args,
      kwargs = processed_kwargs,
      **overflow_kwargs
    )
    job.start()
    return job
  
  return wrapped


