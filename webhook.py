import requests
import config

url = "https://api.telegram.org/bot{token}/{method}".format(
    token=config.config.token,
    method="deleteWebhook"
)

data = {"url": "https://functions.yandexcloud.net/d4e8qve0v1p3scvs8vc1"}

r = requests.post(url, data=data)

# url = "https://api.telegram.org/bot{token}/{method}".format(
#     token=config.config.token,
#     method="setWebhook"
# )
#
# r = requests.post(url, data=data)
#
# url = "https://api.telegram.org/bot{token}/{method}".format(
#     token=config.config.token,
#     method="getWebhookinfo"
# )
#
# r = requests.post(url, data=data)

print(r.json())