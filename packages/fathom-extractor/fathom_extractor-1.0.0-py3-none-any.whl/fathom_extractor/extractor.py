#!/usr/bin/env python3
"""
HAR File Transcript Extractor

This script analyzes HAR (HTTP Archive) files and extracts JSON transcripts
from network requests, particularly looking for transcription-related API calls
and embedded transcript data in web application responses.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import re


class HARTranscriptExtractor:
    def __init__(self, har_file_path: str):
        self.har_file_path = Path(har_file_path)
        self.har_data = None
        
    def load_har_file(self) -> bool:
        """Load and parse the HAR file."""
        try:
            with open(self.har_file_path, 'r', encoding='utf-8') as f:
                self.har_data = json.load(f)
            print(f"Successfully loaded HAR file: {self.har_file_path}")
            return True
        except FileNotFoundError:
            print(f"Error: HAR file not found: {self.har_file_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in HAR file: {e}")
            return False
        except Exception as e:
            print(f"Error loading HAR file: {e}")
            return False
    
    def analyze_entries(self) -> List[Dict[str, Any]]:
        """Analyze HAR entries to find potential transcript data."""
        if not self.har_data:
            return []
        
        transcript_entries = []
        entries = self.har_data.get('log', {}).get('entries', [])
        
        print(f"Analyzing {len(entries)} network entries...")
        
        for i, entry in enumerate(entries):
            request = entry.get('request', {})
            response = entry.get('response', {})
            
            # Look for transcript-related URLs
            url = request.get('url', '')
            method = request.get('method', '')
            
            # Common patterns for transcript/transcription APIs
            transcript_patterns = [
                r'transcript',
                r'transcribe',
                r'captions',
                r'subtitles',
                r'speech',
                r'stt',  # speech-to-text
                r'asr',  # automatic speech recognition
                r'/v1/audio/transcriptions',
                r'whisper',
                r'deepgram',
                r'rev\.ai',
                r'speechmatics',
                r'assembly',
                r'google.*speech',
                r'azure.*speech',
                r'aws.*transcribe'
            ]
            
            # Fathom-specific patterns
            fathom_patterns = [
                r'fathom\.video.*_inertia',
                r'page-call-detail',
                r'share/.*\?_inertia'
            ]
            
            is_transcript_related = any(
                re.search(pattern, url, re.IGNORECASE) for pattern in transcript_patterns
            )
            
            is_fathom_related = any(
                re.search(pattern, url, re.IGNORECASE) for pattern in fathom_patterns
            )
            
            # Check response content for Fathom-specific data
            content = response.get('content', {})
            response_text = content.get('text', '')
            
            has_fathom_transcript_content = False
            if response_text:
                # Look for Fathom-specific transcript indicators in response
                fathom_content_patterns = [
                    r'page-call-detail',
                    r'"questions".*"clips"',
                    r'"cue_id".*"speaker".*"question".*"answer"',
                    r'"aiNotes".*"noteText"',
                    r'"transcript.*"text"'
                ]
                
                has_fathom_transcript_content = any(
                    re.search(pattern, response_text, re.IGNORECASE) for pattern in fathom_content_patterns
                )
            
            if is_transcript_related or is_fathom_related or has_fathom_transcript_content:
                transcript_entries.append({
                    'index': i,
                    'url': url,
                    'method': method,
                    'entry': entry,
                    'type': 'fathom' if (is_fathom_related or has_fathom_transcript_content) else 'generic'
                })
                print(f"Found potential transcript entry {i}: {method} {url}")
        
        return transcript_entries
    
    def extract_transcript_from_entry(self, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract transcript data from a specific HAR entry."""
        response = entry.get('response', {})
        content = response.get('content', {})
        
        # Get response text
        text = content.get('text', '')
        if not text:
            return None
        
        # Try to parse as JSON
        try:
            response_data = json.loads(text)
            
            # Check if this is a Fathom Inertia.js response
            if self._is_fathom_response(response_data):
                return self._extract_fathom_transcript(entry, response_data)
            
            # Look for common transcript fields
            transcript_fields = [
                'transcript', 'transcription', 'text', 'results', 'segments',
                'alternatives', 'words', 'utterances', 'captions', 'subtitles'
            ]
            
            transcript_data = {}
            
            # Extract any fields that might contain transcript data
            for field in transcript_fields:
                if field in response_data:
                    transcript_data[field] = response_data[field]
            
            # If we found transcript-related fields, return the data
            if transcript_data:
                return {
                    'url': entry.get('request', {}).get('url', ''),
                    'timestamp': entry.get('startedDateTime', ''),
                    'transcript_data': transcript_data,
                    'full_response': response_data,
                    'source': 'generic_api'
                }
            
            # If no specific fields found, check if the entire response looks like transcript data
            if self._looks_like_transcript(response_data):
                return {
                    'url': entry.get('request', {}).get('url', ''),
                    'timestamp': entry.get('startedDateTime', ''),
                    'transcript_data': response_data,
                    'full_response': response_data,
                    'source': 'generic_api'
                }
                
        except json.JSONDecodeError:
            # If it's not JSON, check if it's plain text transcript
            if self._looks_like_text_transcript(text):
                return {
                    'url': entry.get('request', {}).get('url', ''),
                    'timestamp': entry.get('startedDateTime', ''),
                    'transcript_data': {'text': text},
                    'full_response': text,
                    'source': 'plain_text'
                }
        
        return None
    
    def _is_fathom_response(self, data: Any) -> bool:
        """Check if this is a Fathom Inertia.js response."""
        if isinstance(data, dict):
            # Check for Fathom-specific structure
            if data.get('component') == 'page-call-detail':
                return True
            
            # Check for props with Fathom-specific fields
            props = data.get('props', {})
            if isinstance(props, dict):
                fathom_indicators = ['questions', 'aiNotes', 'askFathom', 'sharing', 'cueSpans']
                if any(indicator in props for indicator in fathom_indicators):
                    return True
        
        return False
    
    def _extract_fathom_transcript(self, entry: Dict[str, Any], response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract transcript data from a Fathom Inertia.js response."""
        props = response_data.get('props', {})
        
        # Extract basic metadata
        url = entry.get('request', {}).get('url', '')
        timestamp = entry.get('startedDateTime', '')
        
        # Initialize the transcript data structure
        transcript_data = {
            'url': url,
            'timestamp': timestamp,
            'source': 'fathom'
        }
        
        # Extract call metadata
        call_metadata = {}
        if 'call' in props:
            call = props['call']
            call_metadata = {
                'title': call.get('title', ''),
                'duration_minutes': call.get('duration_minutes'),
                'host': call.get('host', {}).get('email', ''),
                'created_at': call.get('created_at', ''),
                'updated_at': call.get('updated_at', '')
            }
        
        # Extract speakers
        speakers = []
        if 'speakers' in props:
            for speaker in props['speakers']:
                speakers.append({
                    'name': speaker.get('name', ''),
                    'email': speaker.get('email', ''),
                    'id': speaker.get('id', '')
                })
        
        # Extract Q&A clips
        qa_clips = []
        if 'questions' in props:
            for question in props['questions']:
                clips = question.get('clips', [])
                for clip in clips:
                    qa_clips.append({
                        'question': question.get('question', ''),
                        'answer': clip.get('answer', ''),
                        'speaker': clip.get('speaker', {}),
                        'start_time': clip.get('start_time', 0),
                        'end_time': clip.get('end_time', 0),
                        'cue_id': clip.get('cue_id', '')
                    })
        
        # Extract AI notes
        ai_notes = []
        if 'aiNotes' in props:
            for note in props['aiNotes']:
                ai_notes.append({
                    'note_text': note.get('noteText', ''),
                    'created_at': note.get('created_at', ''),
                    'id': note.get('id', '')
                })
        
        # Extract meeting summary
        meeting_summary = {}
        if 'aiNotes' in props and props['aiNotes']:
            # Usually the first AI note contains the meeting summary
            first_note = props['aiNotes'][0]
            meeting_summary = {
                'noteText': first_note.get('noteText', ''),
                'created_at': first_note.get('created_at', ''),
                'id': first_note.get('id', '')
            }
        
        # Extract note clips
        note_clips = []
        if 'noteClips' in props:
            for clip in props['noteClips']:
                note_clips.append({
                    'text': clip.get('text', ''),
                    'start_time': clip.get('start_time', 0),
                    'end_time': clip.get('end_time', 0),
                    'speaker': clip.get('speaker', {}),
                    'cue_id': clip.get('cue_id', '')
                })
        
        # Extract full transcript
        full_transcript = self._extract_full_transcript_from_props(props)
        
        # Assemble the final transcript data
        transcript_data['transcript_data'] = {
            'call_metadata': call_metadata,
            'speakers': speakers,
            'qa_clips': qa_clips,
            'ai_notes': ai_notes,
            'meeting_summary': meeting_summary,
            'note_clips': note_clips,
            'full_transcript': full_transcript
        }
        
        return transcript_data
    
    def _extract_full_transcript_from_props(self, props: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract the full transcript from Fathom props."""
        transcript_segments = []
        
        # Look for cueSpans which contain the full transcript
        if 'cueSpans' in props:
            cue_spans = props['cueSpans']
            
            for span in cue_spans:
                # Each span represents a segment of speech
                segment = {
                    'text': span.get('text', ''),
                    'start_time': span.get('start_time', 0),
                    'end_time': span.get('end_time', 0),
                    'speaker_id': span.get('speaker_id', ''),
                    'cue_id': span.get('cue_id', '')
                }
                
                # Try to match speaker ID to speaker name
                if 'speakers' in props:
                    for speaker in props['speakers']:
                        if speaker.get('id') == segment['speaker_id']:
                            segment['speaker_name'] = speaker.get('name', 'Unknown')
                            segment['speaker_email'] = speaker.get('email', '')
                            break
                    else:
                        segment['speaker_name'] = 'Unknown'
                        segment['speaker_email'] = ''
                
                transcript_segments.append(segment)
        
        # Alternative: look for transcript data in other locations
        elif 'transcript' in props:
            transcript_data = props['transcript']
            if isinstance(transcript_data, list):
                for item in transcript_data:
                    if isinstance(item, dict):
                        segment = {
                            'text': item.get('text', ''),
                            'start_time': item.get('start_time', 0),
                            'end_time': item.get('end_time', 0),
                            'speaker_name': item.get('speaker', 'Unknown'),
                            'speaker_id': item.get('speaker_id', ''),
                            'cue_id': item.get('cue_id', '')
                        }
                        transcript_segments.append(segment)
        
        # Sort by start time
        transcript_segments.sort(key=lambda x: x.get('start_time', 0))
        
        return transcript_segments
    
    def _looks_like_transcript(self, data: Any) -> bool:
        """Check if data structure looks like transcript data."""
        if isinstance(data, dict):
            # Check for common transcript fields
            transcript_indicators = [
                'text', 'transcript', 'transcription', 'words', 'segments',
                'alternatives', 'results', 'utterances', 'speaker', 'timestamp'
            ]
            
            # If it has multiple transcript-like fields, it's probably a transcript
            matches = sum(1 for indicator in transcript_indicators if indicator in data)
            return matches >= 2
        
        elif isinstance(data, list) and data:
            # Check if it's a list of transcript segments
            first_item = data[0]
            if isinstance(first_item, dict):
                return self._looks_like_transcript(first_item)
        
        return False
    
    def _looks_like_text_transcript(self, text: str) -> bool:
        """Check if plain text looks like a transcript."""
        # Look for patterns common in transcripts
        transcript_patterns = [
            r'\[\d+:\d+\]',  # Timestamps like [12:34]
            r'\d+:\d+\s',    # Timestamps like 12:34 
            r'Speaker \d+:',  # Speaker labels
            r'[A-Z][a-z]+:',  # Name: format
            r'>>',            # Speaker change indicators
            r'SPEAKER_\d+',   # Speaker labels
        ]
        
        matches = sum(1 for pattern in transcript_patterns if re.search(pattern, text))
        
        # Also check for reasonable length and word density
        words = len(text.split())
        lines = len(text.split('\n'))
        
        # Heuristic: transcripts usually have reasonable word/line ratios
        if words > 50 and lines > 5 and matches > 0:
            return True
        
        return matches >= 2
    
    def extract_all_transcripts(self) -> List[Dict[str, Any]]:
        """Extract all transcripts from the HAR file."""
        if not self.load_har_file():
            return []
        
        transcript_entries = self.analyze_entries()
        transcripts = []
        
        for entry_info in transcript_entries:
            transcript = self.extract_transcript_from_entry(entry_info['entry'])
            if transcript:
                transcripts.append(transcript)
        
        return transcripts
    
    def save_transcripts(self, transcripts: List[Dict[str, Any]], output_file: str):
        """Save extracted transcripts to a JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transcripts, f, indent=2, ensure_ascii=False)
        print(f"Transcripts saved to: {output_file}")
    
    def create_clean_transcript(self, transcripts: List[Dict[str, Any]], output_file: str):
        """Create a clean, readable transcript file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("EXTRACTED TRANSCRIPTS\n")
            f.write("=" * 50 + "\n\n")
            
            for i, transcript in enumerate(transcripts, 1):
                f.write(f"TRANSCRIPT {i}\n")
                f.write("-" * 20 + "\n")
                f.write(f"Source: {transcript['source']}\n")
                f.write(f"URL: {transcript['url']}\n")
                f.write(f"Timestamp: {transcript['timestamp']}\n\n")
                
                if transcript['source'] == 'fathom':
                    self._write_fathom_transcript(f, transcript['transcript_data'])
                else:
                    self._write_generic_transcript(f, transcript['transcript_data'])
                
                f.write("\n" + "=" * 50 + "\n\n")
        
        print(f"Clean transcript saved to: {output_file}")
    
    def create_markdown_transcript(self, transcripts: List[Dict[str, Any]], output_file: str):
        """Create a beautiful markdown transcript with YAML frontmatter."""
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write YAML frontmatter
            f.write("---\n")
            f.write(f'title: "Extracted Transcript"\n')
            f.write(f'extraction_date: "{self._get_current_timestamp()}"\n')
            f.write(f'total_transcripts: {len(transcripts)}\n')
            
            if transcripts:
                f.write("transcripts:\n")
                for i, transcript in enumerate(transcripts, 1):
                    f.write(f"  - id: {i}\n")
                    f.write(f'    source: "{transcript["source"]}"\n')
                    f.write(f'    url: "{transcript["url"]}"\n')
                    f.write(f'    timestamp: "{transcript["timestamp"]}"\n')
                    
                    # Add Fathom-specific metadata
                    if transcript['source'] == 'fathom':
                        data = transcript['transcript_data']
                        if 'call_metadata' in data:
                            meta = data['call_metadata']
                            if meta.get('title'):
                                f.write(f'    meeting_title: "{meta["title"]}"\n')
                            if meta.get('duration_minutes'):
                                f.write(f'    duration_minutes: {meta["duration_minutes"]}\n')
                            if meta.get('host'):
                                f.write(f'    host: "{meta["host"]}"\n')
            
            f.write("---\n\n")
            
            # Write main content
            f.write("# Extracted Transcripts\n\n")
            f.write(f"This document contains {len(transcripts)} transcript(s) extracted from a HAR file.\n\n")
            
            for i, transcript in enumerate(transcripts, 1):
                self._write_markdown_transcript(f, transcript, i)
        
        print(f"Markdown transcript saved to: {output_file}")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _write_markdown_transcript(self, file_handle, transcript: Dict[str, Any], index: int):
        """Write a single transcript in markdown format."""
        file_handle.write(f"## Transcript {index}\n\n")
        
        # Write metadata table
        file_handle.write("| Field | Value |\n")
        file_handle.write("|----------|-------|\n")
        file_handle.write(f"| **Source** | `{transcript['source']}` |\n")
        file_handle.write(f"| **URL** | `{transcript['url']}` |\n")
        file_handle.write(f"| **Timestamp** | `{transcript['timestamp']}` |\n")
        
        # Add Fathom-specific metadata
        if transcript['source'] == 'fathom':
            data = transcript['transcript_data']
            if 'call_metadata' in data:
                meta = data['call_metadata']
                if meta.get('title'):
                    file_handle.write(f"| **Meeting Title** | {meta['title']} |\n")
                if meta.get('duration_minutes'):
                    file_handle.write(f"| **Duration** | {meta['duration_minutes']} minutes |\n")
                if meta.get('host'):
                    file_handle.write(f"| **Host** | {meta['host']} |\n")
        
        file_handle.write("\n")
        
        # Write transcript content based on source
        if transcript['source'] == 'fathom':
            self._write_fathom_markdown(file_handle, transcript['transcript_data'])
        else:
            self._write_generic_markdown(file_handle, transcript['transcript_data'])
        
        file_handle.write("\n---\n\n")
    
    def _write_fathom_markdown(self, file_handle, data: Dict[str, Any]):
        """Write Fathom transcript data in markdown format."""
        # Speakers
        if 'speakers' in data and data['speakers']:
            file_handle.write("### 👥 Speakers\n\n")
            for speaker in data['speakers']:
                name = speaker.get('name', 'Unknown')
                email = speaker.get('email', 'No email')
                file_handle.write(f"- **{name}** ({email})\n")
            file_handle.write("\n")
        
        # Meeting Summary
        if 'meeting_summary' in data and data['meeting_summary']:
            summary = data['meeting_summary']
            note_text = summary.get('noteText', '')
            if note_text:
                file_handle.write("### 📋 Meeting Summary\n\n")
                # Clean up HTML tags and links
                clean_text = re.sub(r'<[^>]+>', '', note_text)
                clean_text = re.sub(r'\\u003c[^>]+\\u003e', '', clean_text)
                file_handle.write(clean_text)
                file_handle.write("\n\n")
        
        # AI Notes
        if 'ai_notes' in data and data['ai_notes']:
            file_handle.write("### 🤖 AI Notes\n\n")
            for note in data['ai_notes']:
                note_text = note.get('noteText', '')
                if note_text:
                    # Clean up HTML tags
                    clean_text = re.sub(r'<[^>]+>', '', note_text)
                    clean_text = re.sub(r'\\u003c[^>]+\\u003e', '', clean_text)
                    file_handle.write(f"- {clean_text}\n")
            file_handle.write("\n")
        
        # Q&A Clips
        if 'qa_clips' in data and data['qa_clips']:
            file_handle.write("### 💬 Questions & Answers\n\n")
            for i, clip in enumerate(data['qa_clips'], 1):
                speaker_name = clip.get('speaker', {}).get('name', 'Unknown')
                question = clip.get('question', '')
                answer = clip.get('answer', '')
                start_time = clip.get('start_time', 0)
                end_time = clip.get('end_time', 0)
                
                # Format time as MM:SS
                start_min, start_sec = divmod(int(start_time), 60)
                end_min, end_sec = divmod(int(end_time), 60)
                time_range = f"{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}"
                
                file_handle.write(f"#### Q&A {i} - {speaker_name}\n")
                file_handle.write(f"🕒 **Time:** {time_range}\n\n")
                file_handle.write(f"**❓ Question:** {question}\n\n")
                file_handle.write(f"**💡 Answer:** {answer}\n\n")
            file_handle.write("\n")
        
        # Full Transcript
        if 'full_transcript' in data and data['full_transcript']:
            file_handle.write("### 📄 Full Transcript\n\n")
            file_handle.write("*Complete conversation in chronological order*\n\n")
            
            current_speaker = None
            current_time_block = None
            
            for segment in data['full_transcript']:
                text = segment.get('text', '').strip()
                speaker_name = segment.get('speaker_name', 'Unknown')
                start_time = segment.get('start_time', 0)
                
                if not text:
                    continue
                
                # Format time as MM:SS
                start_min, start_sec = divmod(int(start_time), 60)
                time_formatted = f"{start_min:02d}:{start_sec:02d}"
                
                # Group consecutive segments from the same speaker in the same time window
                time_block = f"{start_min:02d}:{start_sec//10}x"  # Group by 10-second blocks
                
                if current_speaker != speaker_name or current_time_block != time_block:
                    if current_speaker is not None:
                        file_handle.write("\n\n")
                    
                    file_handle.write(f"**[{time_formatted}] {speaker_name}:**  \n")
                    current_speaker = speaker_name
                    current_time_block = time_block
                    file_handle.write(f"{text}")
                else:
                    # Continue the same speaker's segment
                    file_handle.write(f" {text}")
            
            file_handle.write("\n\n")
    
    def _write_generic_markdown(self, file_handle, data: Dict[str, Any]):
        """Write generic transcript data in markdown format."""
        file_handle.write("\n### 📄 Transcript Content\n\n")
        
        # Handle different data structures
        if isinstance(data, dict):
            if 'text' in data:
                file_handle.write(f"{data['text']}\n\n")
            elif 'transcript' in data:
                file_handle.write(f"{data['transcript']}\n\n")
            else:
                file_handle.write("```json\n")
                file_handle.write(json.dumps(data, indent=2, ensure_ascii=False))
                file_handle.write("\n```\n\n")
        elif isinstance(data, str):
            file_handle.write(f"{data}\n\n")
        else:
            file_handle.write("```json\n")
            file_handle.write(json.dumps(data, indent=2, ensure_ascii=False))
            file_handle.write("\n```\n\n")

    def _write_fathom_transcript(self, file_handle, data: Dict[str, Any]):
        """Write Fathom transcript data in a readable format."""
        # Write call metadata
        if 'call_metadata' in data:
            meta = data['call_metadata']
            file_handle.write(f"MEETING: {meta.get('title', 'Unknown')}\n")
            file_handle.write(f"Duration: {meta.get('duration_minutes', 'Unknown')} minutes\n")
            file_handle.write(f"Host: {meta.get('host', 'Unknown')}\n\n")
        
        # Write speakers
        if 'speakers' in data:
            file_handle.write("SPEAKERS:\n")
            for speaker in data['speakers']:
                name = speaker.get('name', 'Unknown')
                email = speaker.get('email', 'No email')
                file_handle.write(f"  - {name} ({email})\n")
            file_handle.write("\n")
        
        # Write Q&A clips
        if 'qa_clips' in data:
            file_handle.write("QUESTIONS & ANSWERS:\n\n")
            for clip in data['qa_clips']:
                speaker_name = clip.get('speaker', {}).get('name', 'Unknown')
                question = clip.get('question', '')
                answer = clip.get('answer', '')
                start_time = clip.get('start_time', 0)
                end_time = clip.get('end_time', 0)
                
                file_handle.write(f"[{start_time:.1f}s - {end_time:.1f}s] {speaker_name}\n")
                file_handle.write(f"Q: {question}\n")
                file_handle.write(f"A: {answer}\n\n")
        
        # Write meeting summary
        if 'meeting_summary' in data:
            summary = data['meeting_summary']
            note_text = summary.get('noteText', '')
            if note_text:
                file_handle.write("MEETING SUMMARY:\n")
                # Clean up HTML tags and links
                clean_text = re.sub(r'<[^>]+>', '', note_text)
                clean_text = re.sub(r'\\u003c[^>]+\\u003e', '', clean_text)
                file_handle.write(clean_text)
                file_handle.write("\n\n")
        
        # Write full transcript
        if 'full_transcript' in data and data['full_transcript']:
            file_handle.write("FULL TRANSCRIPT:\n\n")
            
            current_speaker = None
            
            for segment in data['full_transcript']:
                text = segment.get('text', '').strip()
                speaker_name = segment.get('speaker_name', 'Unknown')
                start_time = segment.get('start_time', 0)
                
                if not text:
                    continue
                
                # Format time as MM:SS
                start_min, start_sec = divmod(int(start_time), 60)
                time_formatted = f"{start_min:02d}:{start_sec:02d}"
                
                if current_speaker != speaker_name:
                    if current_speaker is not None:
                        file_handle.write("\n")
                    file_handle.write(f"\n[{time_formatted}] {speaker_name}: ")
                    current_speaker = speaker_name
                
                file_handle.write(text + " ")
            
            file_handle.write("\n\n")

    def _write_generic_transcript(self, file_handle, data: Dict[str, Any]):
        """Write generic transcript data in a readable format."""
        if isinstance(data, dict):
            if 'text' in data:
                file_handle.write(f"{data['text']}\n\n")
            elif 'transcript' in data:
                file_handle.write(f"{data['transcript']}\n\n")
            else:
                file_handle.write(json.dumps(data, indent=2, ensure_ascii=False))
                file_handle.write("\n\n")
        elif isinstance(data, str):
            file_handle.write(f"{data}\n\n")
        else:
            file_handle.write(json.dumps(data, indent=2, ensure_ascii=False))
            file_handle.write("\n\n") 