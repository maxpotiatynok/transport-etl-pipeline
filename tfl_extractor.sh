#!/bin/zsh
PROJECT=~/PycharmProjects/transport-etl-pipeline
cd "$PROJECT" || exit 1
mkdir -p logs
LOG=logs/pipeline.log

# Writes a UTC-timestamped line to the pipeline log
log() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $1" >> "$LOG" }

log "extractor started"
if "$PROJECT/.venv/bin/python" tfl_extractor.py >> "$LOG" 2>&1; then
    log "extractor finished"
    # Rebuilds StatusIslands only after a successful extraction
    log "transformer started"
    if "$PROJECT/.venv/bin/python" table_transformer.py >> "$LOG" 2>&1; then
        log "transformer finished"
    else
        log "transformer FAILED"
    fi
else
    log "extractor FAILED, transformer skipped"
fi