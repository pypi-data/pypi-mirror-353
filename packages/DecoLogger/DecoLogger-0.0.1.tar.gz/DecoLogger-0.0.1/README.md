# DecoratorLogger

## Install

```
pip install git+https://github.com/chogamy/DecoratorLogger.git
```

## How to use it?

```
from DecoratorLogger.DecoratorLogger import DecoratorLogger

dl = DecoratorLogger("./logs/app.log")


@dl.error_logging
@dl.return_logging
@dl.time_logging
def test(aa):
    return "aaaaaaaaaaaaaaaa"

test("aaaa")

```