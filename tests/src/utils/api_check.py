import http
import requests
from requests.exceptions import ConnectionError
import backoff


class ApiCheck:

    @backoff.on_predicate(backoff.fibo, max_value=10)
    @backoff.on_exception(backoff.expo, ConnectionError)
    def ping(self, url) -> bool:
        response = requests.get(url)
        if response.status_code == http.HTTPStatus.OK:
            return True
        return False


ApiCheck().ping("http://auth:5000/v1/health_check")
ApiCheck().ping("http://billing:8000/api/v1/health_check")
