import cashctrl
from icecream import ic
import time

cc = cashctrl.Client()
accounts = cc.account.list()
print(f"Found {len(accounts)} accounts")
count = 0
for account in accounts:
    ic(cc.account.read(account['id']))
    if account['endAmount'] == 0:
        try:
            print(f"Disabling account {account['id']} {account['name']}")
            cc.account.update(account, isInactive=True)
            count += 1
        except Exception as e:
            print(f"Error disabling account {account['id']}: {e}")
    time.sleep(0.05)  # To avoid hitting the API rate limit
print(f"Disabled {count} accounts")
