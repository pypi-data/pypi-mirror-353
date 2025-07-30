<a name="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]







<!-- About -->
<div align="center">

<h3 align="center">Python DecoratorFunc</h3>

<p align="center">

Simple tools for creating and managing decorator functions in Python.

[Changelog][changelog-url] · [Report Bug][issues-url] · [Request Feature][issues-url]
 
</p>

</div>



<!-- ABOUT THE PROJECT -->

##  About The Project

Provides simple decorator function utilities for Python 3.x.

###  Built With

* [![python-shield][python-shield]][pypi-project-url]

<br>


<!-- GETTING STARTED -->

##  Getting Started

To get a local copy up and running follow these simple example steps.

###  Prerequisites

 * Python-lib - [DecoratorBasic][pythonlib-decoratorbasic] has been used for basic decorator utilities.

###  Installation

1. Clone the repo
```sh
git clone https://github.com/TahsinCr/python-decoratorfunc.git
```

2. Install PIP packages
```sh
pip install decoratorfunc
```


<br>



<!-- USAGE EXAMPLES -->

##  Usage

Let's create a decorator named Timer
```python
import time

from decoratorbasic import get_decorators, get_decorator_callable
from decoratorfunc import definator, decorator, is_decoratorfunc

@definator
def time_decorator(func):
    # The DecoratorFuncBasic class is automatically created.
    # It is named according to PEP8 conventions by using the function's name (time_decorator -> TimeDecorator).
    # The generated DecoratorFuncBasic class can be accessed via time_decorator.__class__.
    print(f"Add Decorator '{func.__name__}': '{time_decorator.__class__.__name__}'")
    return func

@time_decorator.decorator
def time_decorator(func, *args, **kwargs):
    # A function defined with the definator/decorator will return a DecoratorFuncBasic class.
    # This allows the function to be redefined using the definator/decorator again. (time_decorator.decorator/time_decorator.definator)
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    print(f"Result '{callable.__name__}': {end - start}")
    return result

# Since the time_decorator function returns the DecoratorFuncBasic class, the __call__ method of this class is used as a decorator.
# In this way, the DecoratorFuncBasic class behaves like DecoratorBasic and fulfills the decorator functionality.
@time_decorator
def test_range(start:int, stop:int):
    for n in range(start, stop): ...

@time_decorator
class testo:
    def __init__(self):
        for n in range(1, 10000000):...


test_range(1,4000000)

decoratorbases = get_decorators(test_range)
print('IsDecoratorFunc:', is_decoratorfunc(decoratorbases[0]))

testo()

```
Output
```
Add Decorator 'test_range': 'TimeDecorator'
Add Decorator 'testo': 'TimeDecorator'
Result 'callable': 0.10388374328613281
IsDecoratorFunc: True
Result 'callable': 0.1656045913696289
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

Project: [TahsinCr/python-decoratorfunc][project-url]







<!-- IMAGES URL -->

[python-shield]: https://img.shields.io/pypi/pyversions/decoratorfunc?style=flat-square

[contributors-shield]: https://img.shields.io/github/contributors/TahsinCr/python-decoratorfunc.svg?style=for-the-badge

[forks-shield]: https://img.shields.io/github/forks/TahsinCr/python-decoratorfunc.svg?style=for-the-badge

[stars-shield]: https://img.shields.io/github/stars/TahsinCr/python-decoratorfunc.svg?style=for-the-badge

[issues-shield]: https://img.shields.io/github/issues/TahsinCr/python-decoratorfunc.svg?style=for-the-badge

[license-shield]: https://img.shields.io/github/license/TahsinCr/python-decoratorfunc.svg?style=for-the-badge

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555



<!-- Github Project URL -->

[project-url]: https://github.com/TahsinCr/python-decoratorfunc

[pypi-project-url]: https://pypi.org/project/decoratorfunc

[contributors-url]: https://github.com/TahsinCr/python-decoratorfunc/graphs/contributors

[stars-url]: https://github.com/TahsinCr/python-decoratorfunc/stargazers

[forks-url]: https://github.com/TahsinCr/python-decoratorfunc/network/members

[issues-url]: https://github.com/TahsinCr/python-decoratorfunc/issues

[wiki-url]: https://github.com/TahsinCr/python-decoratorfunc/wiki

[license-url]: https://github.com/TahsinCr/python-decoratorfunc/blob/master/LICENSE

[changelog-url]:https://github.com/TahsinCr/python-decoratorfunc/blob/master/CHANGELOG.md



<!-- Contacts URL -->

[linkedin-url]: https://linkedin.com/in/TahsinCr

[x-url]: https://twitter.com/TahsinCrs

<!-- Dependencies URL -->

[pythonlib-decoratorbasic]: https://github.com/TahsinCr/python-decoratorbasic

