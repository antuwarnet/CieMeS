#!/usr/bin/python3
# -*- coding: utf-8 -*-
# This is a part of CieMeS, check the LICENSE file for more information
# Rex4 - Cantix Crew

import ciemesdb.basic as ciemes
# I know there is no reason at all to create a separate module for this.. there's something that's going to be added here so.. trust me!
def start(source):
    # print(source)
    if 'Joomla! Debug Console' in source or 'xdebug.org/docs/all_settings' in source:
        ciemes.success('Debug mode on!')
        return '1'
    else:
        return '0'
