#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This is a part of CieMeS, check the LICENSE file for more information
# Rex4 - Cantix Crew


import sys
import os
import http.client
import urllib.request
import json
import importlib
from datetime import datetime
import time

import VersionDetect.detect as version_detect # Version detection
import deepscans.core as advanced # Deep scan and Version Detection functions
import ciemesdb.basic as ciemes # All the basic functions
import ciemesdb.sc as source # Contains function to detect cms from source code
import ciemesdb.header as header # Contains function to detect CMS from gathered http headers
import ciemesdb.cmss as cmsdb # Contains basic info about the CMSs
import ciemesdb.robots as robots
import ciemesdb.generator as generator
import ciemesdb.result as result

def main_proc(site,cua):

    # Check for skip_scanned
    if ciemes.skip_scanned:
        for csite in ciemes.report_index['results'][0]:
            if site == csite and ciemes.report_index['results'][0][site]['cms_id'] != '':
                ciemes.warning('Skipping {0} as it was previously scanned!'.format(ciemes.red + site + ciemes.cln))
                return

    ciemes.clearscreen()
    ciemes.banner("CMS Detection And Deep Scan")
    ciemes.info("Scanning Site: " + site)
    ciemes.statement("User Agent: " + cua)
    ciemes.statement("Collecting Headers and Page Source for Analysis")
    init_source = ciemes.getsource(site, cua)
    if init_source[0] != '1':
        ciemes.error("Aborting CMSeek! Couldn't connect to site \n    Error: %s" % init_source[1])
        return
    else:
        scode = init_source[1]
        headers = init_source[2]
        if site != init_source[3] and site + '/' != init_source[3]:
            if ciemes.redirect_conf == '0':
                ciemes.info('Target redirected to: ' + ciemes.bold + ciemes.fgreen + init_source[3] + ciemes.cln)
                if not ciemes.batch_mode:
                    follow_redir = input('[#] Set ' + ciemes.bold + ciemes.fgreen + init_source[3] + ciemes.cln + ' as target? (y/n): ')
                else:
                    follow_redir = 'y'
                if follow_redir.lower() == 'y':
                    site = init_source[3]
                    ciemes.statement("Reinitiating Headers and Page Source for Analysis")
                    tmp_req = ciemes.getsource(site, cua)
                    scode = tmp_req[1]
                    headers = tmp_req[2]
            elif ciemes.redirect_conf == '1':
                site = init_source[3]
                ciemes.info("Followed redirect, New target: " + ciemes.bold + ciemes.fgreen + init_source[3] + ciemes.cln)
                ciemes.statement("Reinitiating Headers and Page Source for Analysis")
                tmp_req = ciemes.getsource(site, cua)
                scode = tmp_req[1]
                headers = tmp_req[2]
            else:
                ciemes.statement("Skipping redirect to " + ciemes.bold + ciemes.red + init_source[3] + ciemes.cln)
    if scode == '':
        # silly little check thought it'd come handy
        ciemes.error('Aborting detection, source code empty')
        return

    ciemes.statement("Detection Started")

    ## init variables
    cms = '' # the cms id if detected
    cms_detected = '0' # self explanotory
    detection_method = '' # ^
    ga = '0' # is generator available
    ga_content = '' # Generator content

    ## Parse generator meta tag
    parse_generator = generator.parse(scode)
    ga = parse_generator[0]
    ga_content = parse_generator[1]

    ciemes.statement("Using headers to detect CMS (Stage 1 of 4)")
    header_detection = header.check(headers)

    if header_detection[0] == '1':
        detection_method = 'header'
        cms = header_detection[1]
        cms_detected = '1'

    if cms_detected == '0':
        if ga == '1':
            # cms detection via generator
            ciemes.statement("Using Generator meta tag to detect CMS (Stage 2 of 4)")
            gen_detection = generator.scan(ga_content)
            if gen_detection[0] == '1':
                detection_method = 'generator'
                cms = gen_detection[1]
                cms_detected = '1'
        else:
            ciemes.statement('Skipping stage 2 of 4: No Generator meta tag found')

    if cms_detected == '0':
        # Check cms using source code
        ciemes.statement("Using source code to detect CMS (Stage 3 of 4)")
        source_check = source.check(scode, site)
        if source_check[0] == '1':
            detection_method = 'source'
            cms = source_check[1]
            cms_detected = '1'

    if cms_detected == '0':
        # Check cms using robots.txt
        ciemes.statement("Using robots.txt to detect CMS (Stage 4 of 4)")
        robots_check = robots.check(site, cua)
        if robots_check[0] == '1':
            detection_method = 'robots'
            cms = robots_check[1]
            cms_detected = '1'

    if cms_detected == '1':
        ciemes.success('CMS Detected, CMS ID: ' + ciemes.bold + ciemes.fgreen + cms + ciemes.cln + ', Detection method: ' + ciemes.bold + ciemes.lblue + detection_method + ciemes.cln)
        ciemes.update_log('detection_param', detection_method)
        ciemes.update_log('cms_id', cms) # update log
        ciemes.statement('Getting CMS info from database') # freaking typo
        cms_info = getattr(cmsdb, cms)
        if cms_info['deeps'] == '1':
            # ciemes.success('Starting ' + ciemes.bold + cms_info['name'] + ' deep scan' + ciemes.cln)
            advanced.start(cms, site, cua, ga, scode, ga_content, detection_method, headers)
            return
        elif cms_info['vd'] == '1':
            ciemes.success('Starting version detection')
            cms_version = '0' # Failsafe measure
            cms_version = version_detect.start(cms, site, cua, ga, scode, ga_content, headers)
            ciemes.clearscreen()
            ciemes.banner("CMS Scan Results")
            result.target(site)
            result.cms(cms_info['name'],cms_version,cms_info['url'])
            ciemes.update_log('cms_name', cms_info['name']) # update log
            if cms_version != '0' and cms_version != None:
                ciemes.update_log('cms_version', cms_version) # update log
            ciemes.update_log('cms_url', cms_info['url']) # update log
            comptime = round(time.time() - ciemes.cstart, 2)
            log_file = os.path.join(ciemes.log_dir, 'cms.json')
            result.end(str(ciemes.total_requests), str(comptime), log_file)
            '''
            ciemes.result('Target: ', site)
            ciemes.result("Detected CMS: ", cms_info['name'])
            ciemes.update_log('cms_name', cms_info['name']) # update log
            if cms_version != '0' and cms_version != None:
                ciemes.result("CMS Version: ", cms_version)
                ciemes.update_log('cms_version', cms_version) # update log
            ciemes.result("CMS URL: ", cms_info['url'])
            ciemes.update_log('cms_url', cms_info['url']) # update log
            '''
            return
        else:
            # nor version detect neither DeepScan available
            ciemes.clearscreen()
            ciemes.banner("CMS Scan Results")
            result.target(site)
            result.cms(cms_info['name'],'0',cms_info['url'])
            ciemes.update_log('cms_name', cms_info['name']) # update log
            ciemes.update_log('cms_url', cms_info['url']) # update log
            comptime = round(time.time() - ciemes.cstart, 2)
            log_file = os.path.join(ciemes.log_dir, 'cms.json')
            result.end(str(ciemes.total_requests), str(comptime), log_file)
            '''
            ciemes.result('Target: ', site)
            ciemes.result("Detected CMS: ", cms_info['name'])
            ciemes.update_log('cms_name', cms_info['name']) # update log
            ciemes.result("CMS URL: ", cms_info['url'])
            ciemes.update_log('cms_url', cms_info['url']) # update log
            '''
            return
    else:
        print('\n')
        ciemes.error('CMS Detection failed, if you know the cms please help me improve CMSeeK by reporting the cms along with the target by creating an issue')
        print('''
{2}Create issue:{3} https://github.com/Tuhinshubhra/CMSeeK/issues/new

{4}Title:{5} [SUGGESTION] CMS detction failed!
{6}Content:{7}
    - CMSeeK Version: {0}
    - Target: {1}
    - Probable CMS: <name and/or cms url>

N.B: Create issue only if you are sure, please avoid spamming!
        '''.format(ciemes.ciemes_version, site, ciemes.bold, ciemes.cln, ciemes.bold, ciemes.cln, ciemes.bold, cmseek.cln))
        return
    return
