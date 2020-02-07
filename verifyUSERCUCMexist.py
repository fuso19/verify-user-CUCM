'''
VERIFICA SE O USUÁRIO JÁ EXISTE NO CUCM

CASO EXISTA, RESETA A SENHA
'''


from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from lxml import etree


disable_warnings(InsecureRequestWarning)

username = 'USERNAME'
password = 'PASSWORD'
# If you're not disabling SSL verification, host should be the FQDN of the server rather than IP
host = 'CUCM_IP'

wsdl = 'PATH TO WSDL FILE'
location = 'https://{host}:8443/axl/'.format(host=host)
binding = "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding"

# Create a custom session to disable Certificate verification.
# In production you shouldn't do this,
# but for testing it saves having to have the certificate in the trusted store.
session = Session()
session.verify = False
session.auth = HTTPBasicAuth(username, password)

transport = Transport(cache=SqliteCache(), session=session, timeout=20)
history = HistoryPlugin()
client = Client(wsdl=wsdl, transport=transport, plugins=[history])
service = client.create_service(binding, location)

# FUNCAO PARA TROUBLESHOOT


def show_history():
    for item in [history.last_sent, history.last_received]:
        print(etree.tostring(item["envelope"],
                             encoding="unicode", pretty_print=True))


print('Verificar se usuario <x> existe no CUCM: \n')
userCUCM = input('UserID (login): ')
passwordUSER = input('PASSWORD')

try:
    # passar userCUCM como variavel
    resp = service.getUser(userid='{}'.format(userCUCM))
    userCONSULT = resp['return'].user.userid
    if (userCUCM == userCONSULT):
        print('Usuario ja existe.')
        resetPSWD = input('Deseja resetar a senha? (Y/N): ')
        if (resetPSWD == 'Y' or resetPSWD == 'y'):
            try:
                updateUSER = service.updateUser(
                    userid='{}'.format(userCUCM), password=passwordUSER)  # passar userCUCM como variavel
                print('Senha atualizada: ' + passwordUSER)
            except Fault:
                show_history()
        else:
            pass
    else:
        print('Usuario {name} nao cadastrado no CUCM'.format(name=userCUCM))
except Fault:
    show_history()
