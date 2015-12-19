import property_reader
import getpass

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
