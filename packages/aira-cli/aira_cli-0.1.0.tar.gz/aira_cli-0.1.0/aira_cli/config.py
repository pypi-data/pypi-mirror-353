import subprocess
import sys

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def config_set(args):
    command = ["sudo", "bash", "-c", f"echo '{args.value}' > /etc/aira/{args.key}"]
    output = run_command(command)
    print(output)

def config_get(args):
    command = ["cat", f"/etc/aira/{args.key}"]
    output = run_command(command)
    print(output)

def config_defaults(args):
    if not args.force:
        confirm = input("Are you sure you want to apply default configurations? [y/N]: ")
        if confirm.lower() != 'y':
            print("Configuration aborted.")
            return
    command = ["sudo", "cp", "/etc/aira/defaults", "/etc/aira/config"]
    output = run_command(command)
    print(output)