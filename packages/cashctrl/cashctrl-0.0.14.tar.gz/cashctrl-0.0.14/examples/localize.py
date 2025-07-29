import xmltodict
import cashctrl
from icecream import ic
cc=cashctrl.Client()
accounts=cc.account.list()
account=cc.account.read(accounts[0]["id"])
data=account["name"]
xml = xmltodict.parse(data)
localised_name=xml["values"][cc.default_language]
ic(localised_name)