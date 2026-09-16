"""Create a fresh output folder inside an explicitly identified existing session."""

import argparse
from datetime import datetime, timezone
import json
import sys
import tempfile

from session_reader import ReaderError, resolve_session_directory


def create_output_directory(*, session_id=None, session_root=None, session_dir=None):
    directory = resolve_session_directory(
        session_id=session_id, session_root=session_root, session_dir=session_dir,
    )
    prefix = "wiki-output-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-"
    output = tempfile.mkdtemp(prefix=prefix, dir=directory)
    return {"status": "created", "output_directory": output}


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ReaderError("invalid_arguments")


def main(argv=None):
    parser = Parser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--session-id")
    source.add_argument("--session-dir")
    parser.add_argument("--session-root")
    try:
        args = parser.parse_args(argv)
        result = create_output_directory(
            session_id=args.session_id, session_root=args.session_root,
            session_dir=args.session_dir,
        )
    except ReaderError as error:
        print(json.dumps({"status": "failed", "error": error.code}))
        return 1
    except OSError:
        print(json.dumps({"status": "failed", "error": "output_directory_unavailable"}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
