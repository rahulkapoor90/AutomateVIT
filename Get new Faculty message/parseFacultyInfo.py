from BeautifulSoup import BeautifulSoup
import mechanize
import smtplib
from StringIO import StringIO
from PIL import Image
from CaptchaParser import CaptchaParser
from pprint import pprint
import cookielib
import json
import textmyself
import sys, getopt
from clint.textui import colored, puts
from clint import arguments
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


import os
REGNO = ''
PASSWORD = ''
facultyInfo = []


def login():
    br = mechanize.Browser()
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    cj = cookielib.CookieJar()
    br.set_cookiejar(cj)
    response = br.open('https://academics.vit.ac.in/student/stud_login.asp')
    html = response.read()
    soup = BeautifulSoup(html)
    im = soup.find('img', id='imgCaptcha')
    image_response = br.open_novisit(im['src'])
    img = Image.open(StringIO(image_response.read()))
    parser = CaptchaParser()
    captcha = parser.getCaptcha(img)
    br.select_form('stud_login')
    br.form['regno'] = REGNO
    br.form['passwd'] = PASSWORD
    br.form['vrfcd'] = str(captcha)
    br.submit()
    if br.geturl() == 'https://academics.vit.ac.in/student/home.asp':
        puts(colored.yellow("LOGIN SUCCESSFUL"))
        return br
    else:
        return None


def parseFacultyPage(br, facultyID):
    if br is None:
        return None

    br.open('https://academics.vit.ac.in/student/stud_home.asp')
    response = br.open('https://academics.vit.ac.in/student/class_message_view.asp?sem=' + facultyID)
    html = response.read()
    soup = BeautifulSoup(html)
    tables = soup.findAll('table')

    # Extracting basic information of the faculty
    infoTable = tables[0].findAll('tr')
    name = infoTable[2].findAll('td')[0].text
    if (len(name) is 0):
        return None
    subject = infoTable[2].findAll('td')[1].text
    msg = infoTable[2].findAll('td')[2].text
    sent = infoTable[2].findAll('td')[3].text
    emailmsg = 'Subject: New VIT Email' + msg

    with open('output/WS.json') as data_file:
        data = json.load(data_file)
    if data["date"] == sent or data['message'] == msg:
        outputpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        if os.path.isdir(outputpath) is False:
         os.makedirs(outputpath)
        result = {'name': name, 'subject': subject, 'message': msg, 'date': sent}
        with open('output/' + str(facultyID) + '.json', 'w') as outfile:
          json.dump(result, outfile, indent=4)
        print('email already sent')
        return result

    else:
        outputpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        if os.path.isdir(outputpath) is False:
         os.makedirs(outputpath)
        result = {'name': name, 'subject': subject, 'message': msg, 'date': sent}
        with open('output/' + str(facultyID) + '.json', 'w') as outfile:
          json.dump(result, outfile, indent=4)
        you = "rahulkapoorbbps@outlook.com"
        me = "hootpile@gmail.com"
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.login('hootpile@gmail.com','rahulkapoor23')
        s.sendmail(me, you, emailmsg)
        s.quit()
        print('sent email and text message')
        textmyself.textmyself(msg)
        return result


def aggregate():
    br = login()
    result = parseFacultyPage(br, "WS")
    if result is not None:
        puts(colored.green("Parsed a new fucking Message"))
    else:
        puts(colored.red('There is nothing new available.'))


if __name__ == '__main__':
    args = arguments.Args()
    REGNO = args.get(0)
    PASSWORD = args.get(1)
    aggregate()
