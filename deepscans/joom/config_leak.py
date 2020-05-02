#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This is a part of CieMeS, check the LICENSE file for more information
# Rex4 - Cantix Crew

import threading
import ciemesdb.basic as ciemes

joom_conf_found = 0
joom_confs = []

def check_config(url,file,ua):
    global joom_conf_found, joom_confs
    file_check = ciemes.check_url(url + '/' + file, ua)
    if file_check == '1':
        ciemes.success('Potential configuration file found: ' + ciemes.bold + ciemes.fgreen + file + ciemes.cln)
        joom_conf_found += 1
        joom_confs.append(file)

def start(url, ua):
    config_files = ['configuration.php~','configuration.php.new','configuration.php.new~','configuration.php.old','configuration.php.old~','configuration.bak','configuration.php.bak','configuration.php.bkp','configuration.txt','configuration.php.txt','configuration - Copy.php','configuration.php.swo','configuration.php_bak','configuration.orig','configuration.php.save','configuration.php.original','configuration.php.swp','configuration.save','.configuration.php.swp','configuration.php1','configuration.php2','configuration.php3','configuration.php4','configuration.php4','configuration.php6','configuration.php7','configuration.phtml','configuration.php-dist']

    threads = [threading.Thread(target=check_config, args=(url, file ,ua)) for file in config_files]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    global joom_conf_found, joom_confs
    return [joom_conf_found, joom_confs]
