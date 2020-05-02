#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This is a part of CieMeS, check the LICENSE file for more information
# Rex4 - Cantix Crew

# Joomla DeepScan
# Rev 1
# Props to joomscan.. big time! https://github.com/rezasp/joomscan

import os
import ciemesdb.basic as cmseek
import VersionDetect.joom as version_detect
import deepscans.joom.backups as backup_finder
import deepscans.joom.config_leak as config_check
import deepscans.joom.core_vuln as core_vuln
import deepscans.joom.admin_finder as admin_finder
import deepscans.joom.check_debug as check_debug
import deepscans.joom.dir_list as dir_list
import deepscans.joom.check_reg as user_registration

def start(id, url, ua, ga, source):

    # Remove / from url
    if url.endswith("/"):
        url = url[:-1]

    # init variables
    vuln_detection = '0'
    vuln_count = 0
    joom_vulns = []

    # Version Detection
    version = version_detect.start(id, url, ua, ga, source)

    # Detecting joomla core vulnerabilities
    jcv = core_vuln.start(version)
    vuln_detection = jcv[0]
    vuln_count = jcv[1]
    joom_vulns = jcv[2]

    # README.txt
    readmesrc = ciemes.getsource(url + '/README.txt', ua)
    if readmesrc[0] != '1': ## something went wrong while getting the source codes
        ciemes.statement("Couldn't get readme file's source code most likely it's not present")
        readmefile = '0'
    elif 'This is a Joomla!' in readmesrc[1]:
        ciemes.info('README.txt file found')
        readmefile = '1' # Readme file present
    else:
        readmefile = '2' # Readme file found but most likely it's not of joomla

    # Debug Mode
    ciemes.info('Checking debug mode status')
    debug_mode = check_debug.start(source)

    # Check user registration status
    ciemes.statement('Checking if user registration is enabled')
    registration = user_registration.start(url,ua)

    # Find admin url
    ciemes.info('Locating admin url')
    admin = admin_finder.start(url,ua)

    # Backups check
    ciemes.info('Checking for common Backups')
    backups = backup_finder.start(url,ua)

    # Check Potential configuration file leak
    ciemes.info('Looking for potential config leak')
    configs = config_check.start(url,ua)

    # Checking for directory listing
    ciemes.statement('Checking for directory listing')
    directories = dir_list.start(url, ua)

    ### THE RESULTS START FROM HERE

    ciemes.clearscreen()
    ciemes.banner("Deep Scan Results")
    ciemes.result('Target: ',url)
    ciemes.result("Detected CMS: ", 'Joomla')
    ciemes.update_log('cms_name','joomla') # update log
    ciemes.result("CMS URL: ", "https://joomla.org")
    ciemes.update_log('cms_url', "https://joomla.org") # update log

    if version != '0':
        ciemes.result("Joomla Version: ", version)
        ciemes.update_log('joomla_version', version)

    if registration[0] == '1':
        ciemes.result('User registration enabled: ', registration[1])
        ciemes.update_log('user_registration_url', registration[1])

    if debug_mode =='1':
        ciemes.result('Debug mode enabled', '')
        ciemes.update_log('joomla_debug_mode', 'enabled')
    else:
        ciemes.update_log('joomla_debug_mode', 'disabled')

    if readmefile == '1':
        ciemes.result('Readme file: ', url + '/README.txt')
        ciemes.update_log('joomla_readme_file', url + '/README.txt')

    if admin[0] > 0:
        ciemes.result('Admin URL: ', url + admin[1][0])
        admin_log = ''
        for adm in admin[1]:
            admin_log += url + '/' + adm + ','
            # print(ciemes.bold + ciemes.fgreen + "   [B] " + ciemes.cln + url + '/' + adm)
        ciemes.update_log('joomla_backup_files', admin_log)
        print('\n')

    if directories[0] > 0:
        ciemes.result('Open directories: ', str(directories[0]))
        ciemes.success('Open directory url: ')
        dirs = ''
        for dir in directories[1]:
            dirs += url + '/' + dir + ','
            print(ciemes.bold + ciemes.fgreen + "   [>] " + ciemes.cln + url + dir)
        ciemes.update_log('directory_listing', dirs)
        print('\n')

    if backups[0] > 0:
        ciemes.result('Found potential backup file: ', str(backups[0]))
        ciemes.success('Backup URLs: ')
        bkup_log = []
        for backup in backups[1]:
            bkup_log.append(url + '/' + backup)
            print(ciemes.bold + ciemes.fgreen + "   [B] " + ciemes.cln + url + '/' + backup)
        ciemes.update_log('joomla_backup_files', bkup_log, False)
        print('\n')

    if configs[0] > 0:
        ciemes.result('Found potential Config file: ', str(configs[0]))
        ciemes.success('Config URLs: ')
        conf_log = ''
        for config in configs[1]:
            conf_log += url + '/' + config + ','
            print(ciemes.bold + ciemes.fgreen + "   [c] " + ciemes.cln + url + '/' + config)
        ciemes.update_log('joomla_config_files', conf_log)
        print('\n')

    if vuln_detection == '1' and vuln_count > 0:
        ciemes.result('Total joomla core vulnerabilities: ', str(vuln_count))
        ciemes.update_log("vulnerabilities_count", vuln_count)
        joomla_vulns_to_log = []
        ciemes.info('Vulnerabilities found: \n')
        for vuln in joom_vulns:
            # prepare the vuln details to be added to the log
            _vulnName = vuln.split('\\n')[0]
            _vulnRefs = []
            # TODO: try not to use a for loop here.
            for _index, _vr in enumerate(vuln.split('\\n')):
                if _index != 0:
                    _vulnRefs.append(_vr)
            
            joomla_vulns_to_log.append({"name": _vulnName, "references": _vulnRefs})
            vuln = vuln.replace('\\n', ciemes.cln + '\n    ')
            print(ciemes.bold + ciemes.red + '[v] ' + vuln)
            print('\n')
        ciemes.update_log("vulnerabilities", joomla_vulns_to_log, False)
    elif vuln_detection == '2':
        ciemes.update_log("vulnerabilities_count", 0)
        ciemes.warning('Couldn\'t find core vulnerabilities, No VERSION detected')
    elif vuln_detection == '3':
        ciemes.update_log("vulnerabilities_count", 0)
        ciemes.error('Core vulnerability database not found!')
    else:
        ciemes.update_log("vulnerabilities_count", 0)
        ciemes.warning('No core vulnerabilities detected!')
