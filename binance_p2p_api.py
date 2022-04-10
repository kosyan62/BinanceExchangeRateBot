import requests
import json

BINANCE_API_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/"
AVAILABLE_PAY_TYPES_LIST = ["Revolut", "Tinkoff", "BANK"]
AVAILABLE_FIAT_LIST = ["EUR", "USD", "RUB"]


def get_data(url, json_data):
    response = requests.post(url + "search", json=json_data)
    if response.ok:
        try:
            return response.json()
        except json.JSONEncoder:
            return None
    else:
        return None



def format_json(trade_type, fiat, asset, trans_amount=None, pay_types=None, publisher_type=None):
    """
    Функция формирующая json для запроса binance p2p. 
    Параметры аналогичны, что и у вызывающей.
    :return: dict для запроса или None при неверных входных значениях
    """

    # Валидируем входные данные. В случае, если что-то не так, возвращаем None
    if not pay_types:
        pay_types = []
    else:
        if pay_types not in AVAILABLE_PAY_TYPES_LIST:
            return None
    if fiat not in AVAILABLE_FIAT_LIST:
        return None
    if trans_amount:
        if type(trans_amount) == int:
            trans_amount = str(trans_amount)
        elif type(trans_amount) == str:
            try:
                int(trans_amount)
            except ValueError:
                return None
        else:
            return None

    # Формируем словарь
    final_json = {
        "payTypes": pay_types,
        "publisherType": publisher_type,
        "asset": asset,
        "tradeType": trade_type,
        "fiat": fiat
    }
    if trans_amount:
        final_json["transAmount"] = trans_amount

    return final_json


def p2p_price(trade_type, fiat, asset, trans_amount=None, pay_types=None, publisher_type=None):
    """
    Функция возвращает самую низкую цену p2p предложений binance
    :param trade_type: "BUY" или "SELL" ищем предложения о покупке, или о продаже
    :param fiat: Валюта (Доллар/Евро/Рубли) TODO Добавить валюты
    :param asset: Криптовалюта, через которую будет рассчитываться курс
    :param trans_amount: Количество фиата, который покупается/продается
    :param pay_types: Способы перевода
    :param publisher_type: Надежный/ненадежный поставщик
    :return: str самая низкая цена на рынке
    """
    json_request = format_json(trade_type, fiat, asset, trans_amount, pay_types, publisher_type)
    if not json_request:
        return None
    json_request["page"] = 1
    json_request["rows"] = 1
    response = get_data(BINANCE_API_URL, json_request)
    if response['code'] != '000000':
        return None
    lowest_price = response['data'][0]['adv']['price']
    return lowest_price


def get_exchange_rate(from_fiat, to_fiat, middle_crypto='ETH'):
    """
    Получить текущий курс обмена через промежуточную криптовалюту
    :param from_fiat: Валюта продажи
    :param to_fiat: Валюта покупки
    :param middle_crypto: Криптовалюта, через которую осуществляется обмен
    :return:
    """
    buy_rate = p2p_price("BUY", from_fiat, middle_crypto)
    sell_rate = p2p_price("SELL", to_fiat, middle_crypto)
    return str((float(buy_rate)/float(sell_rate)))
