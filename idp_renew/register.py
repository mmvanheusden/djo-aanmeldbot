from idp_renew.auth import AuthServer
from urllib.parse import urljoin
from datetime import date


class Register:
    def __init__(self, server: AuthServer):
        self.session = server.session
        self.endpoint = server.endpoint

    def uri(self, uri):
        return urljoin(self.endpoint, uri)

    def pods(self):
        _uri = "api/v2/free"
        uri = self.uri(_uri)

        res = self.session.get(uri)
        if res.status_code != 200:
            raise Exception("Incorrect status code.")

        pods = res.json()
        return [Pod(p, self) for p in pods]


class Pod:
    def __init__(self, data, registrar: Register):
        self.day: str = data['name']
        self.pod: str = data['pod']
        self.closed: bool = data['closed']

        self.available: int = data['available']
        self.taken: int = data['taken']

        self.date: date = date.fromisoformat(data['date'])
        self.description: str = data['description']

        self.registrar = registrar

    def __str__(self):
        return self.description

    def call(self, end):
        _uri = f"{end}/day/{self.day}/{self.pod}"
        uri = self.registrar.uri(_uri)

        res = self.registrar.session.get(uri)

        if res.status_code != 200:
            raise Exception("Incorrect status code.")

    def register(self):
        self.call("register")

    def deregister(self):
        self.call("deregister")