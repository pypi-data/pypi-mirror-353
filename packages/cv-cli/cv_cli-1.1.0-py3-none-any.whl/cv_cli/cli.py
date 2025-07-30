from pathlib import Path
from argparse import ArgumentParser, Namespace
from .constants import DEFAULT_PROFILE, DEFAULT_TEMPLATE, DEFAULT_OUTPUT_FNAME, DEFAULT_PROFILE_REPO
from .render import compile_pdf
from .git import git_init, git_clone, git_sync
from .profiles import new_template, edit_template, del_template, init_template, sync_template, clone_template
from .templates import new_template, edit_template, del_template, init_template, sync_template, clone_template

def build_parser(subparser):
    build = subparser.add_parser(name="build", help="Generate latex resumes from a yaml profile.")
    build.add_argument("-p", "--profile", help="Sets profile for build.", default=DEFAULT_PROFILE)
    build.add_argument("-t", "--template", help="Sets resume template for build.", default=DEFAULT_TEMPLATE)
    build.add_argument("-o", "--output", help="Sets output file path", default=DEFAULT_OUTPUT_FNAME, type=Path)

def profiles_parser(subparser):
    profiles = subparser.add_parser("profiles", help="Manage and sync profile data.")
    subparser = profiles.add_subparsers(dest="profiles_command", required=True)

    profiles_new = subparser.add_parser("new", help="Create new profile.")
    profiles_new.add_argument("name", help="Name of profile.")
    profiles_new.add_argument("-s", "--src", help="Base profile to copy from.", default=None)

    profiles_edit = subparser.add_parser("edit", help="Edit profile.")
    profiles_edit.add_argument("name", nargs="?", help="Name of profile.", default=None)
    profiles_edit.add_argument("-e", "--editor", help="Editor cmdline tool", default="code")

    profiles_del = subparser.add_parser("del", help="Delete profile.")
    profiles_del.add_argument("name", help="Name of profile.")

    profiles_init = subparser.add_parser("init", help="Initialize profiles repository.")
    profiles_init.add_argument("name", nargs="?", help="Name of repo.", default=DEFAULT_PROFILE_REPO)
    profiles_init.add_argument("-p", "--public", help="Make repo public.", action="store_true")

    # profile_sync
    subparser.add_parser("sync", help="Sync profiles with remote.")

    profiles_clone = subparser.add_parser("clone", help="Clone profiles from remote.")
    profiles_clone.add_argument("remote", help="Url to remote.")
    profiles_clone.add_argument("-f", "--force", help="Forces clone (Removes existing repo.)", action="store_true")

def templates_parser(subparser):
    templates = subparser.add_parser("templates", help="Manage and sync template data.")
    subparser = templates.add_subparsers(dest="templates_command", required=True)

    templates_new = subparser.add_parser("new", help="Create new template.")
    templates_new.add_argument("name", help="Name of template.")
    templates_new.add_argument("-s", "--src", help="Base template to copy from.", default=None)

    templates_edit = subparser.add_parser("edit", help="Edit template.")
    templates_edit.add_argument("name", nargs="?", help="Name of template.", default=None)
    templates_edit.add_argument("-e", "--editor", help="Editor cmdline tool", default="code")

    profiles_del = subparser.add_parser("del", help="Delete template.")
    profiles_del.add_argument("name", help="Name of template.")

    templates_init = subparser.add_parser("init", help="Initialize template repository.")
    templates_init.add_argument("name", nargs="?", help="Name of repo.", default=DEFAULT_PROFILE_REPO)
    templates_init.add_argument("-p", "--public", help="Make repo public.", action="store_true")

    # template_sync
    templates_sync = subparser.add_parser("sync", help="Sync template with remote.")
    templates_sync.add_argument("name", help="Name of template.")

    templates_clone = subparser.add_parser("clone", help="Clone template from remote.")
    templates_clone.add_argument("remote", help="Url to remote.")
    templates_clone.add_argument("name", nargs="?", help="Name of template")
    templates_clone.add_argument("-f", "--force", help="Forces clone (Removes existing repo.)", action="store_true")


def get_args() -> Namespace:
    parser = ArgumentParser(prog="resume", description="Command-line tool to generate resumes from YAML and LaTeX templates")
    subparser = parser.add_subparsers(dest="command", required=True)

    build_parser(subparser)
    profiles_parser(subparser)
    templates_parser(subparser)
    
    return parser.parse_args()

def run_profiles(args):
    if args.profiles_command == "new":
        new_template(args.name, args.src)
    elif args.profiles_command == "edit":
        edit_template(args.name, args.editor)
    elif args.profiles_command == "del":
        del_template(args.name)
    elif args.profiles_command == "init":
        init_template(args.name, args.public)
    elif args.profiles_command == "sync":
        sync_template()
    elif args.profiles_command == "clone":
        clone_template(args.remote, args.force)

def run_templates(args):
    if args.templates_command == "new":
        new_template(args.name, args.src)
    elif args.templates_command == "edit":
        edit_template(args.name, args.editor)
    elif args.templates_command == "del":
        del_template(args.name)
    elif args.templates_command == "init":
        init_template(args.name, args.public)
    elif args.templates_command == "sync":
        sync_template(args.name)
    elif args.templates_command == "clone":
        clone_template(args.remote, args.name, args.force)

def main():
    args = get_args()

    if args.command == "build":
        compile_pdf(
            profile=args.profile,
            template=args.template,
            output_name=args.output
        )

    elif args.command == "profiles":
        run_profiles(args)
    
    elif args.command == "templates":
        run_templates(args)