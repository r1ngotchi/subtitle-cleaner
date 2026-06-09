import unittest
from cleaner import clean_text, clean_subtitle_content

class TestSubtitleCleaner(unittest.TestCase):
    def test_clean_text_duplicates(self):
        self.assertEqual(clean_text("We're we're going."), "We're going.")
        self.assertEqual(clean_text("the the store"), "The store")
        self.assertEqual(clean_text("No duplicates here."), "No duplicates here.")
        
    def test_clean_text_fillers(self):
        self.assertEqual(clean_text("Yeah, like, we should go."), "Yeah we should go.")
        self.assertEqual(clean_text("um, absolutely uh yes"), "Absolutely yes")
        self.assertEqual(clean_text("like, like, we're we're going"), "We're going")
        
    def test_clean_srt(self):
        srt_input = """1
00:00:01,000 --> 00:00:04,000
Yeah, we're we're going to like, um, build this.

2
00:00:04,100 --> 00:00:06,000
Like, uh, absolutely."""
        
        expected_output = """1
00:00:01,000 --> 00:00:04,000
Yeah, we're going to build this.

2
00:00:04,100 --> 00:00:06,000
Absolutely."""
        self.assertEqual(clean_subtitle_content(srt_input), expected_output)

    def test_clean_vtt(self):
        vtt_input = """WEBVTT
Kind: captions
Language: en

1
00:00:01.000 --> 00:00:04.000
Yeah, we're we're going to like, um, build this.

2
00:00:04.100 --> 00:00:06.000
Like, uh, absolutely."""
        
        expected_output = """WEBVTT
Kind: captions
Language: en

1
00:00:01.000 --> 00:00:04.000
Yeah, we're going to build this.

2
00:00:04.100 --> 00:00:06.000
Absolutely."""
        self.assertEqual(clean_subtitle_content(vtt_input), expected_output)

    def test_clean_corrupt_srt(self):
        corrupt_input = """1
00:00:01,000 -> 00:00:03,000
Welcome welcome back back to to the channel.

1
00:00:03,100 --> 00:00:06,000
\tThis subtitle block has bad spacing.

3
00:00:05,500 --> 00:00:08,000
This subtitle overlaps with the previous one.

5
00:00:09,000 –> 00:00:11,000
This subtitle uses a malformed unicode arrow."""

        expected_output = """1
00:00:01,000 --> 00:00:03,000
Welcome back to the channel.

2
00:00:03,100 --> 00:00:06,000
This subtitle block has bad spacing.

3
00:00:05,500 --> 00:00:08,000
This subtitle overlaps with the previous one.

4
00:00:09,000 --> 00:00:11,000
This subtitle uses a malformed unicode arrow."""
        self.assertEqual(clean_subtitle_content(corrupt_input), expected_output)

    def test_reading_speed_detector(self):
        from diagnostics import run_diagnostics
        # 20 characters in 0.2s = 100 CPS (extremely high)
        srt_input = """1
00:00:01,000 --> 00:00:01,200
Supercalifragilistic"""
        findings = run_diagnostics(srt_input)
        speed_findings = [f for f in findings if f['type'] == 'reading_speed']
        self.assertTrue(len(speed_findings) > 0)
        self.assertEqual(speed_findings[0]['severity'], 'HIGH')
        self.assertIn("High reading speed", speed_findings[0]['message'])

    def test_semantic_segmentation(self):
        from cleaner import split_line_semantically
        # Length: 46 characters. Splits at the conjunction "and"
        long_line = "We wanted to go to the store and buy some milk"
        expected = "We wanted to go to the store\nand buy some milk"
        self.assertEqual(split_line_semantically(long_line, 40), expected)

    def test_mobile_readability_segmentation(self):
        # Length of text line is 35 characters (exceeds mobile limit 30, but fits desktop limit 40)
        srt_input = """1
00:00:01,000 --> 00:00:05,000
This is a long sentence for mobile"""
        
        # Segment off (or desktop limit): no change
        self.assertEqual(clean_subtitle_content(srt_input, segment=True, mobile=False), srt_input)
        
        # Segment on with mobile: split semantically
        expected_mobile = """1
00:00:01,000 --> 00:00:05,000
This is a long sentence
for mobile"""
        self.assertEqual(clean_subtitle_content(srt_input, segment=True, mobile=True), expected_mobile)

    def test_mobile_pacing_warning(self):
        from diagnostics import run_diagnostics
        # 2 lines of text, duration is 1.0 second (less than 1.5s limit)
        srt_input = """1
00:00:01,000 --> 00:00:02,000
First short line
Second short line"""
        findings = run_diagnostics(srt_input)
        speed_findings = [f for f in findings if f['type'] == 'reading_speed' and 'Pacing issue' in f['message']]
        self.assertTrue(len(speed_findings) > 0)
        self.assertEqual(speed_findings[0]['severity'], 'MEDIUM')

    def test_vocabulary_mapping(self):
        # Test word-boundary-aware search and replace
        vocab_map = {
            "open eye": "OpenAI",
            "antigravity": "Antigravity"
        }
        
        # Test basic text clean
        self.assertEqual(clean_text("We are using open eye tech.", vocab_map), "We are using OpenAI tech.")
        self.assertEqual(clean_text("Testing antigravity tool.", vocab_map), "Testing Antigravity tool.")
        # Test it doesn't match parts of words (word boundary check)
        self.assertEqual(clean_text("This is an open eyelet.", vocab_map), "This is an open eyelet.")
        
        # Test subtitle content clean
        srt_input = """1
00:00:01,000 --> 00:00:04,000
We are using open eye and antigravity."""
        expected = """1
00:00:01,000 --> 00:00:04,000
We are using OpenAI and Antigravity."""
        self.assertEqual(clean_subtitle_content(srt_input, vocab_map=vocab_map), expected)

    def test_batch_directory_processing(self):
        import tempfile
        import shutil
        import subprocess
        import os
        import sys
        
        # Create temp input and output directories
        temp_in = tempfile.mkdtemp()
        temp_out = tempfile.mkdtemp()
        try:
            # Write mock files to input directory, including nested
            srt1 = os.path.join(temp_in, "sub1.srt")
            with open(srt1, "w", encoding="utf-8") as f:
                f.write("1\n00:00:01,000 -> 00:00:03,000\nWelcome welcome.")
            
            srt2 = os.path.join(temp_in, "nested", "sub2.srt")
            os.makedirs(os.path.dirname(srt2), exist_ok=True)
            with open(srt2, "w", encoding="utf-8") as f:
                f.write("1\n00:00:04,000 -> 00:00:06,000\nHello hello.")
                
            # Execute CLI batch run in a subprocess
            subprocess.run(
                [sys.executable, "cleaner.py", "-i", temp_in, "-o", temp_out],
                capture_output=True,
                text=True
            )
            
            # Check output files exist and maintain structure
            out_sub1 = os.path.join(temp_out, "sub1.srt")
            out_sub2 = os.path.join(temp_out, "nested", "sub2.srt")
            
            self.assertTrue(os.path.exists(out_sub1))
            self.assertTrue(os.path.exists(out_sub2))
            
            with open(out_sub1, "r", encoding="utf-8") as f:
                content1 = f.read()
                self.assertIn("00:00:01,000 --> 00:00:03,000", content1)
                self.assertIn("Welcome.", content1)
        finally:
            shutil.rmtree(temp_in)
            shutil.rmtree(temp_out)

    def test_nle_compatibility_detectors(self):
        from diagnostics import run_diagnostics
        
        # Test 1: Block with 3+ lines (High risk)
        srt_input_3lines = """1
00:00:01,000 --> 00:00:04,000
Line one of text
Line two of text
Line three of text"""
        findings = run_diagnostics(srt_input_3lines)
        nle_findings = [f for f in findings if f['type'] == 'nle_compatibility']
        self.assertTrue(len(nle_findings) > 0)
        self.assertEqual(nle_findings[0]['severity'], 'HIGH')
        self.assertIn("maximum of 2 lines", nle_findings[0]['message'])

        # Test 2: Line > 37 chars (Medium risk)
        srt_input_longline = """1
00:00:01,000 --> 00:00:04,000
This is a very long line that exceeds thirty seven characters in length."""
        findings2 = run_diagnostics(srt_input_longline)
        nle_findings2 = [f for f in findings2 if f['type'] == 'nle_compatibility']
        self.assertTrue(len(nle_findings2) > 0)
        self.assertEqual(nle_findings2[0]['severity'], 'MEDIUM')
        self.assertIn("exceeds 37 characters", nle_findings2[0]['message'])

    def test_nle_optimization_options(self):
        # Test Premiere Pro 37 characters width limit reformatting
        # 39 characters. Splits at the preposition "to"
        srt_input = """1
00:00:01,000 --> 00:00:04,000
We wanted to go to the grocery store today"""
        
        expected_premiere = """1
00:00:01,000 --> 00:00:04,000
We wanted to go
to the grocery store today"""
        self.assertEqual(clean_subtitle_content(srt_input, nle='premiere'), expected_premiere)

    def test_youtube_pipeline(self):
        import unittest.mock as mock
        import youtube_sync
        import tempfile
        import os
        
        mock_vtt = """WEBVTT

1
00:00:01.000 --> 00:00:04.000
Welcome welcome back back to to the channel.
"""
        def mock_download(url, prefix):
            path = f"{prefix}_xyz.en.vtt"
            with open(path, "w", encoding="utf-8") as f:
                f.write(mock_vtt)
            return path
            
        with mock.patch("youtube_sync.download_youtube_subs", side_effect=mock_download):
            temp_out = tempfile.mktemp(suffix=".vtt")
            try:
                with mock.patch("sys.argv", ["youtube_sync.py", "https://youtube.com/watch?v=xyz", "-o", temp_out]):
                    youtube_sync.main()
                
                self.assertTrue(os.path.exists(temp_out))
                with open(temp_out, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.assertIn("Welcome back to the channel.", content)
            finally:
                if os.path.exists(temp_out):
                    os.remove(temp_out)

if __name__ == "__main__":
    unittest.main()
