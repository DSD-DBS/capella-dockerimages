#!/usr/bin/env zsh

# shell editor:
export EDITOR=nvim
export VISUAL=nvim

export PATH=$HOME/.local/bin:/opt/capella:$PATH
export POWERLEVEL9K_DISABLE_CONFIGURATION_WIZARD=true
export ZSH="$HOME/.oh-my-zsh"
export ZSH_DISABLE_COMPFIX=true
ZSH_THEME="powerlevel10k/powerlevel10k"
plugins=(
    git
)
source $ZSH/oh-my-zsh.sh

setopt autopushd    # cd automatically pushes old dir onto dir stack
setopt pushd_ignore_dups # don't push multiple copies of the same directory onto the directory stack

setopt CDABLE_VARS  # expand the expression (allows 'cd -2/tmp')

# shell history:
export SAVEHIST=1000000         # No of cmds stored in hist file
export HISTSIZE=50000             # No of cmds loaded into RAM from hist file
export HISTFILE=$HOME/.zsh_history
setopt INC_APPEND_HISTORY       # cmds are added to the history immediately

# poetry
export POETRY_VIRTUALENVS_IN_PROJECT=true

# home/ end keys:
bindkey "^[[H" beginning-of-line
bindkey "^[[F" end-of-line
bindkey "^[[1;3C" forward-word
bindkey "^[[1;3D" backward-word

# Load version control information
autoload -Uz vcs_info
precmd() { vcs_info }

# Format the vcs_info_msg_0_ variable
zstyle ':vcs_info:git:*' formats '%F{9}%b%f'
 
# Set up the prompt (with git branch name)
setopt PROMPT_SUBST
NEWLINE=$'\n'
# PROMPT='%(?.%F{green}✔.%F{red}%?)%f %F{2}%n @ %m%f %F{14}${PWD/#$HOME/~}%f ${vcs_info_msg_0_}${NEWLINE}\$ '
# RPROMPT='$(python3 -c "import sys; print(sys.executable)") - $(python3 -V)'

cd_func() {
  local x2 the_new_dir adir index
  local -i cnt

  if [[ $1 ==  "--" ]]; then
    dirs -v
    return 0
  fi
  the_new_dir=$1
  [[ -z $1 ]] && the_new_dir=$HOME

  if [[ ${the_new_dir:0:1} == '-' ]]; then
    #
    # Extract dir N from dirs
    index=${the_new_dir:1}
    [[ -z $index ]] && index=1
    adir=$(dirs +$index)
    [[ -z $adir ]] && return 1
    the_new_dir=$adir
  fi
  #
  # '~' has to be substituted by ${HOME}
  [[ ${the_new_dir:0:1} == '~' ]] && the_new_dir="${HOME}${the_new_dir:1}"

  #
  # Now change to the new dir and add to the top of the stack
  pushd "${the_new_dir}" > /dev/null
  [[ $? -ne 0 ]] && return 1
  the_new_dir=$(pwd)
  #
  # Trim down everything beyond 11th entry
  popd -n +11 2>/dev/null 1>/dev/null
  #
  # Remove any other occurence of this dir, skipping the top of the stack
  for ((cnt=1; cnt <= 10; cnt++)); do
    x2=$(dirs +${cnt} 2>/dev/null)
    [[ $? -ne 0 ]] && return 0
    [[ ${x2:0:1} == '~' ]] && x2="${HOME}${x2:1}"
    if [[ "${x2}" == "${the_new_dir}" ]]; then
      popd -n +$cnt 2>/dev/null 1>/dev/null
      cnt=cnt-1
    fi
  done
  return 0
}
alias cd=cd_func

# git:
alias add='git add'
alias checkout='git checkout'
alias commit='git commit'
alias gitdiff='git difftool --no-symlinks'
alias gitdiffdir='git difftool --no-symlinks --dir-diff'
alias gitreset='git checkout -- .; git reset --hard HEAD; git clean -d --force'
alias pull='git pull'
alias push='git push'
alias st='git status .'
alias up='git add .; git commit -m "WIP"; git push'

alias grep='grep --color --exclude-dir=.git --exclude-dir=.svn'

# fzf:
FZF_DEFAULT_OPTS='--history-size=10000'
alias fd='FZF_DEFAULT_COMMAND="find . -type d" fzf'
alias ff='FZF_DEFAULT_COMMAND="find . -type f" fzf --preview "bat --style=numbers --color=always --line-range :500 {}"'
alias vf='FZF_DEFAULT_COMMAND=find . -type f | grep -v .git; nvim $(fzf --preview "bat --style=numbers --color=always --line-range :500 {}"); unset FZF_DEFAULT_COMMAND'

# misc:
alias erc='nvim $HOME/.zshrc'
alias pslong='ps -eo pid,nice,user,command'
alias psshort='ps -eo pid,nice,user,comm'
alias src='source $HOME/.zshrc'

alias cl='clear'
alias ls='ls --color'
alias l='ls -lh'
alias ll='ls -lha'
alias vi='nvim'
alias vidiff='nvim -d'
alias vim='nvim'

alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
alias ......='cd ../../../../..'

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh  # installed by: $ ~/opt/fzf/install

fpath=(~/.zsh $fpath)
# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi
