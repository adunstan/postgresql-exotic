#!/bin/bash
# Show client- and server-side messages in the given language.
# Usage: [PGWT=/path/to/pg/tree] smoke.sh LANGCODE      (en@piglatin, eo, tlh)
set -eu
lang=$1
wt=${PGWT:-/home/andrew/pgl/pg_head-nls-demo}
inst=$wt/builddir-cassert/tmp_install/usr/local/pgsql
bin=$inst/bin
run=$wt/builddir-cassert/testrun/nls-demo
data=$run/data
sock=$run/sock
port=54329
# On multiarch hosts (Debian/Ubuntu) the shared libs land in
# lib/<triplet>/ rather than directly under lib/; without the triplet
# component the loader silently falls back to any system libpq.so.5,
# masking the newly built catalogs. Prefer the multiarch dir if present.
libdir=$inst/lib
for d in "$inst"/lib/*/; do
	if [ -e "${d}libpq.so" ]; then
		libdir=${d%/}
		break
	fi
done
export LD_LIBRARY_PATH=$libdir

mkdir -p "$sock"
if [ ! -d "$data" ]; then
	"$bin/initdb" -D "$data" --no-locale -E UTF8 >/dev/null
	cat >> "$data/postgresql.conf" <<EOF
port = $port
unix_socket_directories = '$sock'
listen_addresses = ''
lc_messages = 'en_US.utf8'
EOF
fi

unset LC_ALL LANG
export LANGUAGE=$lang LC_MESSAGES=en_US.utf8 LC_CTYPE=en_US.utf8
psql=("$bin/psql" -X -h "$sock" -p "$port" -d postgres)

echo "== libpq: connection failure"
"$bin/psql" -X -h "$run/nonexistent" -p "$port" -d postgres -c 'SELECT 1' 2>&1 || true
echo "== psql --help"
"$bin/psql" --help | head -3

"$bin/pg_ctl" -D "$data" -l "$run/server-$lang.log" -w start >/dev/null
trap '"$bin/pg_ctl" -D "$data" -m fast -w stop >/dev/null' EXIT

echo "== backend: division by zero"
"${psql[@]}" -c 'SELECT 1/0' 2>&1 || true
echo "== backend: missing table"
"${psql[@]}" -c 'SELECT * FROM no_such_table' 2>&1 || true
echo "== psql: invalid command"
"${psql[@]}" -c '\foo' 2>&1 || true
echo "== psql \\?"
"${psql[@]}" -c '\?' | head -5
