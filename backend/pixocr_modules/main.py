# Refactored main.py with modular upgrades (Entry Point)

import os
import argparse
import json
from pathlib import Path
from core.extractor import SmartTableExtractor
from core.config import load_config

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Smart OCR Pipeline for Construction Documents")
    parser.add_argument('--image', required=True, help="Path to input image")
    parser.add_argument('--model', required=True, help="Path to YOLOv8 model")
    parser.add_argument('--output', required=True, help="Directory to save outputs")
    parser.add_argument('--translate_headers', action='store_true', help="Translate German headers to canonical English names")
    parser.add_argument('--validate_schema', action='store_true', help="Enable strict schema validation")
    parser.add_argument('--debug', action='store_true', help="Enable debug outputs and confidence maps")
    parser.add_argument('--config', help="Optional path to config.yaml")
    
    args = parser.parse_args()
    
    cfg = load_config(args.config)
    
    extractor = SmartTableExtractor(
        yolo_model_path=args.model,
        output_dir=args.output,
        config=cfg,
        translate_headers=args.translate_headers,
        validate_schema=args.validate_schema,
        debug=args.debug
    )

    result = extractor.process(args.image)
    print(json.dumps(result, indent=2))
