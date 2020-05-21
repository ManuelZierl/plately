# Plately

Plately is a simple templating-engie written in pure python to make massive templating as 
easy as possible. This includes operations like iterative and combinaaiton tamplate building tasks

*... Plately is still work in progress ...*

## Getting started
```python
from plately import Parser

template = """
Dear {(customer)},
It is {.January,February,March.} the {.1,2,3.}th
this is the {o1,1o}th e-mail you receive from us
Your Lucky number of tody is: {?1,2,3,4,5,6,7?}
"""

for result in Parser.parse(template, {"customer": "Anna"}):
    print(result)
```
<details>
  <summary>output</summary>
    
    ```
    Dear Anna,
    It is January the 1th
    this is the 1th e-mail you receive from us
    Your Lucky number of tody is: 3
    
    
    Dear Anna,
    It is January the 2th
    this is the 2th e-mail you receive from us
    Your Lucky number of tody is: 3
    
    
    Dear Anna,
    It is January the 3th
    this is the 3th e-mail you receive from us
    Your Lucky number of tody is: 1
    
    
    Dear Anna,
    It is February the 1th
    this is the 4th e-mail you receive from us
    Your Lucky number of tody is: 1
    
    
    Dear Anna,
    It is February the 2th
    this is the 5th e-mail you receive from us
    Your Lucky number of tody is: 1
    
    
    Dear Anna,
    It is February the 3th
    this is the 6th e-mail you receive from us
    Your Lucky number of tody is: 1
    
    
    Dear Anna,
    It is March the 1th
    this is the 7th e-mail you receive from us
    Your Lucky number of tody is: 4
    
    
    Dear Anna,
    It is March the 2th
    this is the 8th e-mail you receive from us
    Your Lucky number of tody is: 4
    
    
    Dear Anna,
    It is March the 3th
    this is the 9th e-mail you receive from us
    Your Lucky number of tody is: 3       
    ```
  
</details>

## Operations Overview
 A list of the availaibe operations, provided with the first to outputs of the given examples. For a more indepth explanation
 read below ...
 
| type              |  short description                                        | example             |  first-output  | second-output| mnemonic
|---                |---                                                        |---                  |---             |---           |---
| identity          | string is alway converted to itself (useful for escaping) | `{ plately }`       | `"plately"`    |`"plately"`   |
| [product](product)| cartesian product is build between all products           | `{.1,2.}_{.1,2.}`   | `"1_1"`        |`"1_2"`       | point is symbol for product
| iteration         | elements are iterated                                     | `{[1,2]}_{[1,2]}`   | `"1_1"`        |`"2_2"`       | list = iterator  
| random            | random element is choosen                                 | `{?a,b,c?}`         | `"c"`          |`"a"`         | what will i take?
| interval_iterator | elements are iterated but repetent for specific interval  | `{-1,2;2-}`         | `"1"`          |`"1"`         |
| variable          | string is defined by variable name                        | `{(var1)}`          |                |              |
| infinite_iterator | iterterats to infitity until all other operators have sto | `{(oo)}`            |  `"1"`         |`"2"`         | oo = ∞          
## Operations

Be aware that you can also comine all of these operations in your string. If you are then interatin to all
todo: explain max iteration

#### identity
The `identity` always gets interpreted as itself.

```python
from plately import Parser
for templ in Parser.parse("a{ b }c"):
    print(templ)

```
```
abc
```
this is especially useful for escaping charcters so for example
```python
from plately import Parser
print(Parser.parse("{ { }}"))
```
```
{}
```
the blank spaces are mandatory for plately.

#### product
<a name="pookie"></a>
the product build the caresian product between all other products in an template
```python
from plately import Parser
for result in Parser.parse("img_{.1,2.}_{.1,2,3.}.png"):
    print(result)
```
```
img_1_1.png
img_1_2.png
img_1_3.png
img_2_1.png
img_2_2.png
img_2_3.png
````

#### iteration
```python
from plately import Parser
for result in Parser.parse("img_{[a,b,c]}.png"):
    print(result)
```
img_a.png
img_b.png
img_c.png

#### random
```python
from plately import Parser
Parser.parse("img_{?a,b,c?}.png")
```
```
img_a.png
```

#### interval_iteration
```python
from plately import Parser
for result in Parser.parse("img_{-a,b;2-}{[1,2]}.png"):
    print()
```
```
img_a1.png
img_a2.png
img_b1.png
img_b2.png
```

#### variable
```python
from plately import Parser
for result in Parser.parse("__{(var1)}__", {"var1": "hallo welt"}):
    print(result)
```
``` 
__hallo welt__
``` 

#### infinite_iterator
# todo: 

## Contributing
#TODO: 
still very new might contain bugs please report so in issues
Everybody welcome to contribute
If you are missing an operator feel free to create an issue or merge request
Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors
# TODO:
* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License
# TODO: 
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

#todo: complex examples

