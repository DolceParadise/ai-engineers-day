/**
 * KhetSetu - ChatGPT-like Frontend
 * Handles conversation UI, API communication, and state management
 */

// Configuration
const API_ENDPOINT = 'http://localhost:5001/ask';
const STORAGE_KEY = 'khetsetu_conversations';
const DARK_MODE_KEY = 'khetsetu_dark_mode';

const AGENT_METADATA = {
    'PromptAgent': { emoji: '💬', name: 'Prompt Agent' },
    'ParseAgent': { emoji: '📊', name: 'Parse Agent' },
    'ForecastAgent': { emoji: '⛅', name: 'Forecast Agent' },
    'WeatherHistoryAgent': { emoji: '📈', name: 'Weather History' },
    'SolutionAgent': { emoji: '🌱', name: 'Solution Agent' },
    'ReviewerAgent': { emoji: '✓', name: 'Reviewer Agent' }
};

// State
const state = {
    isLoading: false,
    currentConversation: [],
    conversationId: null,
    tokenUsage: { promptTokens: 0, completionTokens: 0 },
    agentDetails: [],
    allConversations: [],
    selectedImage: null
};

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const submitBtn = document.getElementById('submitBtn');
const queryForm = document.getElementById('queryForm');
const debugPanel = document.getElementById('debugPanel');
const debugToggle = document.getElementById('debugToggle');
const debugContent = document.getElementById('debugContent');
const newChatBtn = document.getElementById('newChatBtn');
const darkModeBtn = document.getElementById('darkModeBtn');
const savedChatsList = document.getElementById('savedChatsList');
const attachBtn = document.getElementById('attachBtn');
const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const previewName = document.getElementById('previewName');
const previewSize = document.getElementById('previewSize');
const removeImageBtn = document.getElementById('removeImageBtn');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    initializeDarkMode();
    loadConversations();
    queryForm.addEventListener('submit', handleSubmit);
    debugToggle?.addEventListener('click', toggleDebugPanel);
    newChatBtn?.addEventListener('click', resetConversation);
    darkModeBtn?.addEventListener('click', toggleDarkMode);
    attachBtn?.addEventListener('click', () => imageInput?.click());
    imageInput?.addEventListener('change', handleImageSelection);
    removeImageBtn?.addEventListener('click', clearSelectedImage);
    
    // Auto-expand textarea
    userInput.addEventListener('input', autoExpandTextarea);
    
    // Handle Enter key (submit) vs Shift+Enter (new line)
    userInput.addEventListener('keydown', handleKeyPress);
});

// Handle keyboard input for Enter vs Shift+Enter
function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        queryForm.dispatchEvent(new Event('submit'));
    }
    // Shift+Enter allows default behavior (new line)
}

// ============================================================================
// Dark Mode
// ============================================================================

function initializeDarkMode() {
    const isDarkMode = localStorage.getItem(DARK_MODE_KEY) === 'true';
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        darkModeBtn.textContent = '☀️';
    }
}

function toggleDarkMode() {
    const isDarkMode = document.body.classList.toggle('dark-mode');
    localStorage.setItem(DARK_MODE_KEY, isDarkMode);
    darkModeBtn.textContent = isDarkMode ? '☀️' : '🌙';
}

// ============================================================================
// Conversation Management
// ============================================================================

function loadConversations() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        state.allConversations = saved ? JSON.parse(saved) : [];
        renderConversationsList();
    } catch (error) {
        console.error('Error loading conversations:', error);
        state.allConversations = [];
    }
}

function saveConversations() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state.allConversations));
    } catch (error) {
        console.error('Error saving conversations:', error);
    }
}

function saveCurrentConversation() {
    if (state.conversationId && state.currentConversation.length > 0) {
        const index = state.allConversations.findIndex(c => c.id === state.conversationId);
        const title = state.currentConversation[0].text.substring(0, 30) + '...';
        const conversation = {
            id: state.conversationId,
            title: title,
            messages: state.currentConversation,
            timestamp: new Date().toISOString()
        };
        
        if (index >= 0) {
            state.allConversations[index] = conversation;
        } else {
            state.allConversations.unshift(conversation);
        }
        
        // Keep only last 20 conversations
        if (state.allConversations.length > 20) {
            state.allConversations = state.allConversations.slice(0, 20);
        }
        
        saveConversations();
        renderConversationsList();
    }
}

function renderConversationsList() {
    savedChatsList.innerHTML = '';
    
    if (state.allConversations.length === 0) return;
    
    state.allConversations.forEach(conv => {
        const item = document.createElement('button');
        item.className = 'saved-chat-item';
        
        const titleSpan = document.createElement('span');
        titleSpan.textContent = conv.title;
        titleSpan.style.flex = '1';
        titleSpan.style.textAlign = 'left';
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.textContent = '✕';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteConversation(conv.id);
        };
        
        item.appendChild(titleSpan);
        item.appendChild(deleteBtn);
        item.onclick = () => loadConversation(conv);
        
        savedChatsList.appendChild(item);
    });
}

function loadConversation(conversation) {
    state.conversationId = conversation.id;
    state.currentConversation = conversation.messages;
    chatMessages.innerHTML = '';
    
    conversation.messages.forEach(msg => {
        if (msg.type) {
            addMessage(msg.text, msg.type);
        }
    });
}

function deleteConversation(id) {
    state.allConversations = state.allConversations.filter(c => c.id !== id);
    saveConversations();
    renderConversationsList();
    showNotification('Conversation deleted', 'success');
}

// Handle form submission
async function handleSubmit(e) {
    e.preventDefault();
    
    const query = userInput.value.trim();
    if (!query && !state.selectedImage) return;
    
    // Generate conversation ID if needed
    if (!state.conversationId) {
        state.conversationId = Date.now().toString();
        state.currentConversation = [];
    }
    
    // Add user message to chat
    if (query) {
        addMessage(query, 'user');
        state.currentConversation.push({ text: query, type: 'user' });
    }
    if (state.selectedImage) {
        addImageMessage(state.selectedImage.dataUrl, 'user');
        state.currentConversation.push({ text: '[Image attached]', type: 'user' });
    }
    
    userInput.value = '';
    autoExpandTextarea();
    
    // Disable submit
    submitBtn.disabled = true;
    state.isLoading = true;
    
    // Add thinking indicator
    addMessage('Analyzing your query...', 'assistant-thinking');
    
    try {
        const payload = { user_input: query || 'Analyze the attached crop image and describe any visible issues.' };
        if (state.selectedImage?.base64) {
            payload.image_base64 = state.selectedImage.base64;
        }

        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // Remove thinking message
        const lastMessage = chatMessages.lastChild;
        if (lastMessage?.classList.contains('agent-thinking')) {
            lastMessage.remove();
        }
        
        // Process response
        if (data.status === 'success') {
            // Add agent messages
            data.agents.forEach(agent => {
                const msg = `${AGENT_METADATA[agent.name]?.emoji || '🤖'} ${agent.name}\n${agent.output}`;
                addMessage(msg, 'assistant-agent');
                state.currentConversation.push({ text: msg, type: 'assistant-agent' });
            });
            
            // Add final answer
            addMessage(data.final_answer, 'assistant');
            state.currentConversation.push({ text: data.final_answer, type: 'assistant' });
            
            // Update debug info
            state.tokenUsage = {
                promptTokens: data.token_summary.total_prompt_tokens,
                completionTokens: data.token_summary.total_completion_tokens
            };
            state.agentDetails = data.agents;
            
            // Show debug panel with data
            updateDebugPanel(data);
            debugPanel.classList.remove('hidden');
            
            // Save conversation
            saveCurrentConversation();
        } else {
            showNotification(data.message || 'Error processing query', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
        state.isLoading = false;
        clearSelectedImage();
    }
}

// Add message to chat
function addMessage(text, type = 'assistant') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    
    if (type === 'user') {
        avatar.textContent = '👤';
    } else if (type === 'assistant-agent') {
        avatar.textContent = '🤖';
    } else if (type === 'assistant-thinking') {
        avatar.textContent = '🤔';
    } else {
        avatar.textContent = '🌾';
    }
    
    // Content
    const content = document.createElement('div');
    content.className = 'message-content';
    
    if (type === 'assistant-thinking') {
        messageDiv.classList.add('agent-thinking');
        content.innerHTML = `<span class="thinking-dot"></span><span class="thinking-dot"></span><span class="thinking-dot"></span>`;
    } else {
        content.textContent = text;
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addImageMessage(dataUrl, type = 'user') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type} image-message`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? '👤' : '🌾';

    const content = document.createElement('div');
    content.className = 'message-content';
    const img = document.createElement('img');
    img.src = dataUrl;
    img.alt = 'Uploaded image';
    content.appendChild(img);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Toggle debug panel
function toggleDebugPanel() {
    debugContent.classList.toggle('hidden');
    debugToggle.classList.toggle('open');
}

// Update debug panel with data
function updateDebugPanel(data) {
    document.getElementById('promptTokens').textContent = data.token_summary.total_prompt_tokens;
    document.getElementById('completionTokens').textContent = data.token_summary.total_completion_tokens;
    document.getElementById('costValue').textContent = `$${data.token_summary.total_cost_usd.toFixed(6)}`;
    
    // Update agent table
    const tbody = document.getElementById('agentTableBody');
    tbody.innerHTML = '';
    
    data.agents.forEach(agent => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${agent.name}</td>
            <td>${agent.tokens.prompt_tokens + agent.tokens.completion_tokens}</td>
            <td>${agent.status}</td>
        `;
        tbody.appendChild(row);
    });
}

// Reset conversation
function resetConversation() {
    saveCurrentConversation();
    chatMessages.innerHTML = '';
    state.currentConversation = [];
    state.conversationId = null;
    state.tokenUsage = { promptTokens: 0, completionTokens: 0 };
    debugPanel.classList.add('hidden');
    clearSelectedImage();
    showNotification('Conversation cleared', 'success');
}

// Auto-expand textarea
function autoExpandTextarea() {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 150) + 'px';
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    const container = document.getElementById('notificationContainer');
    container.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.remove();
    }, 4000);
}

// ============================================================================
// Image Handling
// ============================================================================

function handleImageSelection(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
        showNotification('Please select a valid image file.', 'error');
        clearSelectedImage();
        return;
    }

    const maxSizeBytes = 5 * 1024 * 1024;
    if (file.size > maxSizeBytes) {
        showNotification('Image size must be under 5MB.', 'error');
        clearSelectedImage();
        return;
    }

    const reader = new FileReader();
    reader.onload = () => {
        const dataUrl = reader.result;
        const base64 = typeof dataUrl === 'string' ? dataUrl.split(',')[1] : null;
        state.selectedImage = {
            dataUrl,
            base64,
            name: file.name,
            size: file.size
        };
        previewImg.src = dataUrl;
        previewName.textContent = file.name;
        previewSize.textContent = formatBytes(file.size);
        imagePreview.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

function clearSelectedImage() {
    state.selectedImage = null;
    if (imageInput) {
        imageInput.value = '';
    }
    if (imagePreview) {
        imagePreview.classList.add('hidden');
    }
    if (previewImg) {
        previewImg.src = '';
    }
    if (previewName) {
        previewName.textContent = '';
    }
    if (previewSize) {
        previewSize.textContent = '';
    }
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}
