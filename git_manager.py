import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

# --- Autocomplete Combobox class ---
class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self['values'] = self._completion_list
        self.bind('<KeyRelease>', self.handle_keyrelease)

    def autocomplete(self, delta=0):
        value = self.get()
        if value == '':
            self['values'] = self._completion_list
        else:
            data = []
            for item in self._completion_list:
                if item.lower().startswith(value.lower()):
                    data.append(item)
            self['values'] = data
        if self['values']:
            self.event_generate('<Down>')

    def handle_keyrelease(self, event):
        if event.keysym in ('BackSpace', 'Left', 'Right', 'Up', 'Down', 'Return'):
            return
        self.autocomplete()

# --- Save/load last directory ---
def get_last_dir():
    try:
        with open("last_dir.txt", "r") as f:
            return f.read().strip()
    except Exception:
        return ""

def set_last_dir(folder):
    try:
        with open("last_dir.txt", "w") as f:
            f.write(folder)
    except Exception:
        pass

# --- Git helpers ---
def is_git_repo(path):
    return os.path.exists(os.path.join(path, ".git"))

def find_all_git_repos(root, max_depth=2):
    repos = []
    for dirpath, dirnames, filenames in os.walk(root):
        depth = dirpath[len(root):].count(os.sep)
        if depth > max_depth:
            dirnames[:] = []
            continue
        if is_git_repo(dirpath):
            repos.append(dirpath)
    return repos

def get_current_branch(repo):
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        branch = result.stdout.strip()
        return branch if branch else "unknown"
    except Exception:
        return "error"

def list_branches(repo):
    try:
        result = subprocess.run(
            ["git", "branch", "-a", "--format=%(refname:short)"],
            cwd=repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        branches = [b.strip() for b in result.stdout.splitlines() if b.strip()]
        return sorted(list(set(branches)))
    except Exception:
        return []

def clear_repo_rows(repo_frame):
    for widget in repo_frame.winfo_children():
        widget.destroy()

def build_repo_table(repo_frame, repos, repo_data, output):
    clear_repo_rows(repo_frame)
    headers = ["Repository Path", "Current Branch", "Target Branch"]
    for col, header in enumerate(headers):
        lbl = tk.Label(repo_frame, text=header, borderwidth=1, relief="raised", width=50 if col == 0 else 16)
        lbl.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

    for idx, repo in enumerate(repos):
        branch = get_current_branch(repo)
        branches = list_branches(repo)
        repo_data[repo] = {"current": branch, "all": branches, "target_var": tk.StringVar(value=branch)}
        # Repo path
        tk.Label(repo_frame, text=repo, anchor="w", borderwidth=1, relief="solid", width=50)\
            .grid(row=idx+1, column=0, sticky="nsew", padx=1, pady=1)
        # Current branch
        tk.Label(repo_frame, text=branch, anchor="w", borderwidth=1, relief="solid", width=16)\
            .grid(row=idx+1, column=1, sticky="nsew", padx=1, pady=1)
        # Target branch autocomplete combobox
        cmb = AutocompleteCombobox(repo_frame, textvariable=repo_data[repo]["target_var"], width=14)
        cmb.set_completion_list(branches)
        cmb.grid(row=idx+1, column=2, sticky="nsew", padx=1, pady=1)

def choose_dir(dir_entry, repo_frame, repo_data, output, depth_entry):
    folder = filedialog.askdirectory(initialdir=get_last_dir() or os.getcwd())
    if folder:
        set_last_dir(folder)
        dir_entry.delete(0, tk.END)
        dir_entry.insert(0, folder)
        try:
            depth = int(depth_entry.get())
        except ValueError:
            depth = 2
        repos = find_all_git_repos(folder, depth)
        build_repo_table(repo_frame, repos, repo_data, output)
        output.insert(tk.END, f"Found {len(repos)} repositories.\n")
        output.see(tk.END)
        repo_data["repos"] = repos

def switch_selected_branches(repo_frame, repo_data, output):
    repos = repo_data.get("repos", [])
    for idx, repo in enumerate(repos):
        target_branch = repo_data[repo]["target_var"].get().strip()
        if not target_branch:
            output.insert(tk.END, f"No branch selected for {repo}.\n")
            continue
        output.insert(tk.END, f"Switching {repo} to branch '{target_branch}'...\n")
        try:
            result = subprocess.run(
                ["git", "checkout", target_branch],
                cwd=repo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                output.insert(tk.END, f"Switched to {target_branch} successfully.\n")
            else:
                output.insert(tk.END, f"Failed to switch: {result.stderr.strip()}\n")
        except Exception as e:
            output.insert(tk.END, f"Error: {e}\n")
        output.see(tk.END)
    build_repo_table(repo_frame, repos, repo_data, output)

def pull_all_repos(repo_data, output):
    repos = repo_data.get("repos", [])
    for repo in repos:
        output.insert(tk.END, f"Running 'git pull' in {repo}...\n")
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=repo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output.insert(tk.END, result.stdout)
            if result.stderr:
                output.insert(tk.END, result.stderr)
        except Exception as e:
            output.insert(tk.END, f"Error pulling in {repo}: {e}\n")
        output.see(tk.END)

def apply_branch_to_all(apply_entry, repo_data, repo_frame, output):
    branch_name = apply_entry.get().strip()
    repos = repo_data.get("repos", [])
    changed = 0
    for repo in repos:
        if branch_name in repo_data[repo]["all"]:
            repo_data[repo]["target_var"].set(branch_name)
            changed += 1
        else:
            output.insert(tk.END, f"Branch '{branch_name}' not found in {repo}.\n")
    output.insert(tk.END, f"Set branch '{branch_name}' for {changed} repositories.\n")
    output.see(tk.END)

def main():
    root = tk.Tk()
    root.title("Git Multi-Repo Branch Manager")

    control_frame = tk.Frame(root)
    control_frame.pack(fill=tk.X, padx=10, pady=6)
    tk.Label(control_frame, text="Root Folder:").pack(side=tk.LEFT)
    dir_entry = tk.Entry(control_frame, width=40)
    dir_entry.pack(side=tk.LEFT, padx=4)

    # On load: fill with last used dir, if exists
    last_dir = get_last_dir()
    if last_dir:
        dir_entry.insert(0, last_dir)

    repo_frame = tk.Frame(root)
    repo_frame.pack(fill=tk.X, padx=10, pady=(0,6))

    repo_data = {}

    tk.Button(control_frame, text="Browse", command=lambda: choose_dir(dir_entry, repo_frame, repo_data, output, depth_entry))\
        .pack(side=tk.LEFT, padx=6)
    tk.Label(control_frame, text="Max Depth:").pack(side=tk.LEFT)
    depth_entry = tk.Entry(control_frame, width=5)
    depth_entry.insert(0, "2")
    depth_entry.pack(side=tk.LEFT, padx=4)

    # Apply-to-all frame
    apply_frame = tk.Frame(root)
    apply_frame.pack(fill=tk.X, padx=10, pady=(0,2))
    tk.Label(apply_frame, text="Set Target Branch for ALL:").pack(side=tk.LEFT)
    apply_entry = tk.Entry(apply_frame, width=20)
    apply_entry.pack(side=tk.LEFT, padx=4)
    tk.Button(apply_frame, text="Apply", command=lambda: apply_branch_to_all(apply_entry, repo_data, repo_frame, output))\
        .pack(side=tk.LEFT, padx=4)

    switch_frame = tk.Frame(root)
    switch_frame.pack(fill=tk.X, padx=10)
    tk.Button(switch_frame, text="Switch All Selected", command=lambda: switch_selected_branches(repo_frame, repo_data, output))\
        .pack(side=tk.LEFT, padx=4)
    tk.Button(switch_frame, text="Pull All", command=lambda: pull_all_repos(repo_data, output))\
        .pack(side=tk.LEFT, padx=4)

    output = scrolledtext.ScrolledText(root, width=100, height=12)
    output.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

    # Auto-load table if last_dir exists
    if last_dir:
        try:
            depth = int(depth_entry.get())
        except ValueError:
            depth = 2
        repos = find_all_git_repos(last_dir, depth)
        build_repo_table(repo_frame, repos, repo_data, output)
        output.insert(tk.END, f"Found {len(repos)} repositories.\n")
        output.see(tk.END)
        repo_data["repos"] = repos

    root.mainloop()

if __name__ == "__main__":
    main()
