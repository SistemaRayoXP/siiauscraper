# Módulo siiauscraper
# Autor: SistemaRayoXP
# Fecha de Creación: 18/10/2023
#
# Copyright (c) 2023 Edson Armando Alvarez
#
# Licenciado bajo la Licencia MIT.
# Consulta el archivo LICENSE para obtener más detalles.

import sys
import base64
import requests
import urllib3

from bs4 import BeautifulSoup

from . import errormessages
from . import platform

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


SIIAU_SERVER_NAME = "siiauescolar.siiau.udg.mx"
SIIAU_SERVER_URL = f"https://{SIIAU_SERVER_NAME}"
SIIAU_SERVER_INSTANCE = f"{SIIAU_SERVER_URL}/wus"
DEFAULT_HEADERS = {
    "Accept": "*/*",
    "User-Agent": platform.getPlatformUserAgent(),
}


class Scraper:
    cookiejar = None

    def __init__(self):
        pass

    def createSoup(self, data: str, parser: str = 'lxml'):
        return BeautifulSoup(data, parser)

    def downloadPage(self, url: str, method: str = 'GET', silent=False, **kwargs):
        try:
            if self.cookiejar:
                kwargs['cookies'] = self.cookiejar

            if kwargs.get("headers", None):
                headers = DEFAULT_HEADERS
                headers.update(kwargs.pop("headers"))
            else:
                headers = DEFAULT_HEADERS

            # print(url, method, kwargs.get("params", None), file=sys.stderr) # Debug

            if method == 'POST':
                response = requests.post(
                    url, headers=headers, verify=False, **kwargs)
            elif method == 'OPTIONS':
                response = requests.options(
                    url, headers=headers, verify=False, **kwargs)
            elif method == 'HEAD':
                response = requests.head(
                    url, headers=headers, verify=False, **kwargs)
            else:
                if kwargs.get('data') and not kwargs.get('params'):
                    kwargs['params'] = kwargs['data']
                    kwargs.pop('data')

                response = requests.get(
                    url, headers=headers, verify=False, **kwargs)

            self.cookiejar = response.cookies

            if not response.ok and not silent:
                raise ConnectionError(response.status_code)
            else:
                return response

        except Exception as e:
            if silent:
                return None
            else:
                raise e

    def downloadSoup(self, url: str, method: str = 'GET', silent=True, parser='lxml', **kwargs):
        try:
            response = self.downloadPage(url, method, silent, **kwargs)
            if response:
                return self.createSoup(response.text, parser)
            else:
                return self.createSoup("")

        except Exception:
            return None

    def getAplication(self, app: str, func: str, method: str = "GET",
                      data=None, silent=False, referer=None, soup=False,
                      **kwargs):
        kwargs["data"] = data

        default_request_headers = {
            "Host": SIIAU_SERVER_NAME,
            "Origin": SIIAU_SERVER_URL,
        }

        if isinstance(referer, str):
            default_request_headers['Referer'] = referer

        if kwargs.get("headers") and isinstance(kwargs["headers"], dict):
            kwargs["headers"].update(default_request_headers)
        else:
            kwargs["headers"] = default_request_headers

        url = f"{SIIAU_SERVER_INSTANCE}/{app}.{func}"

        if soup:
            response = self.downloadSoup(url, method, silent=silent, **kwargs)
        else:
            response = self.downloadPage(url, method, silent=silent, **kwargs)

        return response


class LoginScraper(Scraper):
    __user__ = None
    __pssw__ = None
    _isLogged_ = False
    _session_ = None
    _response_ = None

    def __init__(self, user: str = "", pssw: str = ""):
        super().__init__()
        self.__user__ = self.__encode__(user)
        self.__pssw__ = self.__encode__(pssw)
        self.__login__(True)

    def __login__(self, silent=False):
        if not self.__user__ and not self.__pssw__:
            if silent:
                return
            else:
                raise ValueError("No user or password provided")

        # Get Oracle Application Server session cookies
        self.getAplication("gupprincipal", "inicio_f", silent=silent)
        self.getAplication("gupprincipal", "encabezado", silent=silent)

        # Get login form inputs (for validation)
        loginSoup = self.getAplication(
            "gupprincipal", "forma_inicio", silent=silent, soup=True)
        loginForm = loginSoup.find(
            'form', action="gupprincipal.forma_inicio_bd")

        if not loginForm:
            if silent:
                return
            else:
                raise NotImplementedError("Website structure has changed")

        loginInputs = loginForm.findAll(
            'input', {"name": lambda x: not "_" in x})
        credentials = {"p_codigo_c": self.__decode__(self.__user__),
                       "p_clave_c": self.__decode__(self.__pssw__)}
        loginData = dict(credentials)
        loginData.update({x['name']: x['value'] for x in loginInputs})

        self.getAplication("gupprincipal",
                           "forma_inicio_bd",
                           "POST",
                           loginData)
        loginResponse = self.getAplication("gupprincipal",
                                           "valida_inicio",
                                           "POST",
                                           credentials)
        if errormessages.WRONG_CREDENTIALS in loginResponse.text:
            self._isLogged_ = False
        elif errormessages.ACCESS_BLOCKED in loginResponse:
            if errormessages.BLOCKED_TOO_MANY_ATTEMPTS in loginResponse:
                reason = "Too many attempts"
            else:
                reason = "Unknown"
            print(f"Access blocked. Reason: {reason}", file=sys.stderr)
            self._isLogged_ = False
        else:
            soup = self.createSoup(loginResponse.text)
            soup = soup.find("input", {"name": "p_pidm_n"})
            if soup and soup.get('value', None):
                self._session_ = soup['value']
            self._response_ = loginResponse
            self._isLogged_ = True

    def __logout__(self):
        self.getAplication("gupprincipal", "salir")

    def __decode__(self, s: str):
        return base64.b64decode(bytes(s, encoding='utf-8')).decode()

    def __encode__(self, s: str):
        return base64.b64encode(bytes(s, encoding='utf-8')).decode()

    def login(self, user: str, pssw: str):
        # Save user & password (for later logins?)
        self.__user__ = self.__encode__(user)
        self.__pssw__ = self.__encode__(pssw)
        self.__login__()

    def logout(self):
        self.__logout__()

    def isLogged(self):
        return self._isLogged_

    def getSession(self):
        return self._session_
