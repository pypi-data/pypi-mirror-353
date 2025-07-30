# DecoLogger

## Install

```
pip install DecoLogger
```

## How to use it?

```
from DecoLogger.DecoLogger import DecoLogger

dl = DecoLogger("./logs/app.log")


@dl.error_logging
@dl.return_logging
@dl.time_logging
def test(aa):
    return "aaaaaaaaaaaaaaaa"

test("aaaa")

```