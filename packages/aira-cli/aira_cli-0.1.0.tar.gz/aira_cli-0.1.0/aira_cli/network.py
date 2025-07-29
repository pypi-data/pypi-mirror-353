import subprocess
import sys

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def network_status(args):
    command = ["ip", "addr"]
    output = run_command(command)
    print(output)

def network_firewall_list(args):
    command = ["sudo", "ufw", "status"]
    output = run_command(command)
    print(output)

def network_firewall_allow(args):
    command = ["sudo", "ufw", "allow", str(args.port)]
    if args.protocol:
        command.extend(["--proto", args.protocol])
    if args.from_ip:
        command.extend(["from", args.from_ip])
    output = run_command(command)
    print(output)

def network_firewall_deny(args):
    command = ["sudo", "ufw", "deny", str(args.port)]
    if args.protocol:
        command.extend(["--proto", args.protocol])
    if args.from_ip:
        command.extend(["from", args.from_ip])
    output = run_command(command)
    print(output)

def network_firewall_block(args):
    command = ["sudo", "ufw", "deny", "from", args.ip_address]
    output = run_command(command)
    print(output)

def network_firewall_unblock(args):
    command = ["sudo", "ufw", "allow", "from", args.ip_address]
    output = run_command(command)
    print(output)

def network_firewall_reset(args):
    if not args.force:
        confirm = input("Are you absolutely sure? This will remove ALL custom firewall rules. [type 'RESET' to confirm]: ")
        if confirm != 'RESET':
            print("Reset aborted.")
            return
    command = ["sudo", "ufw", "reset"]
    output = run_command(command)
    print(output)

def network_dns_add_host(args):
    command = ["sudo", "bash", "-c", f"echo '{args.ip_address} {args.hostname}' >> /etc/hosts"]
    output = run_command(command)
    print(output)

def network_dns_remove_host(args):
    command = ["sudo", "sed", "-i", f"/{args.hostname}/d", "/etc/hosts"]
    output = run_command(command)
    print(output)

def network_dns_show_hosts(args):
    command = ["cat", "/etc/hosts"]
    output = run_command(command)
    print(output)

def network_dns_configure_resolver(args):
    if not args.force:
        confirm = input("Are you sure you want to configure the DNS resolver? [y/N]: ")
        if confirm.lower() != 'y':
            print("Configuration aborted.")
            return
    resolver_config = "\n".join([f"nameserver {ns}" for ns in args.nameservers])
    command = ["sudo", "bash", "-c", f"echo '{resolver_config}' > /etc/resolv.conf"]
    output = run_command(command)
    print(output)