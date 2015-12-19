#	Copyright (C) 2014 Daniel Schmitz
#	Site: github.com/dr1s
#
#	This program is free software; you can redistribute it and/or
#	modify it under the terms of the GNU General Public License
#	as published by the Free Software Foundation; either version 2
#	of the License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program; if not, write to the Free Software
#	Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import gtk
import random
import terminatorlib.plugin as plugin
import getpass
import menubuilder
import property_reader
import connector

AVAILABLE = ['ClusterConnect']
current_user = getpass.getuser()


class ClusterConnect(plugin.Plugin):
    capabilities = ['terminal_menu']

    def callback(self, menuitems, menu, terminal):
        self._terminal = terminal
        self._menu = menu
        self._menuitems = menuitems
        clusters = property_reader.CLUSTERS
        var_submenu = menubuilder.add_submenu(menuitems, 'ClusterConnect')
        groups = property_reader.read_groups()
        groups.sort()
        if len(groups) > 0:
            for group in groups:
                sub_groups = menubuilder.add_submenu(var_submenu, group)
                for cluster in clusters:
                    self.create_cluster_submenu(cluster, group, sub_groups)

            menuitem = gtk.SeparatorMenuItem()
            var_submenu.append(menuitem)
        for cluster in clusters:
            self.create_cluster_submenu(cluster, 'none', var_submenu)

    def create_cluster_submenu(self, cluster, group, menu_sub):
        # Get users and add current to connect with current user
        users = property_reader.get_property(cluster, 'user')
        sudousers = property_reader.get_property(cluster, 'sudouser')
        servers = property_reader.get_property(cluster, 'server')
        group_tmp = property_reader.get_property(cluster, 'group', 'none')

        self.build_users_and_sort(users, sudousers, servers, cluster)

        if 'users' in locals() and group_tmp == group:
            if len(servers) > 1:
                self.create_cluster_sub_users(servers, menu_sub, cluster, users, sudousers)
            else:
                self.create_servers(servers[0], menu_sub, cluster, users)

    def create_cluster_sub_users(self, servers, menu_sub, cluster, users, sudousers):
        if len(servers) > 1:
            cluster_sub_servers = menubuilder.add_submenu(menu_sub, cluster)
            for server in servers:
                # add submenu for users
                cluster_sub_users = menubuilder.add_submenu(cluster_sub_servers, server)
                self.create_cluster_sub_servers(server, users, self._terminal, cluster, cluster_sub_users, sudousers)

    def create_servers(self, server, menu_sub, cluster, users):
        cluster_sub_users = menubuilder.add_submenu(menu_sub, cluster)
        for user in users:
            menubuilder.add_split_submenu(self._terminal, cluster, user, server, cluster_sub_users)

    def create_cluster_sub_servers(self, server, users, terminal, cluster, cluster_sub_users, sudousers):
        for user in users:
            if server != 'cluster':
                menubuilder.add_split_submenu(terminal, cluster, user, server, cluster_sub_users)
            else:
                menuitem = gtk.MenuItem(user)
                menuitem.connect('activate', connector.connect_cluster,
                                 terminal, cluster, user, 'cluster')
                cluster_sub_users.append(menuitem)
                # add submenu for sudousers
        if 'sudousers' in locals() and sudousers:
            self.add_suduoers(terminal, cluster, sudousers, server, cluster_sub_users)

    def build_users_and_sort(self, users, sudousers, servers, cluster):

        current_user_prop = property_reader.get_property(cluster, 'current_user', True)
        if users:
            users.sort()
            if current_user_prop and current_user not in users:
                users.insert(0, current_user)
        elif current_user_prop:
            users = [current_user]
            # Get sudousers for current user
        if sudousers:
            sudousers.sort()
            # Get servers and insert cluster for cluster connect
        servers.sort()

        if len(servers) > 1:
            if 'cluster' not in servers:
                servers.insert(0, 'cluster')
            else:
                servers.remove('cluster')
                servers.insert(0, 'cluster')

    def add_suduoers(self, terminal, cluster, sudousers, server, cluster_sub_users):
        for sudouser in sudousers:
            if server != 'cluster':
                menubuilder.add_split_submenu(terminal, cluster, sudouser, server, cluster_sub_users, True)
            else:
                menuitem = gtk.MenuItem(sudouser + " (sudo)")
                menuitem.connect('activate', connector.connect_cluster,
                                 terminal, cluster, sudouser, 'cluster', True)
                cluster_sub_users.append(menuitem)
