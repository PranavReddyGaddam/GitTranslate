#!/usr/bin/env python3
"""
Script Translator Worker

This script translates podcast scripts to different languages using Claude AI.
It maintains the dialogue format and conversational tone while adapting to the target language.

Usage:
    python translate_script.py --input input.json
    echo '{"script_data": {...}, "target_language": "es"}' | python translate_script.py
"""

import json
import sys
import argparse
import os
import logging
from typing import Dict, Any, Optional
from anthropic import Anthropic
from scripts.utils import (
    read_input, write_output, create_error_response, create_success_response,
    validate_required_fields, setup_logging
)

# Setup logging
logger = setup_logging()


class ScriptTranslator:
    """Handles script translation using Claude AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the translator with Claude API.
        
        Args:
            api_key: Anthropic Claude API key
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3.5-sonnet-20240620')
        
        # Supported languages mapping
        self.language_map = {
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese (Simplified)',
            'ru': 'Russian',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'no': 'Norwegian',
            'da': 'Danish',
            'fi': 'Finnish',
            'pl': 'Polish',
            'tr': 'Turkish',
            'he': 'Hebrew',
            'th': 'Thai'
        }
    
    def validate_language(self, language_code: str) -> str:
        """
        Validate and return the full language name.
        
        Args:
            language_code: Language code (e.g., 'es', 'fr')
            
        Returns:
            Full language name
            
        Raises:
            ValueError: If language is not supported
        """
        if language_code not in self.language_map:
            supported = ', '.join(self.language_map.keys())
            raise ValueError(f"Unsupported language code '{language_code}'. Supported: {supported}")
        
        return self.language_map[language_code]
    
    def create_translation_prompt(self, script: str, target_language: str) -> str:
        """
        Create a prompt for translating the podcast script.
        
        Args:
            script: Original podcast script
            target_language: Target language name
            
        Returns:
            Formatted translation prompt
        """
        prompt = f"""
You are a professional translator specializing in podcast and media content. 
Translate the following podcast script from English to {target_language}.

The script is a dialogue between a HOST and an EXPERT discussing a technology topic.
Maintain the exact same format and structure, only translating the content.

Important requirements:
1. Keep the exact dialogue format: "HOST:" and "EXPERT:" labels
2. Maintain the conversational, podcast-friendly tone
3. Preserve technical terms appropriately (some may remain in English if commonly used)
4. Ensure cultural appropriateness for {target_language} speakers
5. Keep the same pacing and flow
6. Maintain the same word count approximately

Original script:
{script}

Translate this script to {target_language}, maintaining the exact format:
"""
        return prompt
    
    def translate_script(self, script: str, target_language: str) -> str:
        """
        Translate the script using Claude AI.
        
        Args:
            script: Original podcast script
            target_language: Target language name
            
        Returns:
            Translated script
        """
        try:
            prompt = self.create_translation_prompt(script, target_language)
            
            logger.info(f"Translating script to {target_language}")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more consistent translation
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            translated_script = response.content[0].text.strip()
            
            if not translated_script:
                raise ValueError(f"Claude returned an empty translation for {target_language}")
            
            logger.info(f"Script translated successfully to {target_language}")
            return translated_script
            
        except Exception as e:
            logger.error(f"Failed to translate script to {target_language}: {e}")
            raise
    
    def process_translation(self, script_data: Dict[str, Any], target_language: str) -> Dict[str, Any]:
        """
        Process script translation request.
        
        Args:
            script_data: Script data from summarize_repo.py
            target_language: Target language code
            
        Returns:
            Dictionary containing the translated script and metadata
        """
        try:
            # Validate required fields
            required_fields = ['script', 'repo_name', 'word_count']
            validate_required_fields(script_data, required_fields)
            
            # Validate and get full language name
            full_language_name = self.validate_language(target_language)
            
            # Get original script
            original_script = script_data['script']
            
            # Skip translation if target language is English
            if target_language == 'en':
                logger.info("Target language is English, returning original script")
                return {
                    'script': original_script,
                    'translated_script': original_script,
                    'original_language': 'en',
                    'target_language': 'en',
                    'translation_applied': False,
                    'repo_name': script_data['repo_name'],
                    'word_count': script_data['word_count'],
                    'estimated_duration_minutes': script_data.get('estimated_duration_minutes'),
                    'format': script_data.get('format', 'dialogue'),
                    'participants': script_data.get('participants', ['host', 'expert'])
                }
            
            # Translate the script
            translated_script = self.translate_script(original_script, full_language_name)
            
            # Calculate new word count
            translated_word_count = len(translated_script.split())
            estimated_duration = translated_word_count / 150  # Rough estimate: 150 words per minute
            
            result = {
                'script': original_script,
                'translated_script': translated_script,
                'original_language': 'en',
                'target_language': target_language,
                'target_language_name': full_language_name,
                'translation_applied': True,
                'repo_name': script_data['repo_name'],
                'word_count': translated_word_count,
                'original_word_count': script_data['word_count'],
                'estimated_duration_minutes': round(estimated_duration, 1),
                'format': script_data.get('format', 'dialogue'),
                'participants': script_data.get('participants', ['host', 'expert']),
                'metadata': {
                    'translation_model': self.model,
                    'translated_at': '2024-01-15T10:00:00Z'
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process translation: {e}")
            raise


def main():
    """Main function to handle input/output and orchestrate the translation process."""
    parser = argparse.ArgumentParser(description='Translate podcast script to target language')
    parser.add_argument('--input', '-i', help='Input JSON file path')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--api-key', help='Anthropic Claude API key')
    parser.add_argument('--language', '-l', default='en', help='Target language code (default: en)')
    
    args = parser.parse_args()
    
    try:
        # Read input
        input_data = read_input(args.input)
        
        # Validate input structure
        if 'data' not in input_data:
            raise ValueError("Input must contain 'data' field from summarize_repo.py")
        
        script_data = input_data['data']
        target_language = args.language.lower()
        
        # Initialize translator
        translator = ScriptTranslator(api_key=args.api_key)
        
        # Process translation
        result = translator.process_translation(script_data, target_language)
        
        # Prepare output
        output_data = create_success_response(result)
        
        # Write output
        write_output(output_data, args.output)
        
        logger.info(f"Script translation completed successfully to {target_language}")
        
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