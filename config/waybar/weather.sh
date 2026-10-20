#!/usr/bin/env bash
IFS='|' read -r temp sym cond rise set < <(curl -sf --max-time 10 'https://wttr.in/Utrecht?format=%t|%x|%C|%S|%s')
[ -z "$temp" ] && exit 0

case "$sym" in
  o) alt=sunny ;;
  m) alt=partly ;;
  mm|mmm) alt=cloudy ;;
  =) alt=fog ;;
  /|.) alt=rain ;;
  ///|//) alt=pouring ;;
  x|x/) alt=sleet ;;
  '*'|'*/') alt=snow ;;
  '**'|'*/*') alt=heavysnow ;;
  '/!/'|'!/'|'*!*') alt=thunder ;;
  *) alt=unknown ;;
esac

now=$(date +%H:%M:%S)
if [[ "$now" < "$rise" || "$now" > "$set" ]] && [[ $alt == sunny || $alt == partly ]]; then
  alt="night-$alt"
fi

printf '{"text":"%s","alt":"%s","tooltip":"%s"}\n' "${temp#+}" "$alt" "$cond"
