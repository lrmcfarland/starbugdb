#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Gunicorn wrapper for the Flask UI for the starbug observation database

gunicorn needs app to be instantiated outside of main
"""

import obsui

application = obsui.factory()


