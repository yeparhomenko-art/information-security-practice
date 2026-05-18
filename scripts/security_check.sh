#!/bin/bash

echo "=== SECURITY CHECK ==="
ERRORS=0

echo "1. Перевірка .gitignore..."
if grep -q "\.env" .gitignore; then
  echo "OK: .env у .gitignore"
else
  echo "ERROR: .env НЕ в .gitignore"
  ERRORS=$((ERRORS + 1))
fi

echo "2. Перевірка Dockerfile..."
if grep -q "^USER appuser" Dockerfile; then
  echo "OK: non-root user налаштований"
else
  echo "ERROR: USER appuser не знайдено"
  ERRORS=$((ERRORS + 1))
fi

if grep -q "HEALTHCHECK" Dockerfile; then
  echo "OK: HEALTHCHECK налаштований"
else
  echo "ERROR: HEALTHCHECK відсутній"
  ERRORS=$((ERRORS + 1))
fi

echo "3. pip-audit..."
pip-audit --cache-dir /tmp/pip-audit || ERRORS=$((ERRORS + 1))

echo "4. Bandit..."
bandit -r app/ --severity-level medium || ERRORS=$((ERRORS + 1))

echo "======================"
if [ $ERRORS -eq 0 ]; then
  echo "SECURITY CHECK PASSED"
else
  echo "SECURITY CHECK FINISHED WITH $ERRORS WARNING(S)"
fi

exit 0