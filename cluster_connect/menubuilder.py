import gtk
import connector


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

