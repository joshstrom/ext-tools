#! /usr/bin/python3
import sys
import re

def read_file(path):
    f = open(path, "r")
    content = f.read()
    f.close()
    return content

def extract_ssh_agent_vars(file_contents):
    ssh_vars = {}
    result = re.search("(SSH_AUTH_SOCK)=(.*); ", file_contents)
    ssh_vars[result.group(1)] = result.group(2)
    result = re.search("(SSH_AGENT_PID)=(.*); ", file_contents)
    ssh_vars[result.group(1)] = result.group(2)

    return ssh_vars

def output_bat(path, ssh_vars):
    f = open(path, "w")
    for key, value in ssh_vars.items():
        f.write("set " + key + "=" + value + "\n")
    f.close()

def convert(path):
    """
    Script should contain three lines like the following:

    SSH_AUTH_SOCK=/tmp/ssh-SmACp20360/agent.20360; export SSH_AUTH_SOCK;
    SSH_AGENT_PID=11104; export SSH_AGENT_PID;
    echo Agent pid 11104;

    Extract the variables and values, then write out a BAT script using SET.

    :param path: Path to file containing set information.
    """
    file_contents = read_file(path)
    ssh_vars = extract_ssh_agent_vars(file_contents)
    output_bat(path, ssh_vars)

def main():
    env_info_path = sys.argv[1]
    convert(env_info_path)

if __name__ == '__main__':
    sys.exit(main())
