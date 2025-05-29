const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const newChatBtn = document.getElementById('newChatBtn');

    // --- API設定 ---
    const LM_STUDIO_API_URL = 'http://localhost:8001/ask'; // FastAPIサーバーのURL
    const DEFAULT_MODEL_ID = "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"; // LM Studioでロード済みのモデルID (適宜変更)

    // --- 状態変数 ---
    let inputStartTime = null; // フォーカス時の時間
    let previousText = '';     // 差分比較用の直前のテキスト
    let lastInputTime = null;  // 最後のキー入力時間
    let backspaceCount = 0;
    let editHistory = [];      // 編集操作の履歴
    let isThinking = false;    // ユーザーが思考中かどうかのフラグ (簡易版)
    let thinkingTimeout;       // 思考中判定用のタイマー
    let isIMEComposing = false; // IME変換中かどうかのフラグ
    let textBeforeComposition = ''; // IME変換開始前のテキスト

    // --- ask関数 (LM Studio APIと通信) ---
    /**
     * LM Studio APIに質問を送信し、回答を取得します。
     * @param {string} question - モデルに尋ねたい質問。
     * @param {object} [options={}] - オプションのパラメータ。
     * @param {string} [options.model] - 使用するモデルのID。
     * @param {string} [options.system_prompt] - システムプロンプト。
     * @param {number} [options.temperature] - 生成の温度 (0.0〜2.0)。
     * @param {number} [options.max_tokens] - 最大生成トークン数。
     * @param {object} [options.userInputAnalysis] - ユーザー入力分析情報
     * @returns {Promise<object>} サーバーからのレスポンス。
     */
    async function askLMStudio(question, options = {}) {
        const payload = {
            question: question,
            model: options.model || DEFAULT_MODEL_ID,
            system_prompt: options.system_prompt,
            temperature: options.temperature,
            max_tokens: options.max_tokens,
            // userInputAnalysis: options.userInputAnalysis // API側が対応していれば送信
        };

        console.log("Sending to LM Studio:", payload); // デバッグ用

        try {
            const response = await fetch(LM_STUDIO_API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                let errorDetails = `HTTP error! Status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorDetails = errorData.error || JSON.stringify(errorData);
                } catch (e) {
                    const textError = await response.text();
                    errorDetails += textError ? ` - ${textError}` : " - No further details from server.";
                }
                throw new Error(errorDetails);
            }
            return await response.json();
        } catch (error) {
            console.error("Error calling LM Studio API:", error);
            throw error; // 呼び出し元で処理できるように再スロー
        }
    }


    // --- 編集履歴と入力分析 ---
    function escapeHtml(unsafe) {
        if (typeof unsafe !== 'string') {
            try { unsafe = String(unsafe); } catch (e) { return ""; }
        }
        return unsafe
             .replace(/&/g, "&") // & を最初にエスケープ
             .replace(/</g, "<")
             .replace(/>/g, ">")
             .replace(/"/g, '"')
             .replace(/'/g, "'");
    }

    function recordEdit(oldText, newText) {
        if (oldText === newText || typeof Diff === 'undefined') return null; // Diffライブラリがない場合は何もしない
        try {
            const diff = Diff.diffChars(oldText, newText);
            const edit = {
                time: new Date(),
                changes: diff.map(part => ({
                    type: part.added ? 'added' : part.removed ? 'removed' : 'common',
                    value: part.value
                }))
            };
            editHistory.push(edit);
            // console.log("Edit Recorded:", edit); // デバッグ用
            return edit;
        } catch(e) {
            console.error("Error in recordEdit (jsdiff):", e);
            return null;
        }
    }

    function generateEditHistorySummary(history) {
        if (!history || history.length === 0) return "編集はありませんでした。";

        let addedChars = 0;
        let removedChars = 0;
        let edits = history.length;

        history.forEach(edit => {
            edit.changes.forEach(change => {
                if (change.type === 'added') addedChars += change.value.length;
                if (change.type === 'removed') removedChars += change.value.length;
            });
        });
        return `編集回数: ${edits}, 追加文字数: ${addedChars}, 削除文字数: ${removedChars}`;
    }

    function interpretUserInputBehavior(durationMs, history, backspaceCount, finalLength) {
        const seconds = durationMs / 1000;
        let interpretation = "";

        if (seconds < 2 && history.length <= 1 && finalLength > 0) {
            interpretation = "ユーザーは迅速に入力し、明確な意図を持っていた可能性があります。";
        } else if (seconds > 15 || history.length > 5 || backspaceCount > 10) {
            interpretation = "ユーザーは時間をかけて熟考したか、入力内容に迷いがあった可能性があります。多くの編集やバックスペースが見られます。";
        } else if (history.length > 2 && backspaceCount > 3) {
            interpretation = "ユーザーは何度か修正を加えながら入力したようです。";
        } else if (finalLength === 0 && durationMs > 1000) {
            interpretation = "ユーザーは何かを入力しようとしましたが、最終的に削除しました。";
        } else {
            interpretation = "ユーザーは標準的なペースで入力したようです。";
        }

        if (isThinking) { // グローバルなisThinkingフラグも考慮
            interpretation += " また、送信前には一定時間思考していた可能性があります。";
        }

        return interpretation;
    }


    // --- UIイベントリスナー ---
    userInput.addEventListener('focus', () => {
        inputStartTime = new Date();
        lastInputTime = inputStartTime;
        previousText = userInput.value;
        textBeforeComposition = userInput.value;
        backspaceCount = 0;
        isThinking = false;
        editHistory = []; // 新しい入力セッションのために編集履歴をリセット
        // console.log("Focus: Input session started.");
    });

    userInput.addEventListener('compositionstart', () => {
        isIMEComposing = true;
        textBeforeComposition = userInput.value;
    });

    userInput.addEventListener('compositionend', () => {
        isIMEComposing = false;
        const currentText = userInput.value;
        recordEdit(textBeforeComposition, currentText);
        previousText = currentText;
        lastInputTime = new Date();
        userInput.dispatchEvent(new Event('input', { bubbles: true })); // inputイベントを強制発火させてリサイズなどをトリガー
    });


    userInput.addEventListener('input', () => {
        const currentTime = new Date();
        const currentValue = userInput.value;

        if (isIMEComposing) {
            userInput.style.height = 'auto';
            userInput.style.height = userInput.scrollHeight + 'px';
            return; // IME変換中は詳細な差分記録をcompositionendに任せる
        }

        // IME変換中でない通常の編集
        if (currentValue !== previousText) {
            recordEdit(previousText, currentValue);
            previousText = currentValue;
        }

        lastInputTime = currentTime;
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';

        // 思考中判定のロジック
        clearTimeout(thinkingTimeout);
        isThinking = false; // 入力があったら一旦リセット
        thinkingTimeout = setTimeout(() => {
            // currentTime (inputイベント発生時) と lastInputTime (最後のキー入力) を比較
            // または、単純に現在時刻とlastInputTimeを比較しても良い
            const now = new Date();
            if ((now - lastInputTime) >= 2900 && userInput.value.length > 0) { // 3秒近く入力がなければ
                isThinking = true;
                // console.log("思考中と判定されました。");
            }
        }, 3000); // 3秒間入力がなければ思考中とみなす
    });

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace') {
            backspaceCount++;
        }
        if (e.key === 'Enter') {
            if (e.isComposing || e.keyCode === 229) { // IME変換中のEnter
                return;
            }
            if (!e.shiftKey) { // ShiftなしEnter
                e.preventDefault();
                sendMessage();
            }
        }
    });

    sendBtn.addEventListener('click', sendMessage);

    newChatBtn.addEventListener('click', () => {
        chatMessages.innerHTML = '';
        userInput.value = '';
        userInput.style.height = 'auto';
        editHistory = []; // 新しいチャットで編集履歴もクリア
        // console.log("New chat started.");
    });


    // --- メッセージ処理 ---
    async function sendMessage() {
        const userMessageText = userInput.value.trim();
        if (!userMessageText || sendBtn.disabled) return; // 空メッセージか送信処理中なら何もしない

        const inputEndTime = new Date();
        const inputDuration = inputStartTime ? (inputEndTime - inputStartTime) : 0;

        addMessage('user', userMessageText);
        const currentUserInput = userInput.value; // API送信前に保存
        userInput.value = '';
        userInput.style.height = 'auto';
        sendBtn.disabled = true;
        userInput.disabled = true;
        addMessage('assistant', '...', true); // ローディング表示

        // ユーザー入力行動の分析
        const editSummary = generateEditHistorySummary(editHistory);
        const behaviorInterpretation = interpretUserInputBehavior(inputDuration, editHistory, backspaceCount, currentUserInput.length);

        console.log('--- ユーザー入力分析 ---');
        console.log(`入力時間: ${inputDuration / 1000}秒`);
        console.log(`編集履歴の概要: ${editSummary}`);
        console.log(`バックスペース回数: ${backspaceCount}`);
        console.log(`入力行動の解釈: ${behaviorInterpretation}`);
        console.log('----------------------');

        // LM Studioに渡すシステムプロンプトに行動分析を付加
        const systemPromptWithAnalysis = `あなたはユーザーをサポートする親切なアシスタントです。
ユーザーは現在、以下の状況で質問をしています。これを考慮して、より適切と思われる応答をしてください。
入力にかかった時間: ${Math.round(inputDuration / 1000)}秒
編集の概要: ${editSummary}
バックスペース使用回数: ${backspaceCount}回
入力行動の推測: ${behaviorInterpretation}
---
ユーザーの質問に答えてください。`;

        try {
            const response = await askLMStudio(currentUserInput, {
                system_prompt: systemPromptWithAnalysis,
                // model: "your-specific-model-id", // 必要なら指定
                max_tokens: 500, // 応答の長さを調整
                temperature: 0.7
            });

            updateLastAssistantMessage(response.answer || "申し訳ありません、応答を取得できませんでした。");
            console.log("LM Studio Response:", response);

        } catch (error) {
            updateLastAssistantMessage(`エラーが発生しました: ${error.message}`);
        } finally {
            sendBtn.disabled = false;
            userInput.disabled = false;
            userInput.focus();
            // 新しい入力セッションの準備
            inputStartTime = new Date(); // すぐに次の入力を開始できるように
            previousText = '';
            lastInputTime = inputStartTime;
            backspaceCount = 0;
            editHistory = [];
            isThinking = false;
        }
    }

    function addMessage(role, content, isLoading = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        if (isLoading) {
            messageDiv.classList.add('loading');
        }

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = isLoading ? '<span class="dot-flashing"></span>' : escapeHtml(content).replace(/\n/g, '<br>'); // HTMLとして解釈＆改行を<br>に

        messageDiv.appendChild(messageContent);

        if (role === 'assistant' && !isLoading) { // アシスタントのメッセージで、ローディングでない場合のみコピーボタン追加
            const copyButton = document.createElement('button');
            copyButton.className = 'copy-button';
            copyButton.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
            copyButton.title = "コピー";

            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(content).then(() => {
                    copyButton.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`; // チェックマーク
                    copyButton.classList.add('copied');
                    setTimeout(() => {
                        copyButton.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
                        copyButton.classList.remove('copied');
                    }, 2000);
                }).catch(err => console.error('コピーに失敗しました:', err));
            });
            messageDiv.appendChild(copyButton);
        }
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function updateLastAssistantMessage(content) {
        const loadingMessage = chatMessages.querySelector('.message.assistant.loading');
        if (loadingMessage) {
            const messageContent = loadingMessage.querySelector('.message-content');
            messageContent.innerHTML = escapeHtml(content).replace(/\n/g, '<br>'); // HTMLとして解釈
            loadingMessage.classList.remove('loading');

            // コピーボタンをここでも追加 (addMessageとロジックを共通化しても良い)
            const copyButton = document.createElement('button');
            copyButton.className = 'copy-button';
            copyButton.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
            copyButton.title = "コピー";
            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(content).then(() => {
                    copyButton.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
                    copyButton.classList.add('copied');
                    setTimeout(() => {
                        copyButton.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
                        copyButton.classList.remove('copied');
                    }, 2000);
                }).catch(err => console.error('コピーに失敗しました:', err));
            });
            loadingMessage.appendChild(copyButton);
        }
    }

    // 初期フォーカス
    userInput.focus();