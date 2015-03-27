import sys
import os
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
    pass


# Writes the hosts structure to disk. Overwrites file.
def store_hosts(hosts_structure):
    f = open(get_full_data_file_name(), "w")
    for key, value in hosts_structure.items():
        f.write("{0}={1};".format(key, value))

    f.close()


def add_host(hostname, nickname):
    hosts_structure = {hostname: nickname}
    store_hosts(hosts_structure)


def register_host():

    hostname = input("Enter host (hostname or IP address): ")
    nickname = input("Enter nickname for entry: ")
    confirmation = confirm("Register host '{0}' with nickname '{1}? (y/n): ".format(hostname, nickname))

    if not confirmation:
        print("Cancelled.")
        return

    print("Adding '{0}' as '{1}'...".format(hostname, nickname))
    add_host(hostname, nickname)


def list_hosts():
    pass


def print_help():
    print("Supported commands:")
    print("\t register - Register a host (IP address or hostname) for SSH or SCP.")
    print("\t list - List all registered hosts.")


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

    # ... other commands
    else:
        print("Unrecognized command.")
        print_help()

if __name__ == '__main__':
    sys.exit(main())
