<a name="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]







<!-- About -->
<div align="center">

<h3 align="center">Python decoratorbasic</h3>

<p align="center">

Simple tools for creating and managing decorators in Python.

[Changelog][changelog-url] · [Report Bug][issues-url] · [Request Feature][issues-url]
 
</p>

</div>



<!-- ABOUT THE PROJECT -->

##  About The Project

Provides simple decorator utilities for Python 3.x.

###  Built With

* [![python-shield][python-shield]][pypi-project-url]

<br>


<!-- GETTING STARTED -->

##  Getting Started

To get a local copy up and running follow these simple example steps.

###  Prerequisites

 * Python-lib - [CallableType][pythonlib-callabletype] has been used for advanced type checking.

###  Installation

1. Clone the repo
```sh
git clone https://github.com/TahsinCr/python-decoratorbasic.git
```

2. Install PIP packages
```sh
pip install decoratorbasic
```


<br>



<!-- USAGE EXAMPLES -->

##  Usage

Let's create a decorator named Timer
```python
from typing import Any, Callable, TypeVar, Generic
import time

from decoratorbasic import (
    DecoratorBasic, get_decorator_callable, get_decorators
)
TCallable = TypeVar('TCallable', bound=Callable)    

class TimerDecorator(DecoratorBasic[TCallable], Generic[TCallable]):
    def definator(self, callable:TCallable):
        print(f"Add Decorator '{callable.__name__}': '{self.__class__.__name__}'")
        return callable

    def decorator(self, callable:TCallable, *args, **kwargs):
        self.start = time.time()
        result = callable(*args, **kwargs)
        self.end = time.time()
        print(f"Result '{callable.__name__}': {self.end - self.start}")
        return result

@TimerDecorator()
def test_range(start:int, stop:int):
    for n in range(start, stop): ...

@TimerDecorator()
class testo:
    def __init__(self):
        for n in range(1, 10000000):...

test_range(1,4000000)

print('DecoratorFunction: {}; BaseFuntion: {}'.format(test_range, get_decorator_callable(test_range)))

print('Decorators: {}'.format(str(get_decorators(test_range))))

testo()

```
Output
```
Add Decorator 'test_range': 'TimerDecorator'
Add Decorator 'testo': 'TimerDecorator'
Result 'test_range': 0.06389307975769043
DecoratorFunction: <function test_range at 0x000001C8395540E0>; BaseFuntion: <function test_range at 0x000001C839161440>
Decorators: [<__main__.TimerDecorator object at 0x000001C8393C1400>]
Result '__init__': 0.1724531650543213
```

_For more examples, please refer to the [Documentation][wiki-url]_

<br>





<!-- LICENSE -->

##  License

Distributed under the MIT License. See [LICENSE][license-url] for more information.


<br>





<!-- CONTACT -->

##  Contact

Tahsin Çirkin - [@TahsinCrs][x-url] - TahsinCr@outlook.com

Project: [TahsinCr/python-decoratorbasic][project-url]







<!-- IMAGES URL -->

[python-shield]: https://img.shields.io/pypi/pyversions/decoratorbasic?style=flat-square

[contributors-shield]: https://img.shields.io/github/contributors/TahsinCr/python-decoratorbasic.svg?style=for-the-badge

[forks-shield]: https://img.shields.io/github/forks/TahsinCr/python-decoratorbasic.svg?style=for-the-badge

[stars-shield]: https://img.shields.io/github/stars/TahsinCr/python-decoratorbasic.svg?style=for-the-badge

[issues-shield]: https://img.shields.io/github/issues/TahsinCr/python-decoratorbasic.svg?style=for-the-badge

[license-shield]: https://img.shields.io/github/license/TahsinCr/python-decoratorbasic.svg?style=for-the-badge

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555



<!-- Github Project URL -->

[project-url]: https://github.com/TahsinCr/python-decoratorbasic

[pypi-project-url]: https://pypi.org/project/decoratorbasic

[contributors-url]: https://github.com/TahsinCr/python-decoratorbasic/graphs/contributors

[stars-url]: https://github.com/TahsinCr/python-decoratorbasic/stargazers

[forks-url]: https://github.com/TahsinCr/python-decoratorbasic/network/members

[issues-url]: https://github.com/TahsinCr/python-decoratorbasic/issues

[wiki-url]: https://github.com/TahsinCr/python-decoratorbasic/wiki

[license-url]: https://github.com/TahsinCr/python-decoratorbasic/blob/master/LICENSE

[changelog-url]:https://github.com/TahsinCr/python-decoratorbasic/blob/master/CHANGELOG.md



<!-- Contacts URL -->

[linkedin-url]: https://linkedin.com/in/TahsinCr

[x-url]: https://twitter.com/TahsinCrs

<!-- Dependencies URL -->

[pythonlib-callabletype]: https://github.com/TahsinCr/python-callabletype

