import os
import json
from typing import Dict, Any, List, Optional

class CurriculumService:
    """Service to load and parse the official ABTalks AI Cohort curriculum."""
    
    def __init__(self, filepath: Optional[str] = None):
        if filepath is None:
            # Resolve path relative to this service file:
            # backend/app/services/curriculum.py -> 4 levels up is workspace root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            filepath = os.path.join(base_dir, "docs", "abtalks", "curriculum.json")
        self.filepath = filepath
        self._data: Optional[Dict[str, Any]] = None

    @property
    def data(self) -> Dict[str, Any]:
        """Load and cache the curriculum data from JSON."""
        if self._data is None:
            if not os.path.exists(self.filepath):
                raise FileNotFoundError(f"Curriculum JSON not found at: {self.filepath}")
            with open(self.filepath, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        return self._data

    def get_day(self, day_num: int) -> Optional[Dict[str, Any]]:
        """Get syllabus data for a specific day."""
        for d in self.data.get("days", []):
            if d.get("day") == day_num:
                return d
        return None

    def get_module_for_day(self, day_num: int) -> Optional[Dict[str, Any]]:
        """Get module metadata that encompasses a specific day."""
        for module in self.data.get("modules", []):
            days_range = module.get("days", [])
            if len(days_range) == 2:
                start, end = days_range[0], days_range[1]
                if start <= day_num <= end:
                    return module
        return None
