import subprocess
import sys

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def storage_usage(args):
    command = ["df", "-h"]
    output = run_command(command)
    print(output)

def storage_logs_show_sizes(args):
    command = ["du", "-sh", "/var/log", "/var/lib/docker/containers"]
    output = run_command(command)
    print(output)

def storage_logs_clean(args):
    if not args.force:
        confirm = input("Are you sure you want to clean logs? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cleanup aborted.")
            return
    command = ["sudo", "find", "/var/log", "-type", "f", "-mtime", f"+{args.older_than}", "-delete"]
    output = run_command(command)
    print(output)

def storage_backup_create(args):
    backup_name = args.name if args.name else "backup"
    destination = args.destination if args.destination else "/var/aira/backups"
    command = ["sudo", "tar", "-czf", f"{destination}/{backup_name}.tar.gz", "/path/to/important/data"]
    output = run_command(command)
    print(output)

def storage_backup_list(args):
    command = ["ls", "-lh", "/var/aira/backups"]
    output = run_command(command)
    print(output)

def storage_backup_restore(args):
    if not args.force:
        confirm = input("Restoring from backup will overwrite current AIRA data. Are you sure? [type 'RESTORE' to confirm]: ")
        if confirm != 'RESTORE':
            print("Restore aborted.")
            return
    command = ["sudo", "tar", "-xzf", f"/var/aira/backups/{args.backup_name}.tar.gz", "-C", "/"]
    output = run_command(command)
    print(output)