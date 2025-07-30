#!/usr/bin/env python3
"""
Test the detection strategy feature of breeze-langdetect
"""

import tempfile
import os
import breeze_langdetect


def test_detection_strategies():
    print("Testing language detection strategies:\n")

    # Test 1: Extension-based detection (nonexistent file)
    result = breeze_langdetect.detect_language_with_strategy("/nonexistent/file.py")
    if result:
        print("1. Nonexistent Python file:")
        print(f"   Language: {result.language}")
        print(f"   Strategy: {result.strategy}")
        print("   (Detected from extension without reading file)\n")

    # Test 2: Shebang detection
    with tempfile.NamedTemporaryFile(suffix=".script", mode="w", delete=False) as f:
        f.write('#!/usr/bin/env python3\nprint("Hello")')
        f.flush()
        result = breeze_langdetect.detect_language_with_strategy(f.name)
        if result:
            print("2. Script with Python shebang:")
            print(f"   Language: {result.language}")
            print(f"   Strategy: {result.strategy}")
            print("   (Detected from shebang line)\n")
    os.unlink(f.name)

    # Test 3: Filename detection
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        # Create a file with a special name
        temp_dir = os.path.dirname(f.name)
        special_file = os.path.join(temp_dir, "Makefile")

    with open(special_file, "w") as f:
        f.write('all:\n\techo "Hello"')

    result = breeze_langdetect.detect_language_with_strategy(special_file)
    if result:
        print("3. Makefile (detected by filename):")
        print(f"   Language: {result.language}")
        print(f"   Strategy: {result.strategy}\n")
    os.unlink(special_file)

    # Test 4: FileInfo with detection details
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write('#!/usr/bin/env python3\nimport os\nprint("Hello")')
        f.flush()
        info = breeze_langdetect.detect_file_info(f.name)
        print("4. Python file with full info:")
        print(f"   Language: {info.language}")
        print(f"   Language Detection: {info.language_detection}")
        print(f"   File Type: {info.file_type}")
        print("   (Note: infer detects shebang as shell script)\n")
    os.unlink(f.name)


if __name__ == "__main__":
    test_detection_strategies()
