autoload colors && colors
# cheers, @ehrenmurdick
# http://github.com/ehrenmurdick/config/blob/master/zsh/prompt.zsh

if (( $+commands[git] ))
then
  git="$commands[git]"
else
  git="/usr/bin/git"
fi

git_branch() {
  echo $($git symbolic-ref HEAD 2>/dev/null | awk -F/ {'print $NF'})
}

git_dirty() {
  st=$($git status 2>/dev/null | head -n 1)
  if [[ $st == "" ]]
  then
    echo ""
  else
    if [[ "$st" =~ ^nothing ]]
    then
      echo "(%{$fg_bold[green]%}$(git_prompt_info)%{$reset_color%})"
    else
      echo "(%{$fg_bold[red]%}$(git_prompt_info)%{$reset_color%})"
    fi
  fi
}

git_prompt_info () {
 ref=$($git symbolic-ref HEAD 2>/dev/null) || return
# echo "(%{\e[0;33m%}${ref#refs/heads/}%{\e[0m%})"
 echo "${ref#refs/heads/}"
}

unpushed () {
  $git cherry -v @{upstream} 2>/dev/null
}

need_push () {
  if [[ $(unpushed) == "" ]]
  then
    echo " "
  else
    echo " with %{$fg_bold[magenta]%}unpushed%{$reset_color%} "
  fi
}

rb_prompt(){
  if (( $+commands[rbenv] ))
  then
	  echo "%{$fg_bold[yellow]%}$(rbenv version | awk '{print $1}')%{$reset_color%}"
	else
	  echo ""
  fi
}

git_repo_info(){
  git rev-parse --show-toplevel 2> /dev/null | sed 's|.*/||'
}

git_repo(){
  if [ -n "$(git_repo_info)" ]; then
    echo "%{$fg_bold[green]%}[$(git_repo_info)]%{$reset_color%} "
  else
    echo ""
  fi
}

failure(){
  if [ $? -ne 0 ]; then echo "%{$fg_bold[red]%}(×_×)%{$reset_color%} "; fi
}

directory_name(){
  echo "%{$fg_bold[blue]%}%1/%\/%{$reset_color%}"
}

prompt_symbol(){
  echo "%{$fg_bold[red]%}>>%{$reset_color%}"
}

export PROMPT=$'$(failure)$(git_repo)$(directory_name) $(prompt_symbol) '

set_prompt () {
  export RPROMPT="%{$fg_bold[blue]%}%{$reset_color%}"
}

# precmd() {
#   title "zsh" "%m" "%55<...<%~"
#   set_prompt
# }
