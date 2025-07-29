"""
Handler for processing JSON files.
"""

import logging
import subprocess
from pathlib import Path

from l_command.handlers.base import FileHandler
from l_command.utils import smart_pager

# Constants specific to JSON handling
JSON_CONTENT_CHECK_BYTES = 1024
MAX_JSON_SIZE_BYTES = 10 * 1024 * 1024  # 10MB limit for jq processing

logger = logging.getLogger(__name__)


class JsonHandler(FileHandler):
    """Handler for processing JSON files."""

    @classmethod
    def can_handle(cls: type["JsonHandler"], path: Path) -> bool:
        """Check if the path is a JSON file.

        Args:
            path: The path to check.

        Returns:
            True if the path is a JSON file, False otherwise.
        """
        if not path.is_file():
            return False

        # Check by extension
        if path.suffix.lower() == ".json":
            try:
                if path.stat().st_size == 0:
                    return False
            except OSError:
                return False  # Cannot stat, likely doesn't exist or permission error
            return True

        # Check by content
        try:
            with path.open("rb") as f:
                content_start = f.read(JSON_CONTENT_CHECK_BYTES)
                if not content_start:
                    return False
                try:
                    content_text = content_start.decode("utf-8").strip()
                    if content_text.startswith(("{", "[")):
                        return True
                except UnicodeDecodeError:
                    pass
        except OSError:
            pass

        return False

    @classmethod
    def handle(cls: type["JsonHandler"], path: Path) -> None:
        """Display JSON file using jq with fallbacks.

        Args:
            path: The JSON file path to display.
        """
        try:
            file_size = path.stat().st_size
            if file_size == 0:
                # jq empty fails on empty files, treat as non-JSON for display
                print("(Empty file)")  # Indicate it is empty
                return

            if file_size > MAX_JSON_SIZE_BYTES:
                logger.warning(
                    f"File size ({file_size} bytes) exceeds limit "
                    f"({MAX_JSON_SIZE_BYTES} bytes). "
                    f"Falling back to default viewer.",
                )
                from l_command.handlers.default import DefaultFileHandler

                DefaultFileHandler.handle(path)
                return

            # Validate JSON using jq empty
            try:
                subprocess.run(
                    ["jq", "empty", str(path)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                logger.warning(
                    "jq command not found. Falling back to default viewer.",
                )
                from l_command.handlers.default import DefaultFileHandler

                DefaultFileHandler.handle(path)
                return
            except subprocess.CalledProcessError:
                logger.warning(
                    "File identified as JSON but failed validation or is invalid. Falling back to default viewer.",
                )
                from l_command.handlers.default import DefaultFileHandler

                DefaultFileHandler.handle(path)
                return
            except OSError as e:
                logger.error(f"Error running jq: {e}")
                from l_command.handlers.default import DefaultFileHandler

                DefaultFileHandler.handle(path)
                return

            # If validation passes, display formatted JSON with jq using smart_pager
            try:
                # Start jq process with color output
                jq_process = subprocess.Popen(
                    ["jq", "--color-output", ".", str(path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # Use smart_pager to handle the output
                smart_pager(jq_process, ["less", "-R"])

                # Check if jq process failed
                jq_retcode = jq_process.wait()
                if jq_retcode != 0:
                    logger.error(f"jq process exited with code {jq_retcode}")
                    from l_command.handlers.default import DefaultFileHandler

                    DefaultFileHandler.handle(path)

            except subprocess.SubprocessError as e:
                logger.error(f"Error displaying JSON with jq: {e}")
                # Fallback even if formatting fails after validation
                from l_command.handlers.default import DefaultFileHandler

                DefaultFileHandler.handle(path)
            except OSError as e:
                logger.error(f"Error running jq command: {e}")
                from l_command.handlers.default import DefaultFileHandler

                DefaultFileHandler.handle(path)

        except OSError as e:
            logger.error(
                f"Error accessing file stats for JSON processing: {e}",
            )
            # Fallback if we can't even get the file size
            from l_command.handlers.default import DefaultFileHandler

            DefaultFileHandler.handle(path)

    @classmethod
    def priority(cls: type["JsonHandler"]) -> int:
        """Return the priority of the JSON handler.

        Returns:
            50 (medium priority, higher than default).
        """
        return 50  # JSON has higher priority than default
