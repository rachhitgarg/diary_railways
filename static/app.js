// API Base URL (will be automatically set to current domain)
const API_BASE = window.location.origin;

// DOM Elements
const diaryForm = document.getElementById('diary-form');
const diaryContent = document.getElementById('diary-content');
const moodSlider = document.getElementById('mood-slider');
const submitBtn = document.getElementById('submit-btn');
const statusDiv = document.getElementById('submission-status');
const reflectionDiv = document.getElementById('daily-reflection');
const reflectionBtn = document.getElementById('reflection-btn');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 AI Student Diary initialized');
    loadAnalytics();
    loadReflection();

    // Form submission
    if (diaryForm) {
        diaryForm.addEventListener('submit', handleSubmit);
    }

    // Load any saved draft
    loadDraft();
});

// Update mood label
function updateMoodLabel(value) {
    const labels = {
        '1': 'Very Sad 😢',
        '2': 'Sad 😔', 
        '3': 'Neutral 😐',
        '4': 'Happy 😊',
        '5': 'Very Happy 😄'
    };
    const labelElement = document.getElementById('mood-label');
    if (labelElement) {
        labelElement.textContent = labels[value] + ` (${value})`;
    }
}

// Handle form submission
async function handleSubmit(e) {
    e.preventDefault();

    const content = diaryContent.value.trim();
    const moodScore = parseInt(moodSlider.value) / 5.0;

    if (!content) {
        showStatus('Please write something in your diary!', 'error');
        return;
    }

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span>Analyzing...';
    showStatus('Processing your entry with AI...', 'loading');

    try {
        const response = await fetch(`${API_BASE}/api/v1/diary/entries`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                mood_score: moodScore,
                entry_type: 'text'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        showStatus(`✅ Entry saved! AI analysis in progress... (ID: ${result.entry_id.slice(0, 8)})`, 'success');

        // Clear form and draft
        diaryContent.value = '';
        moodSlider.value = 3;
        updateMoodLabel(3);
        clearDraft();

        // Refresh analytics
        setTimeout(() => {
            loadAnalytics();
            loadReflection();
        }, 2000);

    } catch (error) {
        console.error('Error:', error);
        showStatus(`❌ Error: ${error.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '💾 Save Entry & Get AI Insights';
    }
}

// Show status message
function showStatus(message, type) {
    if (statusDiv) {
        statusDiv.textContent = message;
        statusDiv.className = `status-message ${type}`;

        if (type === 'success') {
            setTimeout(() => {
                statusDiv.textContent = '';
                statusDiv.className = 'status-message';
            }, 5000);
        }
    }
}

// Load daily reflection
async function loadReflection() {
    const reflectionBtn = document.getElementById('reflection-btn');
    const reflectionDiv = document.getElementById('daily-reflection');

    if (!reflectionBtn || !reflectionDiv) return;

    reflectionBtn.disabled = true;
    reflectionBtn.innerHTML = '<span class="spinner"></span>Generating...';

    try {
        const response = await fetch(`${API_BASE}/api/v1/diary/reflection/daily`);

        if (response.ok) {
            const data = await response.json();
            reflectionDiv.innerHTML = `<p>${data.reflection}</p>`;
        } else {
            throw new Error('Failed to load reflection');
        }

    } catch (error) {
        console.error('Reflection error:', error);
        reflectionDiv.innerHTML = '<p>🌅 Good morning! Every new day brings fresh opportunities. You\'re doing great, keep going!</p>';
    } finally {
        reflectionBtn.disabled = false;
        reflectionBtn.innerHTML = '🔄 Get New Reflection';
    }
}

// Load analytics
async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/api/v1/analytics/overview`);

        if (response.ok) {
            const data = await response.json();

            const totalEntriesEl = document.getElementById('total-entries');
            const avgMoodEl = document.getElementById('avg-mood');
            const streakDaysEl = document.getElementById('streak-days');

            if (totalEntriesEl) totalEntriesEl.textContent = data.total_entries || 0;
            if (avgMoodEl) avgMoodEl.textContent = data.mood_average ? 
                (data.mood_average * 5).toFixed(1) : '-';
            if (streakDaysEl) streakDaysEl.textContent = data.streak_days || 0;
        }

    } catch (error) {
        console.error('Analytics error:', error);
    }
}

// Auto-save draft functionality
let draftTimer;
if (diaryContent) {
    diaryContent.addEventListener('input', function() {
        clearTimeout(draftTimer);
        draftTimer = setTimeout(() => {
            if (diaryContent.value.trim()) {
                localStorage.setItem('diary_draft', diaryContent.value);
                localStorage.setItem('diary_draft_mood', moodSlider.value);
            }
        }, 1000);
    });
}

// Load draft on page load
function loadDraft() {
    if (diaryContent && moodSlider) {
        const draft = localStorage.getItem('diary_draft');
        const draftMood = localStorage.getItem('diary_draft_mood');

        if (draft && !diaryContent.value) {
            diaryContent.value = draft;
        }

        if (draftMood) {
            moodSlider.value = draftMood;
            updateMoodLabel(draftMood);
        }
    }
}

// Clear draft
function clearDraft() {
    localStorage.removeItem('diary_draft');
    localStorage.removeItem('diary_draft_mood');
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (diaryContent && document.activeElement === diaryContent) {
            e.preventDefault();
            if (diaryForm) {
                diaryForm.dispatchEvent(new Event('submit'));
            }
        }
    }
});

// Add some visual feedback
function addVisualFeedback() {
    // Add pulse animation to cards when they update
    const cards = document.querySelectorAll('.stat-card');
    cards.forEach(card => {
        card.addEventListener('animationend', () => {
            card.classList.remove('pulse');
        });
    });
}

// Initialize visual feedback
addVisualFeedback();

// Error handling for network issues
window.addEventListener('online', function() {
    showStatus('✅ Connection restored', 'success');
});

window.addEventListener('offline', function() {
    showStatus('⚠️ You\'re offline. Your draft will be saved locally.', 'error');
});

// Welcome message for first-time users
if (!localStorage.getItem('welcomed')) {
    setTimeout(() => {
        showStatus('👋 Welcome to your AI Student Diary! Start by writing about your day above.', 'success');
        localStorage.setItem('welcomed', 'true');
    }, 1000);
}

console.log('📱 AI Student Diary ready! Try writing your first entry.');
