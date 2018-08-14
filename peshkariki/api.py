from typing import List
import logging
from urllib.parse import urljoin

import requests

from .constants import (
    ERRORS, STATUSES, PAYMENT_METHODS, TOWNS, ORDER_TYPES,
    TownEnum, PaymentEnum, OrderTypeEnum
)

logger = logging.getLogger(__name__)


class ApiException(Exception):
    pass


class ServiceException(ApiException):
    def __init__(self, code: int, additional):
        self.code = code
        self.additional = additional
        self.service_msg = ERRORS[code]
        msg = (
            f'Peshkariki error with code #{code}: '
            f'{self.service_msg}; {additional or ""}'
        )
        super().__init__(msg)


class PeshkarikiAPI:
    BASE_API_URL = 'https://api.peshkariki.ru/commonApi/'
    DEFAULT_HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'peshkariki-python',
    }
    DEFAULT_TIMEOUT = 5

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self._token = None
        self.update_token()

    def _make_url(self, path: str):
        return urljoin(self.BASE_API_URL, path)

    def update_token(self):
        login_data = self.login()
        self._token = login_data['token']

    def _make_request(self, path: str, data: dict, req_headers=None, timeout=None):
        url = self._make_url(path)
        headers = self.DEFAULT_HEADERS.copy()
        if req_headers:
            headers.update(req_headers)
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT
        logger.debug(f'Making POST request to {url}')
        resp = requests.post(url, json=data, headers=headers, timeout=timeout)
        data = resp.json()
        if not data['success']:
            raise ServiceException(data['code'], data['additional'])
        return data['response']

    def _make_token_request(self, path, data, **kwargs):
        data['token'] = self._token
        return self._make_request(path, data, **kwargs)

    def _make_auth_request(self, path, data, **kwargs):
        try:
            return self._make_token_request(path, data, **kwargs)
        except ServiceException as err:
            if err.code == 12:
                self.update_token()
                return self._make_token_request(path, data, **kwargs)
            raise

    def login(self):
        data = {
            'login': self.username,
            'password': self.password
        }
        return self._make_request('login', data)

    def check_status(self, order_id: int):
        data = {"order_id": order_id}
        return self._make_auth_request('checkStatus', data)

    def check_multiple_statuses(self, order_ids: List[int]):
        data = {"order_id": order_ids}
        return self._make_auth_request('checkStatus', data)

    def add_order(self,
                  inner_id: str,
                  comment: str,
                  calculate: bool=True,
                  ):
        '''
        Входные параметры:
        массив объектов orders, каждый объект orders содержит массив route и string inner_id – номер заказа в вашей системе.
        string comment – поле с кратким описанием того, что везем (напр. “Наушники”, “CD-диски” и т. п.)
        bool calculate - если 1( ~ true), то просто посчитается стоимость, но заказ не создастся(id не вернется), если 0 – публикация заказа.
        bool clearing – если 1( ~ true), то оплата будет производиться со счета в Пешкариках. Если 0, то наличными с получателя/отправителя.
        bool cash - если 1( ~ true), то необходимо забрать оплату наличными с получателя(ей), если 0 – товар предоплачен. Для создания заказа на выкуп указывается 1, в services добавляется доп. услуга выкуп (25).
        int courier_addition – произвольная доплата курьеру от заказчика. Если цена за доставку кажется заказчику недостаточной, то он может её увеличить. Заказ возьмут быстрее.
        int ewalletType – код платежной системы. Необходим, если курьер получит наличные за товар (cash = 1). См. приложение 3.
        string ewallet – реквизиты, на которые необходимо перечислить полученные деньги. (номер банковской карты, номер кошелька яндекс.денег и т.д.)
        string promo_code – промо-код на скидку (при наличии).
        int city_id – id города в системе, по которому требуется доставка. См. приложение 4.
        int order_type_id – id типа заказа. Массив route – набор параметров адреса:
        string name – имя
        string phone – телефон
        string city – город (указывать, только если пригород)
        string street – улица
        string building – дом
        string apartments – квартира
        string subway_id – id станции метро. См. приложение 6.
        timestamp time_from, time_to – диапазон времени доставки
        string target – комментарий к точке
        bool return_dot – если 1 ( ~ true), то товар, при необходимости, возвращать сюда. Для других точек можно устанавливать 0, можно не указывать. Если точка для возврата указана не будет, то ею по умолчанию будет точка забора.
        int delivery_price_to_return – сумма за доставку, которую курьер должен взять наличными с клиента и вернуть заказчику. Не указывается для точки забора (1-ая в массиве route), только для точек доставки. Если нет необходимости брать деньги за доставку – параметр не указывается (или указывается 0).
        items – массив товаров. Содержит: string name – название товара
        int weight – вес одного товара
        int price – цена одного товара
        int quant – количество товара
        Каждый объект orders содержит массив services – дополнительные услуги.  services состоит из int services_id. Их можно получить с помощью метода getServicesList.
        '''
        data = {
            'orders': [{
                'inner_id': inner_id,
                'comment': comment,
                'calculate': calculate,
            }]
        }
        return self._make_auth_request('addOrder', data)

    def get_order_details(self, order_id: int):
        data = {
            "order_id": order_id
        }
        return self._make_auth_request('addOrder', data)

    def get_multiple_order_details(self, order_id: List[int]):
        data = {
            "order_id": order_id
        }
        return self._make_auth_request('addOrder', data)

    def get_services_list(self):
        return self._make_auth_request('getServicesList', {})

    def check_balance(self):
        return self._make_auth_request('checkBalance', {})

    def check_phone(self, phone: str):
        return self._make_auth_request('checkPhone', {'phone': phone})

    def check_multiple_phones(self, phones: List[str]):
        return self._make_auth_request('checkPhone', {'phone': phones})

    def revoke_token(self):
        return self._make_auth_request('revokeToken', {})

    def change_status(self, order_id: int, status: int):
        data = {
            "orders": [{
                "order_id": order_id,
                "status": status
            }]
        }
        return self._make_auth_request('changeStatus', data)
