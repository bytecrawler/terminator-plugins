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

AVAILABLE = ['ClusterConnect']
current_user = getpass.getuser()


class ClusterConnect(plugin.Plugin):
    capabilities = ['terminal_menu']

    def callback(self, menuitems, menu, terminal):
        self._terminal = terminal
        self._menu = menu
        self._menuitems = menuitems
        clusters = property_reader.CLUSTERS
        var_submenu = menubuilder.MenuBuilder.add_submenu(menuitems, 'ClusterConnect')
        groups = property_reader.read_groups()
        groups.sort()
        if len(groups) > 0:
            for group in groups:
                sub_groups = self.add_submenu(var_submenu, group)
                for cluster in clusters:
                    self.add_cluster_submenu(terminal, cluster, group, sub_groups)

            menuitem = gtk.SeparatorMenuItem()
            var_submenu.append(menuitem)
        for cluster in clusters:
            self.add_cluster_submenu(terminal, cluster, 'none', var_submenu)

    def add_cluster_submenu(self, terminal, cluster, group, menu_sub):
        # Get users and add current to connect with current user
        users = property_reader.get_property(cluster, 'user')
        current_user_prop = property_reader.get_property(cluster, 'current_user', True)
        sudousers = property_reader.get_property(cluster, 'sudouser')

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
        servers = property_reader.get_property(cluster, 'server')
        servers.sort()
        if len(servers) > 1:
            if 'cluster' not in servers:
                servers.insert(0, 'cluster')
            else:
                servers.remove('cluster')
                servers.insert(0, 'cluster')

                # Add a submenu for cluster servers
        group_tmp = property_reader.get_property(cluster, 'group', 'none')
        # Check if users exists for cluster
        if 'users' in locals() and group_tmp == group:
            self.check_for_users_in_cluster(servers, menu_sub, cluster, terminal, users, sudousers)

    def check_for_users_in_cluster(self, servers, menu_sub, cluster, terminal, users, sudousers):
        if len(servers) > 1:
            # Add a submenu for server, if there is more than one
            cluster_sub_servers = menubuilder.MenuBuilder.add_submenu(menu_sub, cluster)
            for server in servers:
                # add submenu for users
                cluster_sub_users = menubuilder.MenuBuilder.add_submenu(cluster_sub_servers, server)
                self.create_cluster_sub_servers(server, users, terminal, cluster, cluster_sub_users, sudousers)
            print "Iterated"
        else:
            # If there is just one server, don't add a server submenu
            cluster_sub_users = menubuilder.MenuBuilder.add_submenu(menu_sub, cluster)
            for user in users:
                # Add menu for split and new tab
                self.add_split_submenu(terminal, cluster, user,
                                       servers[0], cluster_sub_users)

    def create_cluster_sub_servers(self, server, users, terminal, cluster, cluster_sub_users, sudousers):
        for user in users:
            if server != 'cluster':
                self.add_split_submenu(terminal, cluster,
                                       user, server, cluster_sub_users)
            else:
                menuitem = gtk.MenuItem(user)
                menuitem.connect('activate', self.connect_cluster,
                                 terminal, cluster, user, 'cluster')
                cluster_sub_users.append(menuitem)
                # add submenu for sudousers
        if 'sudousers' in locals() and sudousers:
            for sudouser in sudousers:
                if server != 'cluster':
                    self.add_split_submenu(terminal, cluster,
                                           sudouser, server, cluster_sub_users, True)
                else:
                    menuitem = gtk.MenuItem(sudouser + " (sudo)")
                    menuitem.connect('activate', self.connect_cluster,
                                     terminal, cluster, sudouser, 'cluster', True)
                    cluster_sub_users.append(menuitem)

    def add_split_submenu(self, terminal, cluster, user, server, cluster_menu_sub, sudo=False):
        # Add a menu if you connect to just one server
        if sudo:
            cluster_sub_split = menubuilder.MenuBuilder.add_submenu(cluster_menu_sub, user + " (sudo)")
        else:
            cluster_sub_split = menubuilder.MenuBuilder.add_submenu(cluster_menu_sub, user)

        menuitem = gtk.MenuItem('Horizontal Split')
        menuitem.connect('activate', self.connect_server,
                         terminal, cluster, user, server, 'H', sudo)
        cluster_sub_split.append(menuitem)

        menuitem = gtk.MenuItem('Vertical Split')
        menuitem.connect('activate', self.connect_server,
                         terminal, cluster, user, server, 'V', sudo)
        cluster_sub_split.append(menuitem)

        menuitem = gtk.MenuItem('New Tab')
        menuitem.connect('activate', self.connect_server,
                         terminal, cluster, user, server, 'T', sudo)
        cluster_sub_split.append(menuitem)

    def connect_cluster(self, widget, terminal, cluster, user, server_connect, sudo=False):

        if property_reader.CLUSTERS.has_key(cluster):
            # get the first tab and add a new one so you don't need to care
            # about which window is focused
            focussed_terminal = None
            term_window = terminal.terminator.windows[0]
            # add a new window where we connect to the servers, and switch to this tab
            term_window.tab_new(term_window.get_focussed_terminal())
            visible_terminals = term_window.get_visible_terminals()
            for visible_terminal in visible_terminals:
                if visible_terminal.vte.is_focus():
                    focussed_terminal = visible_terminal

                    # Create a group, if the terminals should be grouped
            servers = property_reader.get_property(cluster, 'server')
            servers.sort()

            # Remove cluster from server, there shouldn't be a server named cluster
            if 'cluster' in servers:
                servers.remove('cluster')

            old_group = terminal.group
            if property_reader.get_property(cluster, 'groupby'):
                groupname = cluster + "-" + str(random.randint(0, 999))
                terminal.really_create_group(term_window, groupname)
            else:
                groupname = 'none'
            self.split_terminal(focussed_terminal, servers, user,
                                term_window, cluster, groupname, sudo)
            # Set old window back to the last group, as really_create_group
            # sets the window to the specified group
            terminal.set_group(term_window, old_group)

    def connect_server(self, widget, terminal, cluster, user,
                       server_connect, option, sudo):

        focussed_terminal = None
        term_window = terminal.terminator.windows[0]
        # if there is just one server, connect to that server and dont split the terminal
        visible_terminals_temp = term_window.get_visible_terminals()

        if option == 'H':
            terminal.key_split_horiz()
        elif option == 'V':
            terminal.key_split_vert()
        elif option == 'T':
            term_window.tab_new(term_window.get_focussed_terminal())

        visible_terminals = term_window.get_visible_terminals()
        for visible_terminal in visible_terminals:
            if not visible_terminal in visible_terminals_temp:
                terminal2 = visible_terminal
        self.start_ssh(terminal2, user, server_connect, cluster, sudo)

    def split_terminal(self, terminal, servers, user, window, cluster, groupname, sudo):
        # Splits the window, the split count is limited by
        # the count of servers given to the function
        if property_reader.get_property(cluster, 'groupby'):
            terminal.set_group(window, groupname)
        server_count = len(servers)

        if server_count > 1:
            visible_terminals_temp = window.get_visible_terminals()
            server1 = servers[:server_count / 2]
            server2 = servers[server_count / 2:]

        horiz_splits = property_reader.get_property(cluster, 'horiz_splits', 5)

        if server_count > horiz_splits:
            terminal.key_split_vert()
        elif server_count > 1:
            terminal.key_split_horiz()

        if server_count > 1:
            visible_terminals = window.get_visible_terminals()
            for visible_terminal in visible_terminals:
                if visible_terminal not in visible_terminals_temp:
                    terminal2 = visible_terminal
            self.split_terminal(terminal, server1, user, window,
                                cluster, groupname, sudo)
            self.split_terminal(terminal2, server2, user, window,
                                cluster, groupname, sudo)

        elif server_count == 1:
            self.start_ssh(terminal, user, servers[0], cluster, sudo)

    def start_ssh(self, terminal, user, hostname, cluster, sudo):
        # Function to generate the ssh command, with specified options

        if hostname:
            command = "ssh"

            # get username, if user is current don't set user
            if (user != current_user) and (sudo is False):
                command = command + " -l " + user

                # check if ssh agent should be used, if not disable it
            if property_reader.get_property(cluster, 'agent'):
                command += " -A"
            else:
                command += " -a"

                # If port is configured, get that port
            port = property_reader.get_property(cluster, 'port')
            if port:
                command = command + " -p " + port

                # If ssh-key is specified, use that key
            key = property_reader.get_property(cluster, 'identity')
            if key:
                command = command + " -i " + key

                # get verbosity level
            verbose = property_reader.get_property(cluster, 'verbose')
            if verbose:
                count = 0
                command = "-"
                while count < verbose < 3:
                    command += "v"
                    count += 1

            command = command + " " + hostname

            if sudo:
                command = command + " -t sudo -su " + user

                # Check if a command was generated an pass it to the terminal
            if command[len(command) - 1] != '\n':
                command += '\n'
                terminal.vte.feed_child(command)
