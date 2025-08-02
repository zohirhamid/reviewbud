let currentStep = 1;
const totalSteps = 3;
let selectedTags = [];
let generatedReview = '';
let googleUrl = '';
let isEditMode = false;

// Initialize
updateProgress();
initializeSliders();

// Slider handling with perfect alignment
function initializeSliders() {
    const sliders = document.querySelectorAll('.slider');
    
    sliders.forEach((slider) => {
        const sliderGroup = slider.closest('.slider-group');
        const options = sliderGroup.querySelectorAll('.slider-options span');
        const container = slider.closest('.slider-container');
        
        // Initialize
        updateSliderDisplay(slider, options);
        
        // Add snap points to slider
        slider.addEventListener('input', function() {
            updateSliderDisplay(this, options);
        });
        
        // Snap to nearest value on change
        slider.addEventListener('change', function() {
            const value = Math.round(this.value);
            this.value = value;
            updateSliderDisplay(this, options);
        });
        
        // Allow clicking on options
        options.forEach((option, index) => {
            option.addEventListener('click', function() {
                slider.value = index + 1;
                slider.dispatchEvent(new Event('input'));
                slider.dispatchEvent(new Event('change'));
            });
        });
    });
}

function updateSliderDisplay(slider, options) {
    const value = parseInt(slider.value);
    
    // Update active option
    options.forEach((option, index) => {
        if (index + 1 === value) {
            option.classList.add('active');
        } else {
            option.classList.remove('active');
        }
    });
    
    // Update slider track fill
    const percentage = ((value - 1) / 4) * 100;
    slider.style.background = `linear-gradient(to right, var(--primary) 0%, var(--primary) ${percentage}%, var(--border) ${percentage}%, var(--border) 100%)`;
}

// Navigation
function nextStep() {
    if (currentStep < totalSteps) {
        document.querySelector(`[data-step="${currentStep}"]`).classList.remove('active');
        currentStep++;
        document.querySelector(`[data-step="${currentStep}"]`).classList.add('active');
        updateProgress();
    }
}

function prevStep() {
    if (currentStep > 1) {
        document.querySelector(`[data-step="${currentStep}"]`).classList.remove('active');
        currentStep--;
        document.querySelector(`[data-step="${currentStep}"]`).classList.add('active');
        updateProgress();
    }
}

function updateProgress() {
    const percentage = (currentStep / totalSteps) * 100;
    document.getElementById('progressBar').style.width = percentage + '%';
    document.getElementById('progressText').textContent = `Step ${currentStep} of ${totalSteps}`;
    
    document.querySelectorAll('.dot').forEach((dot, index) => {
        if (index < currentStep - 1) {
            dot.classList.add('completed');
            dot.classList.remove('active');
        } else if (index === currentStep - 1) {
            dot.classList.add('active');
            dot.classList.remove('completed');
        } else {
            dot.classList.remove('active', 'completed');
        }
    });
}

// Submit form and generate review
async function submitAndGenerateReview() {
    nextStep();

    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('reviewDisplay').style.display = 'none';
    document.getElementById('reviewActions').style.display = 'none';
    document.getElementById('step3Nav').style.display = 'none';
    document.getElementById('statusText').style.display = 'none';

    try {
        const formData = new FormData(document.getElementById('reviewForm'));
        const response = await fetch(document.getElementById('reviewForm').action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        });

        const data = await response.json();

        if (data.success) {
            generatedReview = data.ai_review;
            googleUrl = data.google_url;

            document.getElementById('loadingSpinner').style.display = 'none';
            document.getElementById('reviewText').textContent = generatedReview;
            document.getElementById('reviewDisplay').style.display = 'block';
            document.getElementById('reviewActions').style.display = 'block';
            document.getElementById('step3Nav').style.display = 'flex';
            document.getElementById('statusText').style.display = 'block';
            document.getElementById('generationMethod').textContent = `Generated using ${data.generation_method}`;
        } else {
            throw new Error(data.error || 'Failed to generate review');
        }

    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loadingSpinner').innerHTML = 
            '<div style="color: #e53e3e;">❌ Error generating review. Please try again.</div>';

        setTimeout(() => {
            document.getElementById('step3Nav').style.display = 'flex';
        }, 2000);
    }
}

// Toggle edit mode
function toggleEditMode() {
    const reviewDisplay = document.getElementById('reviewDisplay');
    const reviewEditor = document.getElementById('reviewEditor');
    const editBtn = document.getElementById('editBtn');

    if (!isEditMode) {
        reviewEditor.value = generatedReview;
        reviewDisplay.style.display = 'none';
        reviewEditor.style.display = 'block';
        editBtn.textContent = '✅ Save Changes';
        isEditMode = true;
    } else {
        generatedReview = reviewEditor.value;
        document.getElementById('reviewText').textContent = generatedReview;
        reviewEditor.style.display = 'none';
        reviewDisplay.style.display = 'block';
        editBtn.textContent = '✏️ Edit Review';
        isEditMode = false;
    }
}

// Copy review and redirect to Google
async function copyAndRedirect() {
    try {
        await navigator.clipboard.writeText(generatedReview);

        const btn = document.querySelector('.btn-primary');
        const originalText = btn.innerHTML;
        btn.innerHTML = '✅ Copied! Redirecting...';
        btn.style.background = '#48bb78';
        btn.disabled = true;

        setTimeout(() => {
            window.location.href = googleUrl;
        }, 1500);

    } catch (err) {
        console.error('Clipboard copy failed:', err);

        try {
            const textArea = document.createElement('textarea');
            textArea.value = generatedReview;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);

            const btn = document.querySelector('.btn-primary');
            btn.innerHTML = '✅ Copied! Redirecting...';
            btn.style.background = '#48bb78';

            setTimeout(() => {
                window.location.href = googleUrl;
            }, 1500);

        } catch (fallbackErr) {
            console.error('All copy methods failed:', fallbackErr);
            alert('Please manually copy the review above, then click OK to go to Google Reviews.');
            window.location.href = googleUrl;
        }
    }
}

// Handle tag selection
document.addEventListener('DOMContentLoaded', function() {
    const tagButtons = document.querySelectorAll('.tag-btn');
    const selectedTagsInput = document.getElementById('selectedTags');
    let selectedTags = [];

    tagButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tag = this.getAttribute('data-tag');

            if (selectedTags.includes(tag)) {
                selectedTags = selectedTags.filter(t => t !== tag);
                this.style.background = '#edf2f7';
                this.style.color = 'inherit';
                this.style.borderColor = '#e2e8f0';
            } else {
                selectedTags.push(tag);
                this.style.background = '#4299e1';
                this.style.color = 'white';
                this.style.borderColor = '#4299e1';
            }

            selectedTagsInput.value = selectedTags.join(', ');
        });
    });

    const textarea = document.querySelector('textarea[name="feedback"]');
    const charCount = document.querySelector('.char-count');

    if (textarea && charCount) {
        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            charCount.textContent = `${currentLength}/280`;
        });
    }
});
