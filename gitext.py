#! /usr/bin/python3
# Script to automate some Git tasks around branches.

import sys
import subprocess
import re


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def confirm(prompt):
    while True:
        user_input = str(input(prompt).lower())
        if user_input == "y":
            return True

        if user_input == "n":
            return False

        # Anything else:
        print("Invalid input.")


# Returns the name of the current branch as a string. If not a git repo, will print error and exit.
def get_current_branch_name():
    try:
        return subprocess.check_output("git rev-parse --abbrev-ref HEAD", shell=False).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        print("Done.")  # Error printed by git.
        sys.exit()


def get_all_local_branches():
    try:
        branch_list = subprocess.check_output("git branch", shell=False).decode("utf-8")
        return re.findall(r"^\*?\s+(\S+)$", branch_list, re.MULTILINE)
    except subprocess.CalledProcessError:
        print("Done.")  # Error printed by git.
        sys.exit()

# Returns list of branch names (as list of strings) that are NOT the current branch.
# If not a git repo, will print error and exit.
def get_unselected_local_branches():
    try:
        branch_list = subprocess.check_output("git branch", shell=False).decode("utf-8")
        return re.findall(r"^\s+(\S+)$", branch_list, re.MULTILINE)
    except subprocess.CalledProcessError:
        print("Done.")  # Error printed by git.
        sys.exit()


def get_remote_branches():
    try:
        branch_list = subprocess.check_output("git branch --remote", shell=False).decode("utf-8")
        branches = re.findall(r"^\s+(\S+)$", branch_list, re.MULTILINE)
        return [branch.split('/')[-1] for branch in branches]
    except subprocess.CalledProcessError:
        print("Done.")  # Error printed by git.
        sys.exit()


def count_log_length(log_string):
    try:
        branch_list = subprocess.check_output("git --no-pager log --oneline " + log_string, shell=False).decode("utf-8")
        return len(branch_list.splitlines())
    except subprocess.CalledProcessError:
        print("Done.")  # Error printed by git.
        sys.exit()


# Returns True if the provided branch has a remote tracking branch. False otherwise.
# If not a git repo, will print error and exit.
def has_remote_tracking_branch(local_branch_name):
    try:
        return subprocess.check_output("git for-each-ref --format=%(upstream:short) refs/heads/" + local_branch_name,
                                       shell=False).decode("utf-8").strip() != ""
    except subprocess.CalledProcessError:
        print("Done.")  # Error printed by git.
        sys.exit()


# Displays a list of available local branches and prompts the user to select one.
# Returns the name of the selected branch or None if the user cancelled.
def select_branch():
    branch_list = get_unselected_local_branches()
    if len(branch_list) == 0:
        print("No other branches available.")
        return None

    return list_query(branch_list, "Branches:")

def list_query(available_options, list_title):
    if len(available_options) == 0:
        return None

    print(list_title)
    for i in range(len(available_options)):
        print("\t{0}: {1}".format(i, available_options[i]))

    branch_num = -1

    while True:
        user_input = str(input("\nMake selection (q to cancel): ")).lower()
        if user_input == "q":
            return None
        if not is_int(user_input):
            print("Invalid selection.")
            continue

        test_branch_num = int(user_input)
        if test_branch_num < 0 or test_branch_num >= len(available_options):
            print("Selection out of range.")
            continue

        # Valid
        branch_num = test_branch_num
        break

    return available_options[branch_num]

def interactive_checkout():
    current_branch = get_current_branch_name()
    print("Current: " + current_branch)

    to_switch = select_branch()
    if not to_switch:
        print("Cancelled.")
        return

    print("Checkout branch: " + to_switch + "\n")

    subprocess.call("git checkout " + to_switch)
    print("Done.")


def diff_branch():
    current_branch = get_current_branch_name()
    print("Diff: " + current_branch + " <--> ?")
    print("Select target branch.\n")

    to_diff_against = select_branch()
    if not to_diff_against:
        print("Cancelled.")
        return

    print("Running diff: " + current_branch + " (left) <--> " + to_diff_against + " (right)")
    subprocess.call("git difftool --dir-diff " + current_branch + ".." + to_diff_against)
    print("Done.")


def push_remote():
    current_branch = get_current_branch_name()
    if has_remote_tracking_branch(current_branch):
        print("Current branch '" + current_branch + "' already has a remote tracking branch.")
        print("Done.")
        return

    if confirm("Add remote tracking branch 'origin/" + current_branch + "'? (y/n): "):
        command = "git push --set-upstream origin " + current_branch
        print("Running command: '" + command + "'")
        subprocess.call(command)
        print("Done.")
    else:
        print("Cancelled.")

    return


def check_has_remote():
    current_branch = get_current_branch_name()
    if has_remote_tracking_branch(current_branch):
        print("Current branch '" + current_branch + "' has a remote tracking branch.")
    else:
        print("Current branch '" + current_branch + "' does NOT have a remote tracking branch.")

    return


def pull_remote_branch():
    remote_branch_list = get_remote_branches()
    local_branch_list = get_all_local_branches()
    available_branches = [branch for branch in remote_branch_list if branch not in local_branch_list]

    selection = list_query(available_branches, "Available Remote Branches:")
    if selection is None:
        print("Cancelled.")
        return

    if confirm("Pull remote branch '" + selection + "'? (y/n):"):
        command = "git checkout -b " + selection + " origin/" + selection
        print("Running command: '" + command + "'")
        subprocess.call(command)
        print("Done.")
    else:
        print("Cancelled.")


def is_in_sync():
    current_branch = get_current_branch_name()
    print("Current branch: " + current_branch + ". Please select branch to compare.")
    other_branch = select_branch()
    if not other_branch:
        print("Cancelled.")
        return

    print("")
    print("Changes on '" + current_branch + "' that are NOT on '" + other_branch + "': " + str(
        count_log_length(other_branch + ".." + current_branch)))
    print("Changes on '" + other_branch + "' that are NOT on '" + current_branch + "': " + str(
        count_log_length(current_branch + ".." + other_branch)))
    print("")
    print("Done.")


def print_version():
    print("Git-ext tools v1.0")
    print("Python version: " + sys.version)


def print_help():
    print("Supported commands:")
    print("\t checkout - Interactively checkout a different branch.")
    print("\t diffbranch - Diff the current branch against a target branch.")
    print("\t pushremote - Push the current (local only) branch to origin.")
    print("\t hasremote - Check if the current branch has a tracking branch on origin.")
    print("\t insync - Shows details around branch synchronizing.")
    print("\t help - Prints this message.")
    print("\t version - Prints version of this tool.")
    print("\t pullremote - Pull a remote untracked branch.")


def main():
    commands = sys.argv
    if len(commands) < 2:
        print_help()
        return

    command = commands[1]
    if command == "help":
        print_help()
        return
    if command == "version":
        print_version()
        return
    if command == "checkout":
        interactive_checkout()
        return
    if command == "diffbranch":
        diff_branch()
        return
    if command == "pushremote":
        push_remote()
        return
    if command == "hasremote":
        check_has_remote()
        return
    if command == "insync":
        is_in_sync()
        return
    if command == "pullremote":
        pull_remote_branch()
        return
    # ... other commands
    else:
        print("Unrecognized command.")
        print_help()


if __name__ == '__main__':
    sys.exit(main())