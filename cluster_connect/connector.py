import property_reader
import getpass
import random
import menubuilder

current_user = getpass.getuser()


def connect_server(widget, terminal, cluster, user, server_connect, option, sudo):
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
        if visible_terminal not in visible_terminals_temp:
            terminal2 = visible_terminal

    start_ssh(terminal2, user, server_connect, cluster, sudo)


def start_ssh(terminal, user, hostname, cluster, sudo):
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


def connect_cluster(widget, terminal, cluster, user, server_connect, sudo=False):
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
        menubuilder.split_terminal(focussed_terminal, servers, user, term_window, cluster, groupname, sudo)
        # Set old window back to the last group, as really_create_group
        # sets the window to the specified group
        terminal.set_group(term_window, old_group)
