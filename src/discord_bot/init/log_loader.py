"""Provide utilities for locating and preparing log files for models."""

from pathlib import Path
import re

class LogLoader:
    def __init__(self):
        self.log_dir = Path(__file__).parent.parent / "logs"
        self.business_logic_dir = Path(__file__).parent.parent / "business_logic"
    
    def setup_log_files(self) -> None:
        """Create empty log files for each business-logic module if missing."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        business_logic_files = [
            file.stem for file in self.business_logic_dir.glob("*.py")
            if file.stem != "__init__" and file.stem != "model"
        ]
        
        for filename in business_logic_files:
            log_file = self.log_dir / f'{filename}.log'
            if not log_file.exists():
                # Touch files so downstream logging can append without errors.
                log_file.touch()

        print("Log files setup complete.")
    
    def get_log_file_path(self, name: str, *, treat_as_filename: bool = False) -> Path:
        """Return the file system path for a given logical log name.

        Args:
            name (str): Class or filename base to resolve.
            treat_as_filename (bool): Whether to treat ``name`` as a literal filename.

        Returns:
            Path: Fully-qualified path to the log file.
        """
        if treat_as_filename:
            filename = name if name.endswith(".log") else f'{name}.log'
            return self.log_dir / filename

        # Convert CamelCase class names to snake_case filenames for log files.
        filename = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        return self.log_dir / f'{filename}.log'

if __name__ == "__main__":
    log_loader = LogLoader()
    log_loader.setup_log_files()
    