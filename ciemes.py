#!/usr/bin/python3
# -*- coding: utf-8 -*-
# remake by rex4
import sys

## for people who don't bother reading the readme :/
if sys.version_info[0] < 3:
    print("\npython3 is needed to run CieMeS, Try \"python3 ciemes.py\" instead\n")
    sys.exit(2)

import os
import argparse
import json
import importlib

import ciemesdb.basic as ciemes # All the basic functions
import ciemesdb.core as core
import ciemesdb.createindex as createindex
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

parser = argparse.ArgumentParser(prog='ciemes.py',add_help=False)
parser.add_argument('-h', '--help', action="store_true")
parser.add_argument('-v', '--verbose', action="store_true")
parser.add_argument("--version", action="store_true")
parser.add_argument("--update", action="store_true")
parser.add_argument('-r', "--random-agent", action="store_true")
parser.add_argument('--user-agent')
parser.add_argument('--googlebot', action="store_true")
parser.add_argument('-u', '--url')
parser.add_argument('-l', '--list')
parser.add_argument('--clear-result', action='store_true')
parser.add_argument('--follow-redirect', action='store_true')
parser.add_argument('--no-redirect', action='store_true')
parser.add_argument('--batch', action="store_true")
parser.add_argument('-i', '--ignore-cms')
parser.add_argument('--strict-cms')
parser.add_argument('--skip-scanned', action="store_true")
args = parser.parse_args()

if args.clear_result:
    ciemes.clear_log()

if args.help:
    ciemes.help()

if args.verbose:
    ciemes.verbose = True

if args.skip_scanned:
    ciemes.skip_scanned = True

if args.follow_redirect:
    ciemes.redirect_conf = '1'

if args.no_redirect:
    ciemes.redirect_conf = '2'

if args.update:
    ciemes.update()

if args.batch:
    #print('Batch true')
    ciemes.batch_mode = True
    print(ciemes.batch_mode)

if args.version:
    print('\n\n')
    ciemes.info("CieMeS Version: " + ciemes.ciemes_version)
    ciemes.bye()

if args.ignore_cms:
    ciemes.ignore_cms = args.ignore_cms.split(',')
    for acms in ciemes.ignore_cms:
        ciemes.warning('Ignoring CMS: ' + acms)

if args.strict_cms:
    ciemes.strict_cms = args.strict_cms.split(',')
    ciemes.warning('Checking target against CMSes: ' + args.strict_cms)

if args.user_agent is not None:
    cua = args.user_agent
elif args.random_agent is not None:
    cua = ciemes.randomua('random')
else:
    cua = None

if args.googlebot:
    cua = 'Googlebot/2.1 (+http://www.google.com/bot.html)'

# Update report index
index_status = createindex.init(ciemes.access_directory)
if index_status[0] != '1':
    # might be too extreme
    # ciemes.handle_quit()
    if not ciemes.batch_mode:
        input('There was an error while creating result index! Some features might not work as intended. Press [ENTER] to continue:')

if args.url is not None:
    s = args.url
    target = ciemes.process_url(s)
    if target != '0':
        if cua == None:
            cua = ciemes.randomua()
        core.main_proc(target,cua)
        ciemes.handle_quit()

elif args.list is not None:
    sites = args.list
    ciemes.clearscreen()
    ciemes.banner("CMS Detection And Scanner")
    sites_list = []
    try:
        ot = open(sites, 'r')
        file_contents = ot.read().replace('\n','')
        sites_list = file_contents.split(',')
    except FileNotFoundError:
        ciemes.error('Invalid path! CieMeS is quitting')
        ciemes.bye()
    if sites_list != []:
        if cua == None:
            cua = ciemes.randomua()
        for s in sites_list:
            s = s.replace(' ', '')
            target = ciemes.process_url(s)
            if target != '0':
                core.main_proc(target,cua)
                ciemes.handle_quit(False)
                if not ciemes.batch_mode:
                    input('\n\n\tPress ' + ciemes.bold + ciemes.fgreen + '[ENTER]' + ciemes.cln + ' to continue') # maybe a fix? idk
            else:
                print('\n')
                ciemes.warning('Invalid URL: ' + ciemes.bold + s + ciemes.cln + ' Skipping to next')
        print('\n')
        ciemes.result('Finished Scanning all targets.. result has been saved under respective target directories','')
    else:
        ciemes.error("No url provided... CieMeS is exiting")
    ciemes.bye()

################################
###      THE MAIN MENU       ###
################################
ciemes.clearscreen()
ciemes.banner("Tip: check the help menu for more information")
print (" Input    Description")
print ("=======  ==============================")
print ("  (1)    CMS detection and scan")
print ("  (2)    Scan Multiple Sites")
print ("  (3)    Bruteforce CMS")
print ("  (U)    Update CieMeS")
print ("  (R)    Rebuild Cache")
print ("  (0)    Exit CieMeS :( \n")

selone = input("Enter Your Desired Option: ").lower()
if selone == 'r':
    ciemes.update_brute_cache()
elif selone == 'u':
    ciemes.update()
elif selone == '0':
    ciemes.bye()

elif selone == "1":
    # There goes the cms detection thingy
    ciemes.clearscreen()
    ciemes.banner("CMS Detection And Deep Scan")
    site = ciemes.targetinp("") # Get The User input
    if cua == None:
        cua = ciemes.randomua()
    core.main_proc(site,cua)
    ciemes.handle_quit()

elif selone == '2':
    ciemes.clearscreen()
    ciemes.banner("CMS Detection And Deep Scan")
    sites_list = []
    sites = input('Enter comma separated urls(http://1.com,https://2.org) or enter path of file containing URLs (comma separated): ')
    if 'http' not in sites or '://' not in sites:
        ciemes.info('Treating input as path')
        try:
            ot = open(sites, 'r')
            file_contents = ot.read().replace('\n','')
            sites_list = file_contents.split(',')
        except FileNotFoundError:
            ciemes.error('Invalid path! CMSeeK is quitting')
            ciemes.bye()
    else:
        ciemes.info('Treating input as URL list')
        sites_list = sites.split(',')
    if sites_list != []:
        if cua == None:
            cua = ciemes.randomua()
        for s in sites_list:
            s = s.replace(' ', '')
            target = ciemes.process_url(s)
            if target != '0':
                core.main_proc(target,cua)
                ciemes.handle_quit(False)
                if not ciemes.batch_mode:
                    input('\n\n\tPress ' + ciemes.bold + ciemes.fgreen + '[ENTER]' + ciemes.cln + ' to continue') # maybe a fix? idk
            else:
                print('\n')
                ciemes.warning('Invalid URL: ' + ciemes.bold + s + ciemes.cln + ' Skipping to next')
        print('\n')
        ciemes.result('Finished Scanning all targets.. result has been saved under respective target directories','')
    else:
        ciemes.error("No url provided... CMSeeK is exiting")
    ciemes.bye()

elif selone == "3":
    ciemes.clearscreen()
    ciemes.banner("CMS Bruteforce Module")
    ## I think this is a modular approch
    brute_dir = os.path.join(ciemes.cmseek_dir, 'cmsbrute')
    brute_cache = os.path.join(brute_dir, 'cache.json')
    if not os.path.isdir(brute_dir):
        ciemes.error("bruteforce directory missing! did you mess up with it? Anyways CMSeek is exiting")
        ciemes.bye()
    else:
        print ("[#] List of CMSs: \n")
        print (ciemes.bold)
        read_cache = open(brute_cache, 'r')
        b_cache = read_cache.read()
        cache = json.loads(b_cache)
        brute_list = []
        for c in cache:
            brute_list.append(c)
        brute_list = sorted(brute_list)
        for i,x in enumerate(brute_list):
            n = x
            mod = "cmsbrute." + x
            exec(n + " = importlib.import_module(mod)")
            print('['+ str(i) +'] ' + cache[x])
        print(ciemes.cln + '\n')
        cmstobrute = input('Select CMS: ')
        try:
            kek = brute_list[int(cmstobrute)]
            print(kek)
            cms_brute = getattr(locals().get(kek), 'start')
            cms_brute()
        except IndexError:
            ciemes.error('Invalid Input!')
else:
    ciemes.error("Invalid Input!")
    ciemes.bye()
