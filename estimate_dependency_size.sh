#!/bin/bash
# by rubo77: https://stackoverflow.com/a/68278901/1069083

mkdir -p /tmp/pip-size
for i in $(pip-sync -n requirements.txt|tail -n +2); do
  echo -ne "$i:\t"
  wget --quiet -O /tmp/pip-size/$i https://pypi.org/pypi/$i/json
  cat /tmp/pip-size/$i | jq 'last(.releases[])'[].size | paste -sd+ | bc > /tmp/pip-size/$i.size
  cat /tmp/pip-size/$i.size | awk '{$1=$1/1024/1024; print $1,"MB";}'
done
echo -e "--------\ntotal:"
cat /tmp/pip-size/*.size  | paste -sd+ | bc | awk '{$1=$1/1024/1024; print $1,"MB";}';