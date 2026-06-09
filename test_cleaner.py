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

if __name__ == "__main__":
    unittest.main()
