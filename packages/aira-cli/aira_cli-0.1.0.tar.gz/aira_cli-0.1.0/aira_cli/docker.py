import subprocess
import sys

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def docker_ps(args):
    command = ["docker", "ps"]
    if args.all:
        command.append("--all")
    output = run_command(command)
    print(output)

def docker_images(args):
    command = ["docker", "images"]
    output = run_command(command)
    print(output)

def docker_logs(args):
    command = ["docker", "logs", args.container]
    if args.follow:
        command.append("--follow")
    if args.tail:
        command.extend(["--tail", str(args.tail)])
    output = run_command(command)
    print(output)

def docker_start(args):
    command = ["docker", "start", args.container]
    output = run_command(command)
    print(output)

def docker_stop(args):
    command = ["docker", "stop", args.container]
    output = run_command(command)
    print(output)

def docker_restart(args):
    command = ["docker", "restart", args.container]
    output = run_command(command)
    print(output)

def docker_compose_up(args):
    command = ["docker-compose", "up"]
    if args.detach:
        command.append("--detach")
    if args.build:
        command.append("--build")
    output = run_command(command)
    print(output)

def docker_compose_down(args):
    if not args.force:
        confirm = input("Are you sure you want to stop and remove all services? [y/N]: ")
        if confirm.lower() != 'y':
            print("Aborted.")
            return
    command = ["docker-compose", "down"]
    output = run_command(command)
    print(output)

def docker_compose_build(args):
    command = ["docker-compose", "build"]
    output = run_command(command)
    print(output)

def docker_compose_ps(args):
    command = ["docker-compose", "ps"]
    output = run_command(command)
    print(output)

def docker_cleanup(args):
    if not args.force:
        confirm = input("Are you sure you want to remove unused Docker resources? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cleanup aborted.")
            return
    command = ["docker", "system", "prune", "-f"]
    output = run_command(command)
    print(output)