#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This is a part of CieMeS, check the LICENSE file for more information
# Rex4 - Cantix Crew

import ciemesdb.basic as ciemes

def start(url,ua):
    reg_url = url + '/index.php?option=com_users&view=registration'
    reg_source = ciemes.getsource(reg_url, ua)
    if reg_source[0] == '1':
        if 'registration.register' in reg_source[1] or 'jform_password2' in reg_source[1] or 'jform_email2' in reg_source[1]:
            ciemes.success('User registration open, ' + ciemes.bold + reg_url + ciemes.cln)
            return ['1', reg_url]
        else:
            return ['0', '']
    else:
        return ['0', '']
