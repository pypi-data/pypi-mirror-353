import subprocess
from pathlib import Path
import argparse


def git_init():
    if Path(".git").exists():
        return "✅ Git repo already initialized."
    res = subprocess.run(["git", "init"], capture_output=True, text=True, check=True)
    return res.stdout


def git_remote(config_file="plan.txt"):
    config_path = Path.cwd() / config_file
    if not config_path.exists():
        raise FileNotFoundError(f"Missing '{config_file}' in project directory.")

    config = {}
    with open(config_path, "r") as f:
        exec(f.read(), {}, config)

    username = config.get("username", "").strip()
    repo = config.get("repo", "").strip()
    if not username or not repo:
        raise ValueError(f"Invalid or missing 'username' or 'repo' in {config_file}")

    url = f"https://github.com/{username}/{repo}.git"

    remotes = subprocess.run(
        ["git", "remote"], capture_output=True, text=True, check=True
    ).stdout.split()

    if "origin" in remotes:
        return "✅ Remote 'origin' already exists."
    else:
        res = subprocess.run(
            ["git", "remote", "add", "origin", url], capture_output=True, text=True, check=True
        )
        return f"🔗 Added remote: {url}"


def git_add():
    res = subprocess.run(["git", "add", "."], capture_output=True, text=True, check=True)
    return "➕ Staged all files."


def git_commit():
    message = input("💬 Enter commit message: ").strip()
    if not message:
        message = "Update commit"
    res = subprocess.run(
        ["git", "commit", "-m", message], capture_output=True, text=True
    )
    if res.returncode != 0:
        # Usually no changes to commit
        return "⚠️ No changes to commit."
    return f"📦 Commit done: {message}"

def git_branch():
    res = subprocess.run(
        ["git", "branch", "-M", "main"], capture_output=True, text=True
    )
    if res.returncode == 0:
        return "🌿 Renamed branch to 'main'."
    else:
        return f"⚠️ Failed to rename branch. Reason: {res.stderr}"


def git_push():
        res = subprocess.run(
            ["git", "push", "-u", "origin", "main" , "--force"],
            capture_output=True, text=True
        )
        if res.returncode != 0:
            print("❌ Git push failed:")
            print(res.stderr)
            raise subprocess.CalledProcessError(res.returncode, res.args, output=res.stdout, stderr=res.stderr)
        return "🚀 Code pushed to GitHub."



def thallu_main(update_only=False):
    if not update_only:
        print(git_init())
        print(git_remote())
        print(git_add())
        print(git_commit())
        print(git_branch())
    else:
        print(git_add())
        print(git_commit())
    
    print(git_push())


def main():
    parser = argparse.ArgumentParser(description="Git automation tool: thallu")
    parser.add_argument(
        "-u", "--update", action="store_true", help="Run update (add, commit, push) only"
    )
    args = parser.parse_args()

    thallu_main(update_only=args.update)

if __name__ == "__main__":
    main()
