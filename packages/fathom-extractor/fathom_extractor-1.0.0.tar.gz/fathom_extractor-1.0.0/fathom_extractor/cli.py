#!/usr/bin/env python3
"""
Command-line interface for the Fathom Extractor tool.
"""

import argparse
import sys
from pathlib import Path

from .extractor import HARTranscriptExtractor


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Extract transcripts from HAR files, particularly from Fathom video calls',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fathom-extractor recording.har
  fathom-extractor recording.har -o transcripts.json
  fathom-extractor recording.har -m transcript.md
  fathom-extractor recording.har -c clean.txt -m beautiful.md -v

For more information on how to download HAR files, see the README.
        """
    )
    
    parser.add_argument(
        'har_file', 
        help='Path to the HAR file to extract transcripts from'
    )
    parser.add_argument(
        '-o', '--output', 
        default='extracted_transcripts.json',
        help='Output JSON file (default: extracted_transcripts.json)'
    )
    parser.add_argument(
        '-c', '--clean',
        help='Also create a clean, readable transcript file'
    )
    parser.add_argument(
        '-m', '--markdown',
        help='Create a beautiful markdown transcript with YAML frontmatter'
    )
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Check if HAR file exists
    har_path = Path(args.har_file)
    if not har_path.exists():
        print(f"Error: HAR file not found: {args.har_file}", file=sys.stderr)
        sys.exit(1)
    
    # Create extractor and extract transcripts
    extractor = HARTranscriptExtractor(args.har_file)
    transcripts = extractor.extract_all_transcripts()
    
    if transcripts:
        # Save main JSON output
        extractor.save_transcripts(transcripts, args.output)
        
        # Save optional outputs
        if args.clean:
            extractor.create_clean_transcript(transcripts, args.clean)
        
        if args.markdown:
            extractor.create_markdown_transcript(transcripts, args.markdown)
        
        # Print summary
        print(f"\n✅ Successfully extracted {len(transcripts)} transcript(s)")
        print(f"📄 Saved to: {args.output}")
        
        if args.clean:
            print(f"📝 Clean transcript saved to: {args.clean}")
        if args.markdown:
            print(f"📋 Markdown transcript saved to: {args.markdown}")
        
        if args.verbose:
            print("\n📋 Transcript URLs:")
            for i, transcript in enumerate(transcripts, 1):
                print(f"  {i}. {transcript['url']} (source: {transcript['source']})")
        
        # Show what was extracted
        for transcript in transcripts:
            if transcript['source'] == 'fathom':
                data = transcript['transcript_data']
                print(f"\n🎥 Fathom transcript contains:")
                if 'qa_clips' in data:
                    print(f"  • {len(data['qa_clips'])} Q&A clips")
                if 'ai_notes' in data:
                    print(f"  • {len(data['ai_notes'])} AI notes")
                if 'meeting_summary' in data:
                    print(f"  • Meeting summary")
                if 'note_clips' in data:
                    print(f"  • {len(data['note_clips'])} note clips")
                if 'speakers' in data:
                    print(f"  • {len(data['speakers'])} speakers")
                if 'full_transcript' in data:
                    print(f"  • Full transcript with {len(data['full_transcript'])} segments")
    else:
        print("❌ No transcripts found in the HAR file.")
        print("\n🔍 The tool looks for:")
        print("  • Traditional transcript APIs (Whisper, Deepgram, etc.)")
        print("  • Fathom video transcript data in Inertia.js responses")
        print("  • URLs containing keywords like 'transcript', 'transcribe', etc.")
        print("  • Responses with transcript-like data structures")
        print("\n💡 Make sure you captured network traffic while viewing the transcript.")
        sys.exit(1)


if __name__ == '__main__':
    main() 