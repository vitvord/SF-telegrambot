import logging

import requests
import yaml

LOG = logging.getLogger('exchange')


class ExchangeExceptions(Exception):
    pass


class Exchange:
    BASEURL = 'https://api.exchangeratesapi.io/latest'

    def __init__(self, base='RUB'):
        self.base = base
        self.currency_names, self.currency_names_abbr = self.load_currency_list()

    @staticmethod
    def load_currency_list(config_file='config-bot.yml'):
        with open(config_file, 'r') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
        return config['currency'], {val: key for key, val in config['currency'].items()}

    def get_all_rates(self):
        if self.base:
            req = requests.get(self.BASEURL + f'?base={self.base}')
        else:
            req = requests.get(self.BASEURL)
            self.base = req.json()['base']
        result = [f"{x} ({self.currency_names_abbr[x]}) - {y}" for x, y in req.json()['rates'].items() if
                  x in self.currency_names.values()]
        return result, self.base

    def convert_currency_to_abbreviation(self, f, to):
        if f not in self.currency_names:
            LOG.error(f"Can't get currency with name: {f}")
            raise ExchangeExceptions(f"Can't get currency with name: {f}")
        if to not in self.currency_names:
            LOG.error(f"Can't get currency with name: {to}")
            raise ExchangeExceptions(f"Can't get currency with name: {to}")
        return self.currency_names[f], self.currency_names[to]

    def get_price(self, base: str, quote: str, amount: float) -> float:
        base, quote = self.convert_currency_to_abbreviation(base, quote)
        req = requests.get(self.BASEURL + f'?base={base}&' + f'symbols={quote}')
        try:
            cur = float(req.json()['rates'][quote])
        except ValueError:
            LOG.error(f"A strange value from http API")
            raise ExchangeExceptions("I don't understand currency value got from external API")
        try:
            cur = float(cur)
        except:
            LOG.exception("Can't parse currency value from API")
            raise ExchangeExceptions(
                "Can't parse currency value. Please check available currency list (use /values command)")
        return cur * amount

    def get_course_from_text(self, text: str):
        try:
            from_cur, to_cur, value = text.split(' ')
        except Exception as e:
            LOG.exception(f"Can't parse request text from user")
            raise ExchangeExceptions("Can't parse user request")

        try:
            value = float(value)
        except ValueError:
            LOG.exception("Can't parse currency amount")
            raise ExchangeExceptions(
                "Can't parse currency value. Please check available currency list (use /values command)")

        cur = self.get_price(from_cur, to_cur, value)
        return f"Цена {value} {from_cur} в {to_cur} {cur}"
