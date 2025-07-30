# Kuba

The kuba-amazing kubectl companion with [fzf](https://github.com/junegunn/fzf), [fx](https://github.com/antonmedv/fx), [aliases](https://github.com/ahmetb/kubectl-aliases), and more!

<p align="center"><img src="https://raw.githubusercontent.com/hcgatewood/kuba/main/assets/logo_transparent_purple.png" alt="Kuba logo" width="300"/></p>

## Features

<p align="center"><img src="https://raw.githubusercontent.com/hcgatewood/kuba/main/assets/demo.gif" alt="Kuba demo" width="1000"/></p>

- ☁️ **Fuzzy commands** like get and describe
- 🧠 **Guess pod containers** automagically
- ✈️ **Cross namespaces and clusters** in one command
- ⚡ **Cut down on keystrokes** with an alias language
- 🧪 **Simulate scheduling** without the scheduler
- 🔁 **And lots more**!

## Install

Quick-install:

```bash
pip install kuba
```

Kuba makes use of the following tools you'll likely want to install as well: [fzf](https://github.com/junegunn/fzf#installation), [fx](https://fx.wtf/install), and [krew](https://krew.sigs.k8s.io/docs/user-guide/setup/install) for [stern](https://github.com/stern/stern) and [lineage](https://github.com/tohjustin/kube-lineage). On macOS, you can install these tools with [Homebrew](https://brew.sh/):

```bash
brew install fzf fx krew && kubectl krew install stern lineage
```

## Usage

Start by using `kuba get` and `kuba describe` as a ~drop-in replacements for `kubectl get` and `kubectl describe`.

Then check out the help pages for next steps, including using the alias language.
