import sys
import os
import collections
import subprocess


def get_full_data_file_name():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), ".hostslist.txt")


def affirmative(answer):
    answer = answer.lower()
    if (answer == "yes") or (answer == "y"):
        return True
    elif (answer == "no") or (answer == "n"):
        return False
    else:
        return None


def confirm(message):
    while True:
        confirmation = input(message)
        is_affirmative = affirmative(confirmation)

        if is_affirmative is None:
            print("Invalid confirmation.")
            continue

        return is_affirmative


def load_hosts():
    hosts = collections.OrderedDict()
    file_name = get_full_data_file_name()
    if not os.path.isfile(file_name):
        return hosts

    f = open(file_name, "r")
    content = f.read().splitlines()
    for entry in content:
        nickname, sep, hostname = entry.partition("=")
        hosts[nickname] = hostname

    f.close()
    return hosts


# Writes the hosts structure to disk. Overwrites file.
def store_hosts(hosts):
    f = open(get_full_data_file_name(), "w")
    for key, value in hosts.items():
        f.write("{0}={1}\n".format(key, value))

    f.close()


def get_by_index(hosts, index):
    return hosts[list(hosts.keys())[index]]


def get_by_nickname(hosts, nickname):
    return hosts[nickname]


def register_host():
    hosts = load_hosts()
    hostname = input("Enter host (hostname or IP address): ")
    nickname = input("Enter nickname for entry: ")
    confirmation = confirm("Register host '{0}' with nickname '{1}? (y/n): ".format(hostname, nickname))

    if not confirmation:
        print("Cancelled.")
        return

    print("Adding '{0}' as '{1}'...".format(hostname, nickname))
    hosts[nickname] = hostname
    store_hosts(hosts)


def list_hosts():
    hosts = load_hosts()
    index = 0
    for nickname, host in hosts.items():
        print("[{0}] {1}: {2}".format(index, nickname, host))
        index += 1


def connect():
    hosts = load_hosts()
    at_index = get_by_index(hosts, 0)
    print(at_index)


def print_help():
    print("Supported commands:")
    print("\t register - Register a host (IP address or hostname) for SSH or SCP.")
    print("\t list - List all registered hosts.")
    print("\t connect - Connect to a host.")


def main():
    commands = sys.argv
    if len(commands) < 2:
        print_help()
        return

    command = commands[1]
    if command == "register":
        register_host()
        return
    if command == "list":
        list_hosts()
        return
    if command == "connect":
        connect()
        return

    # ... other commands
    else:
        print("Unrecognized command.")
        print_help()

if __name__ == '__main__':
    sys.exit(main())
