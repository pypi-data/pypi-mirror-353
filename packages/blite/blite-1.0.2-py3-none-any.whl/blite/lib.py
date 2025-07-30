import socket as sk
from .utils import validateIp, unpackHead, unpackUri, extractBody
import re
from _thread import start_new_thread
import json
import sys
from .httpCodes import CODES

def __stdInternalServerError():
    return b'HTTP/1.x 501 Internal Server Error\nConnection: close\n\n'

def __stdNotFoundError():
    return b'HTTP/1.x 404 Not Found\nConnection: close\n\n'

def __stdWrongMethod():
    return b'HTTP/1.x 405 Method Not Allowed\nConnection: close\n\n'

def renderFile(path):
    with open(path, 'r') as file:
        return file.read()

class Route:
    def __init__(self, route, callback, kwargs = (), methods = ['GET'], regex = False, allowOptions = True, giveMethod=False, giveUri=False, giveRequest=False):
        self.route = route
        self.callback = callback
        self.kwargs = kwargs
        self.methods = methods
        self.regex = regex
        self.allowOptions = allowOptions
        self.giveUri = giveUri
        self.giveMethod = giveMethod
        self.giveRequest = giveRequest

    def matches(self, uri, method):
        if self.regex:
            if not re.fullmatch(self.route, uri):
                return False

        else:
            if uri != self.route:
                return False

        if method in self.methods:
            return True

        if method.lower() == 'options':
            if self.allowOptions:
                return True

        return False

    def uriMatches(self, uri):
        if self.regex:
            if not re.fullmatch(self.route, uri):
                return False

        else:
            if uri != self.route:
                return False

        return True

class Response:
    def __init__(self, code, headers={'Connection: close'}, body=b''):
        if not isinstance(code, int):
            if not code.isnumeric():
                raise Exception('Wrong type for HTTP code')

        if not code in CODES:
            raise Exception('HTTP code not allowed')

        self.code = code

        if not isinstance(headers, dict):
            raise Exception('Headers must be expressed in dict')
        self.headers = headers

        self.body = body

    def pack(self):
        return (f'HTTP/1.x {self.code} {CODES[self.code]}' + '\n'.join(f'{key}: {value}' for key, value in self.headers.items()) + '\n\n').encode() + (self.body if isinstance(self.body, bytes) else self.body.encode())

class Server:
    def __init__(self, ip, port=80):
        if not validateIp(ip):
            raise Exception(f'Invalid IPv4 address: `{ip}`')

        if isinstance(port, int):
            if port < 0 or port > 65535:
                raise Exception(f'Port out of range 1-65535: `{port}`')

        else:
            raise Exception(f'Port must be an integer')

        self.__routes = []

        self.__sock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.__sock.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)

        self.__sock.bind((ip, port))

    def setRoute(self, route, kwargs=(), methods=['GET'], regex=False, allowOptions=True, giveMethod=False, giveUri=False, giveRequest=False):
        def decorator(callback):
            self.__routes.append(
                Route(
                    route=route, callback=callback, kwargs=kwargs, methods=methods, regex=regex,
                    allowOptions=allowOptions, giveMethod=giveMethod, giveUri=giveUri, giveRequest=giveRequest
                )
            )

        return decorator

    def __handler(self, client, address):
        try:
            requestBytes = client.recv(2048)

        except:
            client.send(__stdInternalServerError())
            client.close()
            return

        method, uri, _ = unpackHead(requestBytes)
        uri, kwargs = unpackUri(uri)

        found = False
        rightRoute = None

        for route in self.__routes:
            if route.matches(uri, method):
                found = True
                rightRoute = route
                break

            if route.uriMatches(uri):
                found = True
                break

        if not found:
            client.send(__stdNotFoundError())
            client.close()
            return

        if found and rightRoute is None:
            client.send(__stdWrongMethod())
            client.close()
            return

        if method == 'OPTIONS' and 'OPTIONS' not in rightRoute.methods:
            client.send(
                f'HTTP/1.1 200 Ok\nConnection: close\nAllow: {" ".join(rightRoute.methods)}\n\n'.encode()
            )
            client.close()
            return

        requestBody = extractBody(requestBytes)

        args = []

        if 'POST' in rightRoute.methods:
            args.append(requestBody)

        if rightRoute.giveMethod:
            args.append(method)

        if rightRoute.giveUri:
            args.append(uri)

        if rightRoute.giveRequest:
            args.append(requestBytes)

        try:
            responseBody = rightRoute.callback(*args, **kwargs)

        except TypeError:
            client.send(__stdInternalServerError())
            client.close()

            exceptionText = f'the callback function for "{method} {uri}" is expected to take at least {len(args)} positional argument(s): '
            expectedArgs = []

            if 'POST' in rightRoute.methods:
                expectedArgs.append('requestBody')

            if rightRoute.giveMethod:
                expectedArgs.append('method')

            if rightRoute.giveUri:
                expectedArgs.append('uri')

            if rightRoute.giveRequest:
                expectedArgs.append('requestBytes')

            raise Exception(exceptionText + ', '.join(expectedArgs))

        except Exception as e:
            print(f'Warning: callback function "{rightRoute.callback.__name__}" failed handling "{method} {uri}" because `{e}`', file=sys.stderr)
            client.send(__stdInternalServerError())
            client.close()
            return

        if responseBody is None:
            client.send('HTTP/1.1 200 Ok\nConnection: close\n\n'.encode())
            client.close()
            return

        responseHeaders = {}

        if isinstance(responseBody, tuple):
            responseHeaders = responseBody[1]
            responseBody = responseBody[0]

        for key, value in [('Connection', 'close'), ()]:
            if key not in responseHeaders:
                responseHeaders[key] = value

        if isinstance(responseBody, dict):
            strJson = json.dumps(responseBody)

            if 'Content-Type' not in responseHeaders:
                responseHeaders['Content-Type'] = 'application/json'

            if 'Content-Length' not in responseHeaders:
                responseHeaders['Content-Length'] = str(len(strJson))

            strHeaders= '\n'.join(f'{key}: {value}' for key, value in responseHeaders.items())

            client.send(
                f'HTTP/1.1 200 Ok\n{strHeaders}\n\n{strJson}'.encode()
            )
            client.close()
            return

        elif isinstance(responseBody, str):
            if 'Content-Type' not in responseHeaders:
                responseHeaders['Content-Type'] = 'text/plain'

            if 'Content-Length' not in responseHeaders:
                responseHeaders['Content-Length'] = str(len(responseBody))

            strHeaders = '\n'.join(f'{key}: {value}' for key, value in responseHeaders.items())

            client.send(
                f'HTTP/1.1 200 Ok\n{strHeaders}\n\n{responseBody}'.encode()
            )
            client.close()
            return

        elif isinstance(responseBody, bytes):
            if 'Content-Type' not in responseHeaders:
                responseHeaders['Content-Type'] = 'application/bytes'

            if 'Content-Length' not in responseHeaders:
                responseHeaders['Content-Length'] = str(len(responseBody))

            strHeaders = '\n'.join(f'{key}: {value}' for key, value in responseHeaders.items())

            client.send(
                f'HTTP/1.1 200 Ok\n{strHeaders}\n\n'.encode() + responseBody
            )
            client.close()
            return

        elif isinstance(responseBody, Response):
            client.send(responseBody.pack())
            client.close()
            return

        else:
            client.send(__stdInternalServerError().encode())
            client.close()
            raise Exception(f'Unexpected return type: `{type(responseBody)}`')

    def listen(self):
        self.__sock.listen()

        while True:
            client, address = self.__sock.accept()
            start_new_thread(self.__handler, (client, address))