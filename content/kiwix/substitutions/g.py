#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This is a globals module, imported by all other modules

import sys
# Get the IIAB variables
sys.path.append('/etc/iiab/')
from iiab_env import get_iiab_env
DOC_ROOT = get_iiab_env("WWWROOT")

MENU_FILES = DOC_ROOT + "/js-menu/menu-files"
MENU_DEFS = MENU_FILES + "/menu-defs"
ICON_BASE = MENU_FILES + "/images"
ASSET_BASE = DOC_ROOT + "/common/assets"
KIWIX_CAT = ASSET_BASE + '/kiwix_catalog.json'
DOWNLOADED_ZIMS = ASSET_BASE + '/zim_version_idx.json'
DL_ZIMS = ASSET_BASE + '/trial_zim_version_idx.json'
MAPPING = ASSET_BASE + '/map2menu.json'
MI_LKUP = ASSET_BASE + '/trial-menuitem-lkup.json'


