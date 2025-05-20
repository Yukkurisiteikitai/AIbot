document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const newChatBtn = document.getElementById('newChatBtn');

    // テキストエリアの自動リサイズ
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    });

    // メッセージ送信処理
    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessage('user', message);
            userInput.value = '';
            userInput.style.height = 'auto';
            
            // ここでAPIリクエストを送信
            // 仮の応答を表示
            setTimeout(() => {
                addMessage('assistant', 'これは仮の応答です。実際のAPIと連携する必要があります。');
            }, 1000);
        }
    }

    // メッセージの追加
    function addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = content;
        
        // コピーボタンの追加
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M8 4v12a2 2 0 002 2h8a2 2 0 002-2V7.242a2 2 0 00-.602-1.43L16.083 2.57A2 2 0 0014.685 2H10a2 2 0 00-2 2z"/>
                <path d="M16 18v2a2 2 0 01-2 2H6a2 2 0 01-2-2V9a2 2 0 012-2h2"/>
            </svg>
        `;
        
        copyButton.addEventListener('click', () => {
            navigator.clipboard.writeText(content).then(() => {
                // コピー成功時のフィードバック
                copyButton.classList.add('copied');
                setTimeout(() => {
                    copyButton.classList.remove('copied');
                }, 2000);
            });
        });
        
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(copyButton);
        chatMessages.appendChild(messageDiv);
        
        // スクロールを最下部に移動
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 送信ボタンのクリックイベント
    sendBtn.addEventListener('click', sendMessage);

    // Enterキーで送信（Shift + Enterで改行）
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // 新しいチャット開始
    newChatBtn.addEventListener('click', () => {
        chatMessages.innerHTML = '';
    });
}); 