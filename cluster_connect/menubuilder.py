import gtk


def add_submenu(cls, submenu, name):
    menu = gtk.MenuItem(name)
    submenu.append(menu)
    menu_sub = gtk.Menu()
    menu.set_submenu(menu_sub)
    return menu_sub

