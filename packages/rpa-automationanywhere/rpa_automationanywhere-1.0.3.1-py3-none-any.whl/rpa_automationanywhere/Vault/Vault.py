""" Implements Automation Anywhere 360 API to use Credential Vault. """

from typing import Literal
from collections import namedtuple
import requests
from RPA.Robocorp.Vault import Secret

Attribute = namedtuple("Attribute", ["name", "description", "userProvided", "masked", "passwordFlag", "value"])


class Vault:
    """
    The library wraps Automation Anywhere 360 API, giving robots the ability to manage the values stored in the Credential Vault.

    Args:
            control_room_uri (str): URL of Automation Anywhere A360 Control Room
            username (str): user name with access to the Vault (API)
            password (str): user password
    """

    def __init__(self, control_room_uri: str, username: str, password: str):
        self.endpoints: dict = {
            'control_room': control_room_uri.rstrip('//'),
            'authentication': f'{control_room_uri.rstrip("//")}/v1/authentication',
            'new-authentication': f'{control_room_uri.rstrip("//")}/v2/authentication',
            'credentials': f'{control_room_uri.rstrip("//")}/v2/credentialvault/credentials',
            'credentialvault': f'{control_room_uri.rstrip("//")}/v2/credentialvault',
            'lockers': f'{control_room_uri.rstrip("//")}/v2/credentialvault/lockers'
        }
        self.username: str = username
        self.password: str = password
        self.token = self.__authenticate__()

    def get_token(self) -> str:
        """
        Returns token generated

        Returns:
            str: token value
        """
        if self.token is None:
            self.__authenticate__()
        return self.token

    def get_credential(self, name: str) -> Secret:
        """
        Fetch credential from the credential vault.

        Args:
            name (str): credential name

        Raises:
            Exception: requests exceptions

        Returns:
            dict: dictionary of all credential's attributes
        """
        try:
            response = self.__get_credentials_list__()
            attributes: dict = {}
            for item in response['list']:
                if item['name'] == name:
                    for attribute in item['attributes']:
                        attributes[attribute['name']] = self.__get_attribute_value__(item['id'], attribute['id'])
                    return Secret(name=name, description='Credential fetched from A360 Credential Vault', values=attributes)
            raise Exception(f'Cannot fetch credential {name} from the Credential Vault. Check if the name is correct.')
        except Exception as ex:
            raise Exception(f'Cannot fetch credential {name}.\n\r') from ex

    def create_credential(self, name: str, attributes: list[Attribute], description: str = ''):

        credential_attributes = [attribute._asdict() for attribute in attributes]

        response = requests.post(
            url=f'{self.endpoints["credentials"]}',
            headers=self.__get_headers__(),
            json={"name": name, "description": description, "attributes": credential_attributes},
            timeout=360
        )

        if response.status_code != 201:
            raise Exception(f'{response.status_code} : {response.text}') from requests.exceptions.RequestException

        credential_id = response.json()["id"]

        # for item in response.json()["attributes"]:
        #     for attribute in attributes:
        #         if attribute.name == item['name']:
        #             self.create_credential_attribute_value(credential_id, item["id"], attribute.value)

    def create_credential_attribute_value(self, credential_id: str, attribute_id: str, value: str):
        response = requests.post(
            url=f'{self.endpoints["credentials"]}/{credential_id}/attributevalues?encryptionKey={self.__get_rsa_public_key__()}',
            headers=self.__get_headers__(),
            json={"list": [{"credentialAttributeId": attribute_id, "value": value}]},
            timeout=360
        )

        if response.status_code != 200:
            raise Exception(f'{response.status_code} : {response.json()}') from requests.exceptions.RequestException

        return response.json()

    def update_credential_attribute_value(self, credential_id: str, attribute_value_id: str, value: str, version: str):
        response = requests.put(
            url=f'{self.endpoints["credentials"]}/{credential_id}/attributevalues/{attribute_value_id}?encryptionKey={self.__get_rsa_public_key__()}',
            headers=self.__get_headers__(),
            json={"value": value, "version": version},
            timeout=360
        )

        if response.status_code != 200:
            raise Exception(f'{response.status_code} : {response.json()}') from requests.exceptions.RequestException

        return response.json()

    def get_locker(self, name: str):
        lockers = ''

    def add_credential_to_locker(self, credential_id: str, locker_name: str):
        lockers = self.__get_lockers_list__()['list']
        locker_id: str
        for locker in lockers:
            if locker['name'] == locker_name:
                locker_id = locker["id"]

        response = requests.put(
            url=f'{self.endpoints["lockers"]}/{locker_id}/credentials/{credential_id}',
            headers=self.__get_headers__(),
            json={"id": locker_id, "credentialId": credential_id},
            timeout=360
        )

        if response.status_code != 200:
            raise Exception(f'{response.status_code} : {response.json()}') from requests.exceptions.RequestException

        return response.json()

    def __get_rsa_public_key__(self):
        response = requests.get(
            url=f'{self.endpoints["credentialvault"]}/keys/transport/public',
            headers=self.__get_headers__(),
            json='',
            timeout=360
        )

        if response.status_code != 200:
            raise Exception(f'{response.status_code} : {response.text}') from requests.exceptions.RequestException

        return response.json()["publicKey"]

    def __get_credential__(self, name: str) -> dict:
        for item in self.__get_credentials_list__()['list']:
            if item['name'].lower() == name.lower():
                return item
        return {}

    def __list_credentials__(self, output_format: Literal['json', 'string'] = 'json') -> list:
        try:
            response = self.__get_credentials_list__()

            credentials: list = []
            for item in response['list']:
                if output_format == 'json':
                    credential: dict = {'name': item['name'].replace(' ', '-').lower(), 'value': {}, 'content_type': 'json'}
                    for attribute in item['attributes']:
                        credential['value'][attribute['name']] = self.__get_attribute_value__(item['id'], attribute['id'])
                else:
                    credential: dict = {'name': item['name']}
                    for attribute in item['attributes']:
                        credential[attribute['name'].lower()] = self.__get_attribute_value__(item['id'], attribute['id'])
                credentials.append(credential)
            return credentials
        except Exception as ex:
            raise Exception('Cannot list credentials') from ex

    def __authenticate__(self) -> str:
        response = requests.post(
            url=self.endpoints['authentication'],
            json={"username": self.username, "password": self.password, "multipleLogin": True},
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=30
        )
        if response.status_code != 200:
            response = requests.post(
                url=self.endpoints['new-authentication'],
                json={"username": self.username, "password": self.password, "multipleLogin": True},
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=30
            )
            if response.status_code != 200:
                raise Exception(f'{response.status_code} : {response.text}') from requests.RequestException
        self.token = response.json()['token']
        return self.token

    def __get_headers__(self):
        if self.token is None:
            self.__authenticate__()
        return {'X-Authorization': self.token}

    def __get_lockers_list__(self):
        response = requests.post(
            url=f'{self.endpoints["lockers"]}/list',
            headers=self.__get_headers__(),
            json={"filter": {"operator": "gt", "field": "createdOn", "value": "2000-10-12T00:00:00.123Z"}, "sort": [{"field": "id", "direction": "asc"}], "page": {"offset": 0, "length": 9999}},
            timeout=360
        )
        return response.json()

    def __get_credentials_list__(self):
        response = requests.post(
            url=f'{self.endpoints["credentials"]}/list',
            headers=self.__get_headers__(),
            json={"fields": [], "page": {"offset": 0, "length": 9999}, "sort": [{"field": "id", "direction": "asc"}]},
            timeout=360
        )

        if response.status_code != 200:
            raise Exception(f'{response.status_code} : {response.text}') from requests.exceptions.RequestException

        return response.json()

    def __get_attribute_value__(self, credential_id: str, attribute_id: str):
        response = requests.get(
            url=f'{self.endpoints["credentials"]}/{credential_id}/attributevalues?credentialAttributeId={attribute_id}',
            headers=self.__get_headers__(),
            timeout=360
        )

        if response.status_code != 200:
            raise Exception(f'{response.status_code} : {response.text}') from requests.RequestException

        values = response.json()['list']
        for value in values:
            if value['credentialAttributeId'] == attribute_id:
                return value['value']
        raise Exception(f'Cannot get value for credential id: {credential_id}, attribute id: {attribute_id}') from ValueError

    def __get_file_extention__(self, file_path: str) -> str:
        return file_path.split('.')[-1].lower()
