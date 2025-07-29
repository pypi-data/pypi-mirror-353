# shellcheck shell=bash

if test -n "${HOME_IMPURE-}"; then
  export HOME="${HOME_IMPURE}"
fi

function labels {
  python '__argSrcLabels__/labels/core/cli.py' "$@"
}
