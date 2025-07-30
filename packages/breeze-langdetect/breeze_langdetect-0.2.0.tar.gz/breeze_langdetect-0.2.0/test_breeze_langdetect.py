import pytest
import tempfile
import os
import breeze_langdetect


class TestDetectLanguage:
    def test_python_file(self):
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
            f.write('print("Hello, World!")')
            f.flush()
            result = breeze_langdetect.detect_language(f.name)
            assert result == "Python"
        os.unlink(f.name)

    def test_javascript_file(self):
        with tempfile.NamedTemporaryFile(suffix='.js', mode='w', delete=False) as f:
            f.write('console.log("Hello, World!");')
            f.flush()
            result = breeze_langdetect.detect_language(f.name)
            assert result == "JavaScript"
        os.unlink(f.name)

    def test_rust_file(self):
        with tempfile.NamedTemporaryFile(suffix='.rs', mode='w', delete=False) as f:
            f.write('fn main() { println!("Hello, World!"); }')
            f.flush()
            result = breeze_langdetect.detect_language(f.name)
            assert result == "Rust"
        os.unlink(f.name)

    def test_unknown_file(self):
        with tempfile.NamedTemporaryFile(suffix='.xyz', mode='w', delete=False) as f:
            f.write('some random content')
            f.flush()
            result = breeze_langdetect.detect_language(f.name)
            assert result is None
        os.unlink(f.name)

    def test_nonexistent_file(self):
        # hyperpolyglot detects language from path/extension without reading the file
        result = breeze_langdetect.detect_language('/nonexistent/file.py')
        assert result == "Python"


class TestDetectFileType:
    def test_png_image(self):
        # Create a minimal PNG file (1x1 transparent pixel)
        png_data = bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000a49444154789c6200010000000500010d0a2db40000000049454e44ae426082')
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(png_data)
            f.flush()
            result = breeze_langdetect.detect_file_type(f.name)
            assert result is not None
            assert result.mime_type == "image/png"
            assert result.extension == "png"
            assert result.category == breeze_langdetect.FileCategory.IMAGE
        os.unlink(f.name)

    def test_json_file(self):
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w', delete=False) as f:
            f.write('{"key": "value"}')
            f.flush()
            result = breeze_langdetect.detect_file_type(f.name)
            # JSON files are not detected by infer (text format)
            assert result is None
        os.unlink(f.name)

    def test_text_file(self):
        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as f:
            f.write('Plain text content')
            f.flush()
            result = breeze_langdetect.detect_file_type(f.name)
            # Plain text files might not be detected by infer
            assert result is None or result.category == breeze_langdetect.FileCategory.TEXT
        os.unlink(f.name)

    def test_nonexistent_file(self):
        with pytest.raises(OSError):
            breeze_langdetect.detect_file_type('/nonexistent/file.png')


class TestDetectFileInfo:
    def test_python_source_file(self):
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
            f.write('#!/usr/bin/env python3\nprint("Hello, World!")')
            f.flush()
            result = breeze_langdetect.detect_file_info(f.name)
            assert result.language == "Python"
            # Python files with shebang are detected as shell scripts by infer
            if result.file_type is not None:
                assert result.file_type.mime_type == "text/x-shellscript"
                assert result.file_type.category == breeze_langdetect.FileCategory.TEXT
        os.unlink(f.name)

    def test_png_image_info(self):
        # Create a minimal PNG file
        png_data = bytes.fromhex('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000a49444154789c6200010000000500010d0a2db40000000049454e44ae426082')
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(png_data)
            f.flush()
            result = breeze_langdetect.detect_file_info(f.name)
            assert result.language is None  # PNG is not a programming language
            assert result.file_type is not None
            assert result.file_type.mime_type == "image/png"
            assert result.file_type.extension == "png"
            assert result.file_type.category == breeze_langdetect.FileCategory.IMAGE
        os.unlink(f.name)

    def test_mixed_detection(self):
        # Test a file that might have both file type and language detection
        with tempfile.NamedTemporaryFile(suffix='.html', mode='w', delete=False) as f:
            f.write('<!DOCTYPE html><html><head><title>Test</title></head><body>Hello</body></html>')
            f.flush()
            result = breeze_langdetect.detect_file_info(f.name)
            assert result.language == "HTML"
            # HTML file type detection depends on infer's capabilities
            if result.file_type is not None:
                assert "html" in result.file_type.mime_type.lower() or result.file_type.extension == "html"
        os.unlink(f.name)


class TestFileCategory:
    def test_category_repr(self):
        # Test that FileCategory enum values are accessible
        assert hasattr(breeze_langdetect.FileCategory, 'IMAGE')
        assert hasattr(breeze_langdetect.FileCategory, 'AUDIO')
        assert hasattr(breeze_langdetect.FileCategory, 'VIDEO')
        assert hasattr(breeze_langdetect.FileCategory, 'DOCUMENT')
        assert hasattr(breeze_langdetect.FileCategory, 'APPLICATION')
        assert hasattr(breeze_langdetect.FileCategory, 'ARCHIVE')
        assert hasattr(breeze_langdetect.FileCategory, 'FONT')
        assert hasattr(breeze_langdetect.FileCategory, 'BOOK')
        assert hasattr(breeze_langdetect.FileCategory, 'TEXT')
        assert hasattr(breeze_langdetect.FileCategory, 'CUSTOM')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])