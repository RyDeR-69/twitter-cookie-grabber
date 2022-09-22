# twitter-cookie-grabber

<h2>Instalation</h2>

`pip install --upgrade pip`<br>
`pip install -r requirements.txt`<br>
`playwright install`<br>

<h2>Data files</h2>

`proxy.txt` - Proxy in format `http://user:pass@ip:port`. Optional. Delete if not using proxy.<br>
`twitter_pass.txt` - Twitter accounts in format user:pass:2fa.<br>
**2fa - account email / phone number. Optional.**<br>
`ua_list.txt` - List of user-agents used when cookie grab, you can add or let default value.


<h2>How to use</h2>

`python main.py` - Grab cookies from `data/twitter_pass.txt` to `cookies/{account_name}.json`<br>
`python format_cookies.py` - Format cookies from json to string in `formated.txt`<br>
