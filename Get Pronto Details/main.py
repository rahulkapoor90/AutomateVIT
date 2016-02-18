import urllib2
import cookielib
import urllib
import os
import json
import re
import textmyself
from datetime import datetime
import dateutil.relativedelta

from BeautifulSoup import BeautifulSoup
from clint.arguments import Args
from clint.textui import prompt, puts, colored, indent


BASE_URL = "http://115.248.50.60"


def getcyclestartdate(planstart):
    today = datetime.now()
    month_ago = today - dateutil.relativedelta.relativedelta(months=1)
    if planstart.day > today.day:
        return {
            "dd": planstart.day,
            "mm": month_ago.month - 1,
            "yy": month_ago.year
        }
    else:
        return {
            "dd": planstart.day,
            "mm": today.month - 1,
            "yy": today.year
        }


def logintopronto(username, password, debug):
    params = urllib.urlencode({
        'loginUserId': username,
        'authType': 'Pronto',
        'loginPassword': password,
        'submit': 'Login'
    })

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
    urllib2.install_opener(opener)
    puts(colored.white("Contacting ProntoNetworks..."))

    if debug:
        if not os.path.exists('debug/'):
            os.makedirs('debug/')

    with indent(5, quote=">"):
        puts(colored.yellow("Fetching site"))
    mainreq = urllib2.Request(BASE_URL + '/registration/Main.jsp?wispId=1&nasId=00:15:17:c8:09:b1')
    mainres = urllib2.urlopen(mainreq)

    if debug:
        with open('debug/main.txt', 'wb') as f:
            f.write(mainres.read())
            f.close()
            with indent(5, quote=colored.white("DEBUG:")):
                puts(colored.red("logged /registration/Main.jsp response"))

    with indent(5, quote=">"):
        puts(colored.yellow("Sending credentials"))
    loginReq = urllib2.Request(BASE_URL + '/registration/chooseAuth.do', params)
    loginRes = urllib2.urlopen(loginReq)

    if debug:
        with open('debug/login.txt', 'wb') as f:
            f.write(loginRes.read())
            f.close()
            with indent(5, quote=colored.white("DEBUG:")):
                puts(colored.red("logged /registration/chooseAuth.do response"))

    with indent(5, quote=">"):
        puts(colored.yellow("Checking plan"))
    planreq = urllib2.Request(BASE_URL + '/registration/main.do?content_key=%2FSelectedPlan.jsp')
    planres = urllib2.urlopen(planreq)

    planSoup = BeautifulSoup(planres.read())
    data = planSoup.findAll('td', attrs={
        'class': 'formFieldRight',
        'colspan': '2'
    })
    planDetails = []
    for i in range(0, len(data) - 1):
        kids = data[i].parent.findAll('td')
        planDetails.append(str(kids[1].text))

    if debug:
        with open('debug/plan.txt', 'wb') as f:
            f.write(loginRes.read())
            f.close()
            with indent(5, quote=colored.white("DEBUG:")):
                puts(colored.red("logged /registration/main.do?content_key=%2FSelectedPlan.jsp response"))

    sedate = datetime.strptime(planDetails[2], "%m/%d/%Y %H:%M:%S")
    # enddate = datetime.strptime(planDetails[3], "%m/%d/%Y %H:%M:%S")

    cycleStart = getcyclestartdate(sedate)

    historyparams = urllib.urlencode({
        "location": "allLocations",
        "parameter": "custom",
        "customStartMonth": cycleStart['mm'],
        "customStartDay": cycleStart['dd'],
        "customStartYear": cycleStart['yy'],
        "customEndMonth": 04,
        "customEndDay": 01,
        "customEndYear": 2016,  # Lazy, so hardcoding end year.
        "button": "View"
    })

    with indent(5, quote=">"):
        puts(colored.yellow("Accessing history"))
    historyreq = urllib2.Request(BASE_URL + '/registration/customerSessionHistory.do', historyparams)
    histories = urllib2.urlopen(historyreq)

    html = histories.read()
    if debug:
        with open('debug/history.txt', 'wb') as f:
            f.write(html)
            f.close()
            with indent(5, quote=colored.white("DEBUG:")):
                puts(colored.red("logged /registration/customerSessionHistory.do response"))

    with indent(5, quote=">"):
        puts(colored.yellow("Parsing data"))
    historysoup = BeautifulSoup(html)
    table = historysoup.find('td', attrs={
        "colspan": "3",
        "class": "subTextRight"
    }).parent
    tds = table.findAll('td')

    print "-" * 40
    puts(colored.cyan(" " * 14 + "Plan Details"))
    print "-" * 40
    puts(colored.magenta("Data Limit: ") + planDetails[0])
    puts(colored.magenta("Start Date: ") + planDetails[2])
    puts(colored.magenta("End Date: ") + planDetails[3])
    print "-" * 40

    print "-" * 40
    puts(colored.cyan(" " * 17 + "Usage"))
    print "-" * 40
    puts(colored.magenta("Total Time: ") + tds[1].text)
    puts(colored.magenta("Uploaded: ") + tds[2].text)
    puts(colored.magenta("Downloaded: ") + tds[3].text)
    puts(colored.magenta("Total Data: ") + tds[4].text)
    sd = str(tds[4].text)
    # print(float(filter(str.isdigit, sd)))
    x = map(float, re.findall(r'[+-]?[0-9.]+', sd))

    if x[0] > 3:
        textmyself.textmyself("Rahul, you have used more than 3GB. STAY SAFE!")
    elif x[0] > 7:
        textmyself.textmyself("Hey Rahul, Data is very low, come on!")
    elif x[0] > 8:
        textmyself.textmyself("Rahul, you asshole control yourself.")
    elif x[0] < 3:
        textmyself.textmyself("GO PORN GO!")

    print "-" * 40


if __name__ == '__main__':
    print "-" * 40
    puts(colored.white(" " * 15 + "ProntoUsage"))
    print "-" * 40
    debug = False
    args = Args().grouped
    if '--debug' in args.keys():
        debug = True
    if '--delete' in args.keys():
        try:
            os.remove('cred.json')
        except OSError:
            pass

    if os.path.isfile('cred.json'):
        with open('cred.json', 'r') as f:
            data = json.load(f)
            username = data['username']
            password = data['password']

    else:
        saved = False
        if '--debug' in args.keys():
            debug = True
        if '-u' in args.keys():
            username = args['-u'][0]
        else:
            username = prompt.query("username:")

        if '-p' in args.keys():
            password = args['-p'][0]
        else:
            password = prompt.query("password:")
        with open('cred.json', 'w') as f:
            f.write(json.dumps({
                'username': username,
                'password': password
            }, ensure_ascii=False))
            f.close()

    logintopronto(username, password, debug)
