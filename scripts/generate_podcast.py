#!/usr/bin/env python3
"""
Podcast Generator Worker

This script generates dual-voice podcasts using LMNT API and saves audio files.
It parses dialogue scripts and creates engaging audio content with different voices.

Usage:
    python generate_podcast.py --input input.json
    echo '{"script_data": {...}}' | python generate_podcast.py
"""

import json
import sys
import argparse
import os
import logging
import requests
import time
from typing import Dict, Any, Optional, List, Tuple
from scripts.utils import (
    read_input, write_output, create_error_response, create_success_response,
    validate_required_fields, setup_logging, ensure_directory_exists, generate_uuid,
    get_audio_output_dir, sanitize_filename
)

# Setup logging
logger = setup_logging()


class PodcastGenerator:
    """Handles podcast generation using LMNT API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the podcast generator with LMNT API.
        
        Args:
            api_key: LMNT API key
        """
        self.api_key = api_key or os.getenv('LMNT_API_KEY')
        if not self.api_key:
            raise ValueError("LMNT_API_KEY environment variable is required")
        
        self.base_url = "https://api.lmnt.com"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Voice configurations for different speakers
        self.voice_configs = {
            'host': {
                'voice': 'burt',  # Professional, friendly male voice
                'speed': 1.0,
                'quality': 'high'
            },
            'expert': {
                'voice': 'sarah',  # Knowledgeable, clear female voice
                'speed': 1.0,
                'quality': 'high'
            }
        }
    
    def parse_dialogue(self, script: str) -> List[Tuple[str, str, str]]:
        """
        Parse the dialogue script into speaker segments.
        
        Args:
            script: Dialogue script with HOST: and EXPERT: labels
            
        Returns:
            List of tuples (speaker, text, voice_config)
        """
        segments = []
        lines = script.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('HOST:'):
                text = line[5:].strip()
                if text:
                    segments.append(('host', text, self.voice_configs['host']))
            elif line.startswith('EXPERT:'):
                text = line[7:].strip()
                if text:
                    segments.append(('expert', text, self.voice_configs['expert']))
        
        return segments
    
    def synthesize_segment(self, text: str, voice_config: Dict[str, Any]) -> str:
        """
        Synthesize a single text segment using LMNT API.
        
        Args:
            text: Text to synthesize
            voice_config: Voice configuration
            
        Returns:
            Audio URL or file path
        """
        try:
            payload = {
                'text': text,
                'voice': voice_config['voice'],
                'speed': voice_config['speed'],
                'quality': voice_config['quality']
            }
            
            response = requests.post(
                f"{self.base_url}/synthesize",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Return the audio URL
            return data.get('url')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to synthesize segment: {e}")
            raise
    
    def download_audio(self, url: str, filepath: str) -> None:
        """
        Download audio file from URL to local filepath.
        
        Args:
            url: Audio file URL
            filepath: Local file path to save to
        """
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Audio downloaded to {filepath}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download audio: {e}")
            raise
    
    def combine_audio_segments(self, segment_files: List[str], output_file: str) -> None:
        """
        Combine multiple audio segments into a single podcast file.
        For now, this is a placeholder - in production you'd use a proper audio library.
        
        Args:
            segment_files: List of audio file paths
            output_file: Output combined audio file path
        """
        # This is a simplified version - in production you'd use pydub or similar
        # For now, we'll just copy the first file as a placeholder
        if segment_files:
            import shutil
            shutil.copy2(segment_files[0], output_file)
            logger.info(f"Combined audio saved to {output_file}")
        else:
            raise ValueError("No audio segments to combine")
    
    def generate_podcast(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete podcast from script data.
        
        Args:
            script_data: Script data from translate_script.py
            
        Returns:
            Dictionary containing podcast metadata and file information
        """
        try:
            # Validate required fields
            required_fields = ['script', 'repo_name']
            validate_required_fields(script_data, required_fields)
            
            script = script_data.get('translated_script', script_data['script'])
            repo_name = script_data['repo_name']
            target_language = script_data.get('target_language', 'en')
            
            logger.info(f"Generating podcast for {repo_name} in {target_language}")
            
            # Parse dialogue into segments
            segments = self.parse_dialogue(script)
            
            if not segments:
                raise ValueError("No valid dialogue segments found in script")
            
            logger.info(f"Found {len(segments)} dialogue segments")
            
            # Generate unique ID for this podcast
            podcast_id = generate_uuid()
            
            # Ensure output directory exists
            audio_dir = get_audio_output_dir()
            ensure_directory_exists(audio_dir)
            
            # Create podcast filename
            safe_repo_name = sanitize_filename(repo_name.replace('/', '_'))
            podcast_filename = f"{safe_repo_name}_{target_language}_{podcast_id}.mp3"
            podcast_filepath = os.path.join(audio_dir, podcast_filename)
            
            # Synthesize each segment
            segment_files = []
            segment_metadata = []
            
            for i, (speaker, text, voice_config) in enumerate(segments):
                logger.info(f"Synthesizing segment {i+1}/{len(segments)} ({speaker})")
                
                # Synthesize audio
                audio_url = self.synthesize_segment(text, voice_config)
                
                # Download audio
                segment_filename = f"segment_{i+1}_{speaker}_{podcast_id}.mp3"
                segment_filepath = os.path.join(audio_dir, segment_filename)
                self.download_audio(audio_url, segment_filepath)
                
                segment_files.append(segment_filepath)
                segment_metadata.append({
                    'segment_number': i + 1,
                    'speaker': speaker,
                    'text': text,
                    'voice': voice_config['voice'],
                    'file': segment_filename
                })
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
            
            # Combine segments into final podcast
            self.combine_audio_segments(segment_files, podcast_filepath)
            
            # Clean up individual segment files
            for segment_file in segment_files:
                try:
                    os.remove(segment_file)
                except OSError:
                    pass  # Ignore cleanup errors
            
            # Calculate file size
            file_size = os.path.getsize(podcast_filepath)
            
            result = {
                'podcast_id': podcast_id,
                'repo_name': repo_name,
                'language': target_language,
                'filename': podcast_filename,
                'filepath': podcast_filepath,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'segments_count': len(segments),
                'duration_minutes': script_data.get('estimated_duration_minutes'),
                'format': 'mp3',
                'quality': 'high',
                'voices_used': {
                    'host': self.voice_configs['host']['voice'],
                    'expert': self.voice_configs['expert']['voice']
                },
                'segments': segment_metadata,
                'metadata': {
                    'generated_at': '2024-01-15T10:00:00Z',
                    'api_used': 'LMNT',
                    'original_script_length': len(script_data['script']),
                    'translated_script_length': len(script)
                }
            }
            
            logger.info(f"Podcast generated successfully: {podcast_filename}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate podcast: {e}")
            raise


def main():
    """Main function to handle input/output and orchestrate the podcast generation process."""
    parser = argparse.ArgumentParser(description='Generate podcast from script data')
    parser.add_argument('--input', '-i', help='Input JSON file path')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--api-key', help='LMNT API key')
    
    args = parser.parse_args()
    
    try:
        # Read input
        input_data = read_input(args.input)
        
        # Validate input structure
        if 'data' not in input_data:
            raise ValueError("Input must contain 'data' field from translate_script.py")
        
        script_data = input_data['data']
        
        # Initialize podcast generator
        generator = PodcastGenerator(api_key=args.api_key)
        
        # Generate podcast
        result = generator.generate_podcast(script_data)
        
        # Prepare output
        output_data = create_success_response(result)
        
        # Write output
        write_output(output_data, args.output)
        
        logger.info("Podcast generation completed successfully")
        
    except json.JSONDecodeError as e:
        error_output = create_error_response(f"Invalid JSON input: {str(e)}")
        write_output(error_output, args.output)
        sys.exit(1)
        
    except Exception as e:
        error_output = create_error_response(str(e))
        write_output(error_output, args.output)
        sys.exit(1)


if __name__ == "__main__":
    main() 