#!/bin/bash
cd /home/kavia/workspace/code-generation/company-data-qa-platform-2984-2993/qanda_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

