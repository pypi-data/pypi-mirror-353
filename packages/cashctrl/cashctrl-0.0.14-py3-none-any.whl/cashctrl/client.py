from datetime import datetime
import logging, os, requests, csv
from requests.auth import HTTPBasicAuth
from cashctrl.limiter import Limiter
from .constants import VALID_LANGUAGES

# name the logger after the package
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Client:
    """
    Client is the main class to interact with the CashCtrl API. It sends all the requests and enables limiting, logging and so on.
    It also provides a convenient way to access all the resources via cc.account, cc.person, etc.
    """

    def __init__(self, api_key=None, organization=None, language=None, limit=True):
        if api_key is None or organization is None or language is None:
            from dotenv import load_dotenv
            entered_credentials = False
            if api_key is None:
                try:
                    load_dotenv()
                    api_key = os.getenv("API_KEY")
                    assert api_key is not None
                except:
                    # if script is running in a non-interactive environment, raise an error
                    if not os.isatty(0):
                        raise ValueError(f"No API key neither as parameter or in a .env file.")
                    else:
                        logging.error(f"No Api key provided neither as parameter or in a  .env file.")
                        api_key = input("API key: ")
                        entered_credentials = True
            if organization is None:
                try:
                    load_dotenv()
                    organization = os.getenv("ORGANIZATION")
                    assert organization is not None
                except:
                    if not os.isatty(0):
                        raise ValueError(f"No organization neither as parameter or in a .env file.")
                    else:
                        logging.error(f"No organization provided neither as parameter or in a .env file.")
                        organization = input("Organization: ")
                        entered_credentials = True
            if language is None:
                try:
                    load_dotenv()
                    language = os.getenv("LANGUAGE")
                    assert language is not None
                except:
                    logging.warning(f"No language provided neither as parameter or in a .env file, defaulting to 'en'.")
                    language = "en"
            if entered_credentials and not os.path.isfile(".env"):
                save = input("Save Credentials in .env file for future? (y/n): ")
                if save.lower() == "y":
                    with open(".env", "a") as f:
                        f.write(f"API_KEY={api_key}\n")
                        f.write(f"ORGANIZATION={organization}\n")
                        f.write(f"LANGUAGE={language}\n")

        language = language.lower()
        if language not in VALID_LANGUAGES:
            raise ValueError(f"Invalid language '{language}'. Valid options are {', '.join(self.VALID_LANGUAGES)}.")
        from .resource import account
        from .resource import person, order, article, customfield  # ,common,file,inventory,journal,meta,order,person,report,setting
        from .resource import order_category # todo: put into order
        self.api_key = api_key
        self.organization = organization
        self.default_language = language
        self.base_url = f"https://{organization}.cashctrl.com/api/v1/"
        self.account = account.Account(self)
        self.person = person.Person(self)
        self.article = article.Article(self)
        self.customfield = customfield.CustomField(self)
        self.order_category = order_category.OrderCategory(self)
        self.order = order.Order(self)
        self.limit = limit
        if self.limit:
            self.limiter = Limiter(self)

    def _make_request(self, method, endpoint, params=None, data=None, dump=False):
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        data = data or {}
        params['lang'] = self.default_language
        req = requests.Request(method, url, auth=HTTPBasicAuth(self.api_key, None), params=params, data=data)
        prepared_req = req.prepare()
        # Log the complete URL with parameters
        logging.debug(f"Making {method} request to {prepared_req.url}")
        try:
            with requests.Session() as s:
                response = s.send(prepared_req)
            response.raise_for_status()
            json_response = response.json()
            if not json_response.get('success', True):
                raise Exception(f"Validation errors: {json_response}")
            if self.limit: self.limiter.lazy_log_request(endpoint)
            result= json_response.get("data", json_response) #todo: breaking changes??
            return result

        except requests.RequestException as e:
            raise Exception(f"An error occurred: {str(e)}")

    def custom_request(self, endpoint, method="GET", params=None):
        # strip https://*.cashctrl.com/api/v1/" or "api/v1/" from the endpoint
        # todo: handle parameters in the url
        endpoint = endpoint.replace("https://*.cashctrl.com/api/v1/", "").replace("api/v1/", "").replace("/api/v1/", "")
        return self._make_request(method, endpoint, params)
