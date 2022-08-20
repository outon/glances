# -*- coding: utf-8 -*-
#
# This file is part of Glances.
#
# SPDX-FileCopyrightText: 2022 Nicolas Hennion <nicolas@nicolargo.com>
#
# SPDX-License-Identifier: LGPL-3.0-only
#

"""StdoutCsv interface class."""

import time

from glances.compat import printandflush


class GlancesStdoutCsv(object):

    """This class manages the StdoutCsv display."""

    separator = ','
    na = 'N/A'

    def __init__(self, config=None, args=None):
        # Init
        self.config = config
        self.args = args

        # Display the header only on the first line
        self.header = True

        # Build the list of plugin and/or plugin.attribute to display
        self.plugins_list = self.build_list()

    def build_list(self):
        """Return a list of tuples taken from self.args.stdout

        :return: A list of tuples. Example -[(plugin, attribute), ... ]
        """
        ret = []
        for p in self.args.stdout_csv.split(','):
            if '.' in p:
                p, a = p.split('.')
            else:
                a = None
            ret.append((p, a))
        return ret

    def end(self):
        pass

    def build_header(self, plugin, attribute, stat):
        """Build and return the header line"""
        line = ''

        if attribute is not None:
            line += '{}.{}{}'.format(plugin, attribute, self.separator)
        else:
            if isinstance(stat, dict):
                for k in stat.keys():
                    line += '{}.{}{}'.format(plugin, str(k), self.separator)
            elif isinstance(stat, list):
                for i in stat:
                    if isinstance(i, dict) and 'key' in i:
                        for k in i.keys():
                            line += '{}.{}.{}{}'.format(plugin, str(i[i['key']]), str(k), self.separator)
            else:
                line += '{}{}'.format(plugin, self.separator)

        return line

    def build_data(self, plugin, attribute, stat):
        """Build and return the data line"""
        line = ''

        if attribute is not None:
            line += '{}{}'.format(str(stat.get(attribute, self.na)), self.separator)
        else:
            if isinstance(stat, dict):
                for v in stat.values():
                    line += '{}{}'.format(str(v), self.separator)
            elif isinstance(stat, list):
                for i in stat:
                    if isinstance(i, dict) and 'key' in i:
                        for v in i.values():
                            line += '{}{}'.format(str(v), self.separator)
            else:
                line += '{}{}'.format(str(stat), self.separator)

        return line

    def update(self, stats, duration=3):
        """Display stats to stdout.

        Refresh every duration second.
        """
        # Build the stats list
        line = ''
        for plugin, attribute in self.plugins_list:
            # Check if the plugin exist and is enable
            if plugin in stats.getPluginsList() and stats.get_plugin(plugin).is_enabled():
                stat = stats.get_plugin(plugin).get_export()
            else:
                continue

            # Build the line to display (header or data)
            if self.header:
                line += self.build_header(plugin, attribute, stat)
            else:
                line += self.build_data(plugin, attribute, stat)

        # Display the line (without the last 'separator')
        printandflush(line[:-1])

        # Display header one time
        self.header = False

        # Wait until next refresh
        if duration > 0:
            time.sleep(duration)
