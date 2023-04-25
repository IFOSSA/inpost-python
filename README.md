
# Inpost Python

Fully async Inpost library using Python 3.10.




## Documentation

[Readthedocs.io](https://inpost-python.readthedocs.io/en/latest/)


## Usage/Examples


```python
from inpost.api import Inpost

inp = await Inpost.from_phone_number('555333444')
await inp.send_sms_code():
...
if await inp.confirm_sms_code(123321):
   print('Congratulations, you initialized successfully!')
```


## Authors

- [@loboda4450](https://www.github.com/loboda4450)
- [@mrkazik99](https://www.github.com/mrkazik99)


## Used By

This project is used by the following repos:

[Inpost Telegram Bot](https://github.com/loboda4450/inpost-telegram-bot)

