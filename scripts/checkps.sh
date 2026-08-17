#!/usr/bin/env bash

set -uo pipefail

PATH="${ZIRCON_PATH:-/usr/local/bin:/usr/bin:/bin}"
export PATH

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
APP_DIR="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
APP_FILE="$APP_DIR/zrmine.py"
APP_NAME="$(basename -- "$APP_FILE")"

BOT_ENV="${ZIRCON_BOT_ENV:-production}"
PYTHON_BIN="${ZIRCON_PYTHON_BIN:-/usr/bin/python3}"
STARTUP_GRACE_SECONDS="${ZIRCON_STARTUP_GRACE_SECONDS:-3}"

LOG_DIR="${ZIRCON_LOG_DIR:-$APP_DIR/log}"
APP_LOG="${ZIRCON_APP_LOG:-$APP_DIR/nohup.out}"
WATCHDOG_LOG="${ZIRCON_WATCHDOG_LOG:-$LOG_DIR/checkps.log}"
RUN_DIR="${ZIRCON_RUN_DIR:-$APP_DIR/run}"
PID_FILE="$RUN_DIR/zrmine.pid"
LOCK_FILE="$RUN_DIR/checkps.lock"
ENV_FILE="$APP_DIR/.env.$BOT_ENV"

log_message() {
    printf '%s %s\n' "$(date '+%Y/%m/%d %H:%M:%S')" "$*" >> "$WATCHDOG_LOG"
}

configuration_error=""
validate_configuration() {
    if [[ ! -x "$PYTHON_BIN" ]]; then
        configuration_error="Python not executable: $PYTHON_BIN"
        return 1
    fi

    if [[ ! -r "$APP_FILE" ]]; then
        configuration_error="application not readable: $APP_FILE"
        return 1
    fi

    if [[ ! -r "$ENV_FILE" ]]; then
        configuration_error="environment file not readable: $ENV_FILE"
        return 1
    fi

    if ! grep -Eq '^[[:space:]]*(export[[:space:]]+)?MCH[[:space:]]*=' "$ENV_FILE"; then
        configuration_error="MCH is not defined in $ENV_FILE"
        return 1
    fi

    if ! grep -Eq '^[[:space:]]*(export[[:space:]]+)?MINING_EXCELLENT_(CH|CHAT)[[:space:]]*=' "$ENV_FILE"; then
        configuration_error="MINING_EXCELLENT_CH is not defined in $ENV_FILE"
        return 1
    fi

    return 0
}

process_matches_app() {
    local pid="$1"
    local cmdline_file="/proc/$pid/cmdline"
    local process_cwd

    [[ -r "$cmdline_file" ]] || return 1

    if tr '\0' '\n' < "$cmdline_file" 2>/dev/null | grep -Fqx -- "$APP_FILE"; then
        return 0
    fi

    process_cwd="$(readlink -f -- "/proc/$pid/cwd" 2>/dev/null || true)"
    [[ "$process_cwd" == "$APP_DIR" ]] || return 1

    tr '\0' '\n' < "$cmdline_file" 2>/dev/null | grep -Fqx -- "$APP_NAME"
}

find_running_pid() {
    local pid
    local proc_dir

    if [[ -r "$PID_FILE" ]]; then
        pid="$(<"$PID_FILE")"
        if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null && process_matches_app "$pid"; then
            printf '%s\n' "$pid"
            return 0
        fi
        rm -f -- "$PID_FILE"
    fi

    for proc_dir in /proc/[0-9]*; do
        pid="${proc_dir##*/}"
        if kill -0 "$pid" 2>/dev/null && process_matches_app "$pid"; then
            printf '%s\n' "$pid"
            return 0
        fi
    done

    return 1
}

if [[ "${1:-}" == "--check" ]]; then
    if validate_configuration; then
        printf 'Watchdog configuration is valid (app: %s, ENV: %s)\n' "$APP_FILE" "$BOT_ENV"
        exit 0
    fi
    printf 'Watchdog configuration error: %s\n' "$configuration_error" >&2
    exit 1
fi

mkdir -p -- "$LOG_DIR" "$RUN_DIR"

if command -v flock >/dev/null 2>&1; then
    exec 9>"$LOCK_FILE"
    flock -n 9 || exit 0
fi

running_pid="$(find_running_pid || true)"
if [[ -n "$running_pid" ]]; then
    printf '%s\n' "$running_pid" > "$PID_FILE"
    log_message "Process $APP_NAME is OK (PID: $running_pid)"
    exit 0
fi

log_message "Process $APP_NAME is Down.."

if ! validate_configuration; then
    log_message "Process $APP_NAME cannot start: $configuration_error"
    exit 1
fi

log_message "Process $APP_NAME Start!!!! (ENV: $BOT_ENV)"

cd -- "$APP_DIR" || {
    log_message "Process $APP_NAME cannot start: failed to enter $APP_DIR"
    exit 1
}

nohup env ENV="$BOT_ENV" "$PYTHON_BIN" -u "$APP_FILE" >> "$APP_LOG" 2>&1 < /dev/null &
started_pid=$!
printf '%s\n' "$started_pid" > "$PID_FILE"

sleep "$STARTUP_GRACE_SECONDS"

if kill -0 "$started_pid" 2>/dev/null && process_matches_app "$started_pid"; then
    log_message "Process $APP_NAME started successfully (PID: $started_pid)"
    exit 0
fi

wait "$started_pid" 2>/dev/null
exit_code=$?
rm -f -- "$PID_FILE"
if [[ "$exit_code" -eq 0 ]]; then
    exit_code=1
fi
log_message "Process $APP_NAME failed during startup (exit: $exit_code); see $APP_LOG"
exit "$exit_code"
