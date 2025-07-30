# lvim

luavim - a remote control interpreter for neovim

lvim is a remote control for nvim, heavily inspired by neovim-remote (nvr)
by mhinz: https://github.com/mhinz/neovim-remote

## Install

The quickest way to start using lvim is with the [uv](https://github.com/astral-sh/uv)
package manager:

```bash
# See uv README for other installation options
curl -LsSf https://astral.sh/uv/install.sh | sh
```

The `uvx` tool can be used to quickly run Python programs in anonymous
virtual environments:

```bash
alias lvim='uvx --from lvim lvim'
```

With this alias, lvim can be used to start the REPL:

```lua
$ lvim
Neovim v0.11.1+ga9a3981669 running LuaJIT 2.1.1741730670 [Lua 5.1]
PID: 599332 Connection: Socket /tmp/nvim.aemiller/o6ze3D/nvim.599332.0

Info:  %help                   -- or :h lua-guide
Usage: print(vim.fn.getcwd())  -- /home/aemiller/repos/lvim

aemiller@nvim://|⇒
```

## Usage

When run without arguments lvim will "attach" to the nvim instance and
provide a read-eval-print-loop for working with it. This is somewhat similar
to IPython, and is using the same library to implement the prompt itself:
https://github.com/prompt-toolkit/python-prompt-toolkit

```lua
-- By default, execute lua code in the attached nvim instance
aemiller@nvim:~/|⇒ vim.fn.getcwd()
/home/aemiller

-- Run shell commands via nvim with !
aemiller@nvim:~/|⇒ ! ls
bin
README.md
repos

-- Change the nvim working directory via the %cwd "magic" function
aemiller@nvim:~/|⇒ %cwd repos/lvim
/home/aemiller/repos/lvim

-- Change the lvim current directory via the %cd "magic" function
aemiller@nvim:~/|⇒ %cd repos/lvim
/home/aemiller/repos/lvim
```

See the directories section below for more info on navigation.

```lua
-- Run vim ex commands with :
aemiller@nvim:~/repos/lvim|⇒ :edit README.md
```


## Completion

Pressing `<Tab>` in the prompt will provide auto-completion for the relevant
command type via nvim RPC. Otherwise it functions similarly to the cmdline
provided in nvim, with changes to the environment persisting between lines.

## Discovery

Discovery of nvim is based on the environment variable `$NVIM`, set in either
the shell environment, or the tmux environment (when `$TMUX` is also set).
Using the tmux environment allows for nvim in another window to manage the
state of this variable for all windows:

```lua
local connection = vim.fn.serverlist()[1]
vim.system({ "tmux", "set-environment", "NVIM", connection })
```

By default, if an existing nvim instance cannot be found, lvim will start
one in a background thread using a socket in the local tmpdir:

```lua
$ tmux set-environment -u NVIM ; unset $NVIM ; lvim
auto starting nvim with: /bin/env nvim --headless --listen '/tmp/lvim.aemiller/tmpu853ocxs/nvim.231284.0'
Neovim v0.11.1+ga9a3981669 running LuaJIT 2.1.1741730670 [Lua 5.1]
PID: 231309 Connection: Listen /tmp/lvim.aemiller/tmpu853ocxs/nvim.231284.0

Info:  %help                   -- or :h lua-guide
Usage: print(vim.fn.getcwd())  -- /home/aemiller

-- Functions as an otherwise normal nvim instance managed by lvim
aemiller@nvim:~/|⇒ :ls
  1 %a   "[No Name]"                    line 1
aemiller@nvim:~/|⇒ exit
auto stopping nvim
```

lvim must have an instance of nvim to run against. If the auto listen server
does not work, the --embed option can be provided to use nvim's built in
stdin/stdout based headless instance. Because this only allows for one RPC
client, notifications via the broker are not enabled.

An explicit nvim server connection can be provided with the --server option.

Running lvim with --clean will start nvim with --clean, skipping user data
and state.

## Directories

Since nvim and lvim are separate processes, they have separate working
directories:

```bash
# Start nvim
~/repos/lvim $ nvim
# Start lvim
~/ $ lvim
aemiller@nvim://|⇒ %cwd
"/home/aemiller/repos/lvim"
aemiller@nvim://|⇒ %cd
"/home/aemiller/repos/lvim"
```

lvim also has a "pinned" directory, which defaults to the current working
dir of the attached nvim instance. This directory and all paths relative
to it will be formattted with a "//" prefix:

```bash
aemiller@nvim://|⇒ %cd! src
"/home/aemiller/repos/lvim/src"
aemiller@nvim://src|⇒ %cd src
```

The pinned directory can be updated with %pin:

```bash
aemiller@nvim://src|⇒ %pin!
aemiller@nvim://|⇒ %pin ..
aemiller@nvim://src|⇒
```

To disable pinning, run lvim with the --no-pin flag.

By default, lvim will change it's working directory to match
the one set in the attached nvim instance, but this can be disabled with
the --no-cd flag:

```bash
~/ $ lvim --no-cd
aemiller@nvim:~/!|⇒ %cwd
"/home/aemiller/repos/lvim"
aemiller@nvim:~/!|⇒ %cd
"/home/aemiller"
```

The prompt will always show the lvim current directory (cd). If this is not
the same as the nvim cwd, an ! is appended to the end of the path:

```bash
aemiller@nvim:~/!|⇒ %cd repos/lvim
"/home/aemiller/repos/lvim"
aemiller@nvim://|⇒
```

To change both dirs at the same time, use the bang form:

```bash
aemiller@nvim://|⇒ %cd! src
"/home/aemiller/repos/lvim/src"
aemiller@nvim://src|⇒
```

With no args, this will sync the cd and cwd:

```bash
aemiller@nvim://|⇒ %cd src
"/home/aemiller/repos/lvim/src"
aemiller@nvim://src!|⇒ %cd!
aemiller@nvim://src|⇒
```

## Config

lvim uses a configuration file format largely based on the one provided by
ptpython. An example configuration with some sane defaults can be found in
the repo at [example/config.py](example/config.py)

This file is read from the config home directory, set with --config or the
`LVIM_CONFIG_HOME` environment variable. See the help text for this option for
the default location on this machine.

## Python REPL

If lvim is started with the `--py` or `--ipy` flags, it will instead start
an instance of `ptpython` or `ptipython` with the various components
of lvim available as globals:

* `vim` - Connected pynvim API client
* `_session` - NvimSession backing the `vim` client
* `broker` - NvimBroker handling RPC notifications
* `repl` - PyREPL instance for the running interpreter

This is useful for debugging and working with nvim's Python SDK. The
config file is loaded from `pyconfig.py` in the `LVIM_CONFIG_HOME`.
An example configuration can be found at [example/pyconfig.py](example/pyconfig.py)

`ptpython` is required for this mode, and can be installed via the
`py` optional dependency set for lvim. `ptipython` also requires
the `IPython` package to be installed, which is in the optional
dependency set `ipy`:

```bash
alias pylvim='uvx --from "lvim[py]" lvim --py'
alias ipylvim='uvx --from "lvim[ipy]" lvim --ipy'
```

## Development

All development on lvim can be handled through the `uv` tool:

```bash
uv sync --dev --all-extras
Resolved 43 packages in 0.54ms
Audited 41 packages in 0.06ms
```

Invocations of `uv` will read configuration from the [pyproject.toml](pyproject.toml)
file and configure a virtual environment with `lvim` and it's dependencies under
`.venv` in the repository.

### nvim

When testing it is useful to run a separate nvim instance without user config:

```bash
lvim --clean --listen auto
```

### Type Checking

Ensure no type errors are present with [pyre](https://github.com/facebook/pyre-check):

```bash
uv run pyre check
ƛ No type errors found
```

**Note**: Pyre daemonizes itself on first run for faster subsequent executions. Be
sure to shut it down with `uv run pyre stop` when finished.

## Formatting

Format code with the [ruff](https://github.com/astral-sh/ruff) formatter:

```bash
uv run ruff format
15 files left unchanged
```
