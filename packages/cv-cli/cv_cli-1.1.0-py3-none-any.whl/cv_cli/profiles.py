from .io import edit_file
from .git import git_init, git_sync, git_clone
from .constants import PROFILES_DIR

def new_template(profile_name, src_profile):
    profile_path = PROFILES_DIR / f"{profile_name}.yaml"

    if profile_path.exists():
        print(f"[Error]: Profile {profile_name} already exists.")
        return
    
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile_path.touch()
    if src_profile:
        src_path = PROFILES_DIR / f"{src_profile}.yaml"
        if not src_path.exists():
            print(f"[Error]: Source profile {profile_name} does not exist.")
            return
        profile_path.write_text(src_path.read_text())

def edit_template(profile_name, editor_cmd):
    profile_path = PROFILES_DIR
    if profile_name:
        profile_path = profile_path / f"{profile_name}.yaml"

    if not profile_path.exists():
        print(f"[Error]: Profile {profile_name} does not exist.")
        return
    edit_file(profile_path, editor_cmd)

def del_template(profile_name):
    profile_path = PROFILES_DIR / f"{profile_name}.yaml"

    if not profile_path.exists():
        print(f"[Error]: Profile {profile_name} does not exist.")
    profile_path.unlink(missing_ok=True)

def init_template(repo_name, public:bool):
    git_init(PROFILES_DIR, repo_name, public)

def sync_template():
    git_sync(PROFILES_DIR)

def clone_template(remote, force:bool):
    git_clone(remote, PROFILES_DIR, force)