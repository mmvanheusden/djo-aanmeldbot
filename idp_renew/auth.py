from requests import Session
from urllib.parse import urlparse, parse_qs


class AuthUser:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def as_data(self):
        return {
            "username": self.username,
            "password": self.password
        }


class AuthServer:
    endpoint = "https://aanmelden.djoamersfoort.nl/"

    def __init__(self, user: AuthUser):
        self.user = user
        self.session = Session()

    def authenticate(self):
        # get redirected to proper endpoint
        req = self.session.get(self.endpoint, allow_redirects=True)

        if req.status_code != 200:
            raise Exception("Incorrect status code.")

        # save csrf and auth code
        self.csrf = self.session.cookies.get("csrftoken")
        self.auth_uri = req.url

        # make request data
        data = self.user.as_data()
        data["csrfmiddlewaretoken"] = self.csrf

        parsed_url = urlparse(self.auth_uri)
        parsed_qs = parse_qs(parsed_url.query)

        data["next"] = parsed_qs['next']

        # make authentication request
        req = self.session.post(self.auth_uri, data, allow_redirects=True)

        if req.status_code != 200:
            raise Exception("Incorrect status code.")

        if req.url == self.auth_uri:
            raise Exception("Invalid username or password.")