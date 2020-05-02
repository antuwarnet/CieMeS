#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This is a part of CieMeS, check the LICENSE file for more information
# Rex4 - Cantix Crew

# This is mostly for falsepositive detection

import ciemesdb.basic as ciemes ## Good old module
import VersionDetect.umbraco as umbraco_version_detect
import cmseekdb.result as sresult
import time
import os
import re

def falsepositive():
    ciemes.error('Detection was false positive! CMSeeK is quitting!')
    ciemes.success('Run CMSeeK with {0}{1}{2} argument next time'.format(ciemes.fgreen, '--ignore-cms umbraco', ciemes.cln))
    #ciemes.handle_quit()
    return

def start(id, url, ua, ga, source, detection_method, headers):
    if id == 'umbraco':
        cms_version = 0
        ciemes.statement('Starting Umbraco DeepScan')
        if detection_method == 'source':
            # detect if it's false positive
            umbraco_url = url + '/umbraco'
            test_src = ciemes.getsource(umbraco_url, ua)

            if test_src[0] == '1':
                # okay we got the source let's test it
                if 'var Umbraco' in test_src[1]:
                    # Umbraco Detected!
                    # Let's get version
                    cms_version = umbraco_version_detect.start(headers, url, ua, test_src[1])
                else:
                    falsepositive()
            else:
                falsepositive()
        else:
            # detection method was different so we are good and no need to check for false positive i guess
            cms_version = umbraco_version_detect.start(headers, url, ua)

        ciemes.clearscreen()
        ciemes.banner("CMS Scan Results")
        sresult.target(url)
        sresult.cms('Umbraco',cms_version,'https://umbraco.com')
        ciemes.update_log('cms_name', 'Umbraco') # update log
        if cms_version != '0' and cms_version != None:
            ciemes.update_log('cms_version', cms_version) # update log
        ciemes.update_log('cms_url', 'https://umbraco.com') # update log
        comptime = round(time.time() - ciemes.cstart, 2)
        log_file = os.path.join(ciemes.log_dir, 'cms.json')
        sresult.end(str(ciemes.total_requests), str(comptime), log_file)
        return
