# Multi Repo Git Branch Manager

A simple Python GUI to manage branches and pull multiple git repositories at once (supports submodules).

## ✨ Features

- Scan any folder (with subfolders) and find all git repositories (supports submodules)
- See current branch for each repo
- Autocomplete for branch selection (per repo)
- Set target branch for all repos at once (bulk)
- Switch all repos to their selected branches with one click
- "Pull All" — run `git pull` for all repos
- Remembers last-used directory
- Cross-platform (Windows, Linux, macOS — Python 3 required)

## 📷 Screenshot

*(Insert a screenshot or GIF here!)*

## 🚀 Installation

Requires Python 3.x  
Tkinter is included by default in most Python installations.

No install needed — just download the script and run:

```bash
python3 git_manager.py
```

## 🛠 Usage

1. Choose a root folder (`Browse`) to scan for git repositories.
2. See a table with all found repos and their current branches.
3. Use autocomplete in the "Target Branch" column to select a branch for each repo.
4. (Optional) Enter a branch name in the "Set Target Branch for ALL" box and click `Apply` to set it for all.
5. Click `Switch All Selected` to switch all repos.
6. Click `Pull All` to run `git pull` in all repos.
7. All output appears in the log at the bottom.

## ⚡ Example

![screenshot](screenshot.png)  
*(You can add your own screenshot!)*

## 💡 Why?

When working with many git repos or monorepos with submodules, switching branches and updating code can be a pain.  
This tool lets you do it all in one window, safely and quickly.

## 📄 License

MIT License  
See [LICENSE](LICENSE).

## 🤝 Contributing

Pull requests, suggestions, and bug reports are welcome!

*Built with ❤️ using Python and Tkinter*
