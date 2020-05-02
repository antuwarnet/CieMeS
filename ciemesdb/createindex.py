#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This is a part of CieMeS, check the LICENSE file for more information
# Rex4 - Cantix Crew

import os
import json
import datetime
import ciemesdb.basic as ciemes
import logging, traceback

def init(cmseek_dir, report_dir=""):
    '''
    Creates/Updates result index
    Needed Parameters:
    cmseek_dir = CMSeeK directory / access_directory
    report_dir = path to report directory leave empty if default
    '''
    # Create a json list of all the sites scanned and save it to <cmseek_dir>/reports.json
    ciemes.info('Updating CMSeeK result index...')
    if os.path.isdir(cmseek_dir):
        index_file = os.path.join(cmseek_dir, 'reports.json')
        if report_dir == "":
            report_dir = os.path.join(cmseek_dir, 'Result')
        if os.path.isdir(report_dir):
            result_index = {}
            result_dirs = os.listdir(report_dir)
            for result_dir in result_dirs:
                scan_file = os.path.join(report_dir, result_dir, 'cms.json')
                if os.path.isfile(scan_file):
                    try:
                        with open(scan_file, 'r', encoding='utf8') as sf:
                            scan_content = json.loads(sf.read())
                        scan_url = scan_content['url']
                        result_index[scan_url] = {"cms_id": scan_content['cms_id'],"date": scan_content['last_scanned'],"report":scan_file}
                    except Exception as e:
                        logging.error(traceback.format_exc())
                        ciemes.statement('Skipping invalid CMSeeK result: ' + scan_file)
            # Write index
            result_index = {"last_updated":str(datetime.datetime.now()), "results":[result_index]}
            inf = open(index_file, 'w+')
            inf.write(json.dumps(result_index, sort_keys=False, indent=4))
            inf.close()
            ciemes.success('Report index updated successfully!')
            ciemes.report_index = result_index
            return ['1', 'Report index updated successfully!']

        else:
            ciemes.error('Result directory does not exist!')
            return [0, 'Result directory does not exist']

    else:
        ciemes.error('Invalid CMSeeK directory passed!')
        return [0, 'CMSeeK directory does not exist']
