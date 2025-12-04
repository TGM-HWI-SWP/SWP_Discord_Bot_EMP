from pathlib import Path
import re

class LogLoader:
    def __init__(self):
        self.log_dir = Path(__file__).parent.parent / "logs"
        self.business_logic_dir = Path(__file__).parent.parent / "business_logic"
    
    def setup_log_files(self) -> None:
        business_logic_files = [
            file.stem for file in self.business_logic_dir.glob("*.py")
            if file.stem != "__init__" and file.stem != "model"
        ]
        
        for filename in business_logic_files:
            log_file = self.log_dir / f'{filename}.log'
            if not log_file.exists():
                log_file.touch()

        print("Log files setup complete.")
    
    def get_log_file_path(self, class_name: str) -> Path:
        filename = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
        
        return self.log_dir / f'{filename}.log'


if __name__ == "__main__":
    log_loader = LogLoader()
    log_loader.setup_log_files()
    