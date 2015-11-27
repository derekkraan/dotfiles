alias r='rbenv local 2.0.0-p195'

alias sc='script/console'
alias sg='script/generate'
alias sd='script/destroy'

alias migrate='rake db:migrate db:test:clone'

alias be='bundle exec'

alias cl='for file in $(find . -regex ".*\.log"); do echo > $file; done'

alias pspec='DISABLE_SPRING=1 rake spec'
