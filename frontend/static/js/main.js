document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('textInput');
    const generateBtn = document.getElementById('generateBtn');
    const audioSection = document.getElementById('audioSection');
    const audioPlayer = document.getElementById('audioPlayer');
    const spinner = generateBtn.querySelector('.spinner');
    const exampleBtns = document.querySelectorAll('.example-btn');

    generateBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        
        if (!text) {
            alert('Please enter some text to generate speech.');
            return;
        }

        try {
            // Show loading state
            generateBtn.disabled = true;
            spinner.classList.remove('hidden');
            generateBtn.textContent = 'Generating...';
            spinner.style.display = 'inline-block';

            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate speech');
            }

            // Update audio player with new source
            audioPlayer.src = data.audio_url;
            audioSection.classList.remove('hidden');
            audioPlayer.play();

        } catch (error) {
            alert('Error generating speech: ' + error.message);
        } finally {
            // Reset button state
            generateBtn.disabled = false;
            spinner.classList.add('hidden');
            generateBtn.textContent = 'Generate';
        }
    });

    // Handle example button clicks
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const exampleText = btn.getAttribute('data-text');
            textInput.value = exampleText;
            textInput.focus();
        });
    });

    // Add input validation
    textInput.addEventListener('input', () => {
        const text = textInput.value.trim();
        generateBtn.disabled = text.length === 0;
    });

    // Handle Enter key in input
    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !generateBtn.disabled) {
            generateBtn.click();
        }
    });
}); 