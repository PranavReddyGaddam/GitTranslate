#!/usr/bin/env python3
"""
Audio URL Provider Worker

This script returns audio file URLs or local file paths for frontend access.
It handles both direct file paths and generates accessible URLs.

Usage:
    python return_audio_url.py --input input.json
    echo '{"podcast_data": {...}}' | python return_audio_url.py
"""

import json
import sys
import argparse
import os
import logging
from typing import Dict, Any, Optional
from utils import (
    read_input, write_output, create_error_response, create_success_response,
    validate_required_fields, setup_logging, get_audio_output_dir
)

# Setup logging
logger = setup_logging()


class AudioURLProvider:
    """Handles audio file URL generation and access."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the audio URL provider.
        
        Args:
            base_url: Base URL for serving audio files (optional)
        """
        self.base_url = base_url or os.getenv('AUDIO_BASE_URL', 'http://localhost:8000')
        self.audio_dir = get_audio_output_dir()
    
    def validate_file_exists(self, filepath: str) -> bool:
        """
        Validate that the audio file exists.
        
        Args:
            filepath: Path to the audio file
            
        Returns:
            True if file exists, False otherwise
        """
        return os.path.isfile(filepath) and os.access(filepath, os.R_OK)
    
    def get_file_info(self, filepath: str) -> Dict[str, Any]:
        """
        Get detailed information about an audio file.
        
        Args:
            filepath: Path to the audio file
            
        Returns:
            Dictionary containing file information
        """
        try:
            stat = os.stat(filepath)
            file_size = stat.st_size
            
            return {
                'exists': True,
                'file_size_bytes': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'created_at': stat.st_ctime,
                'modified_at': stat.st_mtime,
                'readable': os.access(filepath, os.R_OK)
            }
        except OSError as e:
            logger.warning(f"Could not get file info for {filepath}: {e}")
            return {
                'exists': False,
                'error': str(e)
            }
    
    def generate_url(self, filename: str) -> str:
        """
        Generate a URL for the audio file.
        
        Args:
            filename: Audio file filename
            
        Returns:
            Full URL to the audio file
        """
        # Remove any leading slashes and ensure proper URL formatting
        clean_filename = filename.lstrip('/')
        return f"{self.base_url.rstrip('/')}/static/audio/{clean_filename}"
    
    def process_audio_request(self, podcast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process audio file request and return access information.
        
        Args:
            podcast_data: Podcast data from generate_podcast.py
            
        Returns:
            Dictionary containing audio access information
        """
        try:
            # Validate required fields
            required_fields = ['podcast_id', 'filename', 'filepath']
            validate_required_fields(podcast_data, required_fields)
            
            podcast_id = podcast_data['podcast_id']
            filename = podcast_data['filename']
            filepath = podcast_data['filepath']
            
            logger.info(f"Processing audio request for podcast {podcast_id}")
            
            # Check if file exists
            file_info = self.get_file_info(filepath)
            
            if not file_info['exists']:
                raise FileNotFoundError(f"Audio file not found: {filepath}")
            
            if not file_info['readable']:
                raise PermissionError(f"Audio file not readable: {filepath}")
            
            # Generate access URLs
            direct_url = self.generate_url(filename)
            download_url = f"{direct_url}?download=true"
            
            result = {
                'podcast_id': podcast_id,
                'repo_name': podcast_data.get('repo_name'),
                'language': podcast_data.get('language'),
                'filename': filename,
                'filepath': filepath,
                'urls': {
                    'stream': direct_url,
                    'download': download_url,
                    'api_endpoint': f"/api/audio/{podcast_id}"
                },
                'file_info': file_info,
                'metadata': {
                    'duration_minutes': podcast_data.get('duration_minutes'),
                    'segments_count': podcast_data.get('segments_count'),
                    'format': podcast_data.get('format'),
                    'quality': podcast_data.get('quality'),
                    'voices_used': podcast_data.get('voices_used'),
                    'generated_at': podcast_data.get('metadata', {}).get('generated_at')
                },
                'access': {
                    'method': 'http',
                    'content_type': 'audio/mpeg',
                    'supports_range_requests': True,
                    'cache_headers': {
                        'Cache-Control': 'public, max-age=3600',
                        'ETag': f'"{podcast_id}"'
                    }
                }
            }
            
            logger.info(f"Audio access information generated for podcast {podcast_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process audio request: {e}")
            raise
    
    def get_podcast_by_id(self, podcast_id: str) -> Optional[Dict[str, Any]]:
        """
        Get podcast information by ID from the audio directory.
        
        Args:
            podcast_id: Podcast ID to search for
            
        Returns:
            Podcast data if found, None otherwise
        """
        try:
            # Search for files containing the podcast ID
            for filename in os.listdir(self.audio_dir):
                if podcast_id in filename and filename.endswith('.mp3'):
                    filepath = os.path.join(self.audio_dir, filename)
                    file_info = self.get_file_info(filepath)
                    
                    if file_info['exists']:
                        # Extract metadata from filename
                        parts = filename.replace('.mp3', '').split('_')
                        if len(parts) >= 3:
                            repo_name = parts[0].replace('_', '/')
                            language = parts[1]
                            
                            return {
                                'podcast_id': podcast_id,
                                'repo_name': repo_name,
                                'language': language,
                                'filename': filename,
                                'filepath': filepath,
                                'file_info': file_info
                            }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get podcast by ID {podcast_id}: {e}")
            return None


def main():
    """Main function to handle input/output and orchestrate the audio URL provision process."""
    parser = argparse.ArgumentParser(description='Provide audio file URLs and access information')
    parser.add_argument('--input', '-i', help='Input JSON file path')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--base-url', help='Base URL for serving audio files')
    parser.add_argument('--podcast-id', help='Podcast ID to look up (alternative to input file)')
    
    args = parser.parse_args()
    
    try:
        # Initialize provider
        provider = AudioURLProvider(base_url=args.base_url)
        
        if args.podcast_id:
            # Look up podcast by ID
            podcast_data = provider.get_podcast_by_id(args.podcast_id)
            if not podcast_data:
                error_output = create_error_response(f"Podcast not found: {args.podcast_id}")
                write_output(error_output, args.output)
                sys.exit(1)
        else:
            # Read input from file or stdin
            input_data = read_input(args.input)
            
            # Validate input structure
            if 'data' not in input_data:
                raise ValueError("Input must contain 'data' field from generate_podcast.py")
            
            podcast_data = input_data['data']
        
        # Process audio request
        result = provider.process_audio_request(podcast_data)
        
        # Prepare output
        output_data = create_success_response(result)
        
        # Write output
        write_output(output_data, args.output)
        
        logger.info("Audio URL provision completed successfully")
        
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