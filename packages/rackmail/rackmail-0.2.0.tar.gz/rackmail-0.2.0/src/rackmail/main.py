import argparse
from .version import VERSION
from .subcommands.enable_user import enable_user
from .subcommands.disable_user import disable_user
from .subcommands.get_mailbox import get_mailbox
from .subcommands.set_password import set_password

def main():
    main_parser = argparse.ArgumentParser(prog="rackmail",description="CLI to interact with Rackspace's Hosted Email API",)
    main_parser.add_argument("--version",action="version",version=f"{main_parser.prog} V.{VERSION}")

    # This is store two arguments, we can add this as a parent to sub parsers so they will use the --email and --domain arguments.
    global_command_parser = argparse.ArgumentParser(add_help=False)
    global_command_parser.add_argument("-e","--email",action="store",metavar="email",dest="email",help="the email address of a mailbox",required=True)
    global_command_parser.add_argument("-d","--domain",action="store",metavar="domain",dest="domain",help="the domain of a mailbox",required=True)

    subparsers = main_parser.add_subparsers(dest="command")

    enable_user_subcommand = subparsers.add_parser("enableuser",description="Enables a hosted mailbox",parents=[global_command_parser])
    enable_user_subcommand.set_defaults(func=enable_user)

    disable_user_subcommand = subparsers.add_parser("disableuser",description="Disables a hosted mailbox",parents=[global_command_parser])
    disable_user_subcommand.set_defaults(func=disable_user)
    get_mailbox_subcommand = subparsers.add_parser("getmailbox",description="Gets all available information about a mailbox",parents=[global_command_parser])
    get_mailbox_subcommand.set_defaults(func=get_mailbox)

    change_password_subcommand = subparsers.add_parser("setpassword",description="Sets the password of a mailbox",parents=[global_command_parser])
    change_password_subcommand.add_argument("-p","--password",action="store",metavar="password",dest="password",help="The password you want set on a mailbox",required=False,default=None)
    change_password_subcommand.set_defaults(func=set_password)
    
    args = main_parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        main_parser.print_help()

if __name__ == "__main__":
    main()