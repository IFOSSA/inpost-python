[![CodeFactor](https://www.codefactor.io/repository/github/ifossa/inpost-python/badge)](https://www.codefactor.io/repository/github/ifossa/inpost-python)
![Code Quality](https://github.com/ifossa/inpost-python/actions/workflows/lint.yml/badge.svg?barnch=main)
![Todos](https://github.com/ifossa/inpost-python/actions/workflows/todos.yml/badge.svg?barnch=main)

# Inpost Python

Fully async Inpost library using Python 3.10.


## Documentation

[Readthedocs.io](https://inpost-python.readthedocs.io/en/latest/)


## Usage/Examples


```python
from inpost.api import Inpost

inp = Inpost('555333444')
await inp.send_sms_code():
...
if await inp.confirm_sms_code(123321):
   print('Congratulations, you initialized successfully!')
```

## Before you contribute

![Contributors](https://contrib.rocks/image?repo=ifossa/inpost-python)

Install linters and checkers, unlinted pull requests will not be approved
```commandline
poetry run pre-commit install
```

## Authors

- [@loboda4450](https://www.github.com/loboda4450)
- [@mrkazik99](https://www.github.com/mrkazik99)


## Used By

This project is used by the following repos:

[Inpost Telegram Bot](https://github.com/loboda4450/inpost-telegram-bot)



## 😂 Here is a random joke that'll make you laugh!
![Jokes Card](https://readme-jokes.vercel.app/api)