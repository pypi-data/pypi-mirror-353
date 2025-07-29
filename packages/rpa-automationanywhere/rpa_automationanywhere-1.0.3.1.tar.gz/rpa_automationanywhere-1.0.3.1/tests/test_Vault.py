import unittest
from rpa_automationanywhere.Vault import Vault, Attribute

CONTROL_ROOM_URI = 'http://control-room-url.here'
USER_ID = 'domain\\username'
PASSWORD = 'password'
TEST_CREDENTIAL_NAME = 'demo'

VAULT = Vault(
    control_room_uri=CONTROL_ROOM_URI,
    username=USER_ID, password=PASSWORD
)


class Test_Vault(unittest.TestCase):
    def test_get_credential(self):
        print(VAULT.get_credential(TEST_CREDENTIAL_NAME))

    def test_get_token(self):
        print(VAULT.get_token())

    def test_create_credential(self):

        accounts = [
            {'login': 'RPAGFC01', 'password': r'(ddddd'},
            {'login': 'RPAGFC02', 'password': r'(ddddd'},
            {'login': 'RPAGFC03', 'password': r'(ddddd'},
            {'login': 'RPAGFC04', 'password': r'(ddddd'},
            {'login': 'RPAGFC05', 'password': r'(ddddd'},
            {'login': 'RPAGFC06', 'password': r'(ddddd'},
            {'login': 'RPAGFC07', 'password': r'(ddddd'}
        ]

        for account in accounts:
            response = VAULT.create_credential(
                name=f'SAP Production Japan {account["login"]}',
                description="",
                attributes=[
                    Attribute(
                        "login",
                        "",
                        False,
                        False,
                        False,
                        account['login']
                    ),
                    Attribute(
                        "password", 
                        "",
                        False,
                        True,
                        False,
                        account['password']
                    )
                ]
            )
            print(response)

    def test_get_rsa_public_key(self):
        print(VAULT.__get_rsa_public_key__())

    def test_get_lockers_list(self):
        print(VAULT.__get_lockers_list__()['list'])

    def test_add_credential_to_locker(self):
        print(VAULT.add_credential_to_locker())

    def test_credential_list(self):
        values = VAULT.__get_credentials_list__()

        print(len(values))

        for value in values:
            print(values[value])
