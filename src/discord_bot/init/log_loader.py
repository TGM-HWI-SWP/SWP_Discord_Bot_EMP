from pathlib import Path
import re

class LogLoader:
    def __init__(self):
        self.log_dir = Path(__file__).parent.parent / "logs"
        self.business_logic_dir = Path(__file__).parent.parent / "business_logic"
    
    def setup_log_files(self) -> None:
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        business_logic_files = [
            file.stem for file in self.business_logic_dir.glob("*.py")
            if file.stem != "__init__" and file.stem != "model"
        ]
        
        for filename in business_logic_files:
            log_file = self.log_dir / f'{filename}.log'
            if not log_file.exists():
                log_file.touch()

        print("Log files setup complete.")
    
    def get_log_file_path(self, name: str, *, treat_as_filename: bool = False) -> Path:
        if treat_as_filename:
            filename = name if name.endswith(".log") else f'{name}.log'
            return self.log_dir / filename

        filename = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        return self.log_dir / f'{filename}.log'

if __name__ == "__main__":
    log_loader = LogLoader()
    log_loader.setup_log_files()
    