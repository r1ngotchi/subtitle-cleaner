import os
import sys
import subprocess
import argparse
import glob
from cleaner import clean_subtitle_content

def download_youtube_subs(url: str, output_prefix: str = "yt_temp") -> str:
    """Downloads English subtitles from YouTube URL using yt-dlp."""
    print(f"Downloading subtitles for URL: {url}...")
    
    # We download both auto-generated and manual subtitles in vtt format (which is standard on YouTube)
    cmd = [
        "yt-dlp",
        "--write-subs",
        "--write-auto-subs",
        "--skip-download",
        "--sub-lang", "en",
        "--sub-format", "vtt",
        "-o", f"{output_prefix}_%(id)s",
        url
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error: yt-dlp failed to download subtitles: {res.stderr}", file=sys.stderr)
        return None
        
    # Search for downloaded vtt files
    search_pattern = f"{output_prefix}_*.en.vtt"
    downloaded_files = glob.glob(search_pattern)
    
    if not downloaded_files:
        print("Error: No English subtitle tracks found for this video.", file=sys.stderr)
        return None
        
    return downloaded_files[0]

def main():
    parser = argparse.ArgumentParser(description="YouTube Caption Downloader & Cleaner Pipeline")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("-o", "--output", help="Path to save the cleaned subtitle file. If omitted, saves as [VIDEO_ID]_cleaned.vtt")
    parser.add_argument("-s", "--segment", action="store_true", help="Automatically segment lines semantically.")
    parser.add_argument("-m", "--mobile", action="store_true", help="Format for mobile screens (max 30 width).")
    parser.add_argument("-v", "--vocab", help="Path to custom JSON vocabulary mapping file.")
    parser.add_argument("--nle", choices=["premiere", "resolve"], help="Optimize output for specific NLE compatibility.")
    
    args = parser.parse_args()
    
    # Load vocab map if specified
    vocab_map = None
    if args.vocab:
        if not os.path.exists(args.vocab):
            print(f"Error: Vocab file not found: {args.vocab}", file=sys.stderr)
            sys.exit(1)
        import json
        with open(args.vocab, 'r', encoding='utf-8') as f:
            try:
                vocab_map = json.load(f)
            except Exception as e:
                print(f"Error: Failed to parse vocab JSON: {e}", file=sys.stderr)
                sys.exit(1)
                
    # 1. Download
    temp_prefix = "yt_temp_sub"
    downloaded_file = download_youtube_subs(args.url, temp_prefix)
    if not downloaded_file:
        sys.exit(1)
        
    try:
        # 2. Read
        print(f"Subtitles downloaded: {downloaded_file}")
        with open(downloaded_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 3. Clean
        print("Cleaning subtitles...")
        cleaned = clean_subtitle_content(
            content, 
            segment=args.segment, 
            mobile=args.mobile, 
            vocab_map=vocab_map, 
            nle=args.nle
        )
        
        # 4. Save
        if args.output:
            out_path = args.output
        else:
            # Extract video ID from temp file name
            # Format: yt_temp_sub_[VIDEO_ID].en.vtt
            basename = os.path.basename(downloaded_file)
            video_id = basename.replace(f"{temp_prefix}_", "").replace(".en.vtt", "")
            out_path = f"{video_id}_cleaned.vtt"
            
        encoding = "utf-8-sig" if args.nle == "resolve" else "utf-8"
        with open(out_path, "w", encoding=encoding) as f:
            f.write(cleaned)
            if not cleaned.endswith('\n'):
                f.write('\n')
                
        print(f"Success! Cleaned subtitles saved to: {out_path}")
        
    finally:
        # Clean up temporary downloaded file
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)

if __name__ == "__main__":
    main()
