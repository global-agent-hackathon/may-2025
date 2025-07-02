import csv
import io
import json
from typing import List, Dict, Any, Optional

from .logger import get_logger

logger = get_logger()


class DataProcessor:
    @staticmethod
    def rows_to_csv(rows: List[Dict[str, Any]]) -> str:
        if not rows:
            return ""
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        headers = list(rows[0].keys())
        writer.writerow(headers)
        
        for row in rows:
            processed_row = []
            for key in headers:
                value = row.get(key, "")
                if isinstance(value, (dict, list)):
                    processed_row.append(json.dumps(value))
                else:
                    processed_row.append(value)
            writer.writerow(processed_row)
        
        return output.getvalue()

    @staticmethod
    def rows_to_form_data_csv(rows: List[Dict[str, Any]]) -> str:
        if not rows:
            return ""
        
        all_data_keys = set()
        for row in rows:
            data = row.get('data', {})
            if isinstance(data, dict):
                all_data_keys.update(data.keys())
        
        if not all_data_keys:
            return ""
        
        data_headers = sorted(all_data_keys)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(data_headers)
        
        for row in rows:
            data = row.get('data', {})
            processed_row = []
            for key in data_headers:
                value = data.get(key, "")
                if isinstance(value, (dict, list)):
                    processed_row.append(json.dumps(value))
                else:
                    processed_row.append(value)
            writer.writerow(processed_row)
        
        return output.getvalue()

    @staticmethod
    def clean_field_for_frontend(field: Dict[str, Any]) -> Dict[str, Any]:
        return {k: v for k, v in field.items() if v is not None}

    @staticmethod
    def validate_field_structure(field: Dict[str, Any]) -> Dict[str, Any]:
        if "required" not in field:
            field["required"] = False
            
        if field["type"] in ["multiple_choice", "dropdown", "multi_select"]:
            if "options" not in field or field["options"] is None:
                field["options"] = []
        
        if "is_ai_field" not in field:
            field["is_ai_field"] = False
            
        if field.get("is_ai_field") and not field.get("ai_metadata_prompt"):
            field["ai_metadata_prompt"] = ""
        
        return field 