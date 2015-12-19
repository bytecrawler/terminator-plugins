import gtk
import connector
import property_reader


def add_submenu(submenu, name):
    menu = gtk.MenuItem(name)
    submenu.append(menu)
    menu_sub = gtk.Menu()
    menu.set_submenu(menu_sub)
    return menu_sub


def add_split_submenu(terminal, cluster, user, server, cluster_menu_sub, sudo=False):
        # Add a menu if you connect to just one server
        if sudo:
            cluster_sub_split = add_submenu(cluster_menu_sub, user + " (sudo)")
        else:
            cluster_sub_split = add_submenu(cluster_menu_sub, user)

        menuitem = gtk.MenuItem('Horizontal Split')
        menuitem.connect('activate', connector.connect_server,
                         terminal, cluster, user, server, 'H', sudo)
        cluster_sub_split.append(menuitem)

        menuitem = gtk.MenuItem('Vertical Split')
        menuitem.connect('activate', connector.connect_server,
                         terminal, cluster, user, server, 'V', sudo)
        cluster_sub_split.append(menuitem)

        menuitem = gtk.MenuItem('New Tab')
        menuitem.connect('activate', connector.connect_server,
                         terminal, cluster, user, server, 'T', sudo)
        cluster_sub_split.append(menuitem)


def split_terminal(terminal, servers, user, window, cluster, groupname, sudo):
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
        split_terminal(terminal, server1, user, window, cluster, groupname, sudo)
        split_terminal(terminal2, server2, user, window, cluster, groupname, sudo)

    elif server_count == 1:
        connector.start_ssh(terminal, user, servers[0], cluster, sudo)
