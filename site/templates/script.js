// script.js

// --- DOM要素取得 ---
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const newChatBtn = document.getElementById('newChatBtn');

// --- API設定 ---
const API_BASE_URL = "http://localhost:49604"; // あなたのFastAPIサーバーのURL

// --- 状態変数 ---
let currentThreadId = null;
let currentQuestionIdToAnswer = null; // AIからの現在の質問ID
let messages = []; // チャットメッセージの配列: { id: string, role: 'user'|'assistant'|'system', content: string, isLoading?: boolean }
let currentUserIdForApi = 1; // 仮の認証済みユーザーID (実際にはログイン時に設定)


// ユーザー入力分析関連の変数はそのまま (必要に応じて)
let inputStartTime = null;
let previousText = '';
let lastInputTime = null;
let backspaceCount = 0;
let editHistory = [];
let isThinking = false;
let thinkingTimeout;
let isIMEComposing = false;
let textBeforeComposition = '';

// Googleログイン成功時のコールバック関数 
async function handleCredentialResponse(response) {
    const googleIdToken = response.credential;
    console.log("Got Google ID token: " + googleIdToken);

    try {
        // FastAPIの /auth/google/login エンドポイントにPOSTリクエストを送る
        const res = await fetch(`${API_BASE_URL}/auth/google/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // リクエストボディは {"token": "..."} の形にする
            body: JSON.stringify({ token: googleIdToken }) 
        });

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || 'Backend authentication failed');
        }

        const loginData = await res.json();
        console.log("Backend login successful:", loginData);

        // ★★★ GoogleのIDトークンをlocalStorageに保存する ★★★
        // これが今後のAPIアクセスのための「鍵」になる
        localStorage.setItem('googleIdToken', googleIdToken);
        
        // ユーザー情報をアプリ内で保持
        // currentUser = { id: loginData.user_id, email: loginData.user_email };

        // UIをログイン後の状態に更新
        // ...

    } catch (error) {
        console.error("Error during backend authentication:", error.message);
    }
}

// 保護されたAPIを呼び出すときの例
async function fetchMyProfile() {
    const token = localStorage.getItem('googleIdToken');
    if (!token) {
        console.error("Not logged in.");
        return;
    }

    const res = await fetch(`${API_BASE_URL}/users/me`, {
        headers: {
            // AuthorizationヘッダーにGoogleのIDトークンをセットする
            'Authorization': `Bearer ${token}`
        }
    });

    const myProfile = await res.json();
    console.log("My profile:", myProfile);
}


// --- UI更新関数 ---
function renderMessages() {
    chatMessages.innerHTML = ''; // 表示を一旦全てクリア
    messages.forEach(msgData => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${msgData.role}`;
        if (msgData.isLoading) {
            messageDiv.classList.add('loading');
        }

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = msgData.isLoading ? '<span class="dot-flashing"></span>' : escapeHtml(msgData.content).replace(/\n/g, '<br>');
        messageDiv.appendChild(messageContent);

        if (msgData.role === 'assistant' && !msgData.isLoading && msgData.content) {
            const copyButton = document.createElement('button');
            copyButton.className = 'copy-button';
            copyButton.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
            copyButton.title = "コピー";
            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(msgData.content).then(() => {
                    copyButton.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
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
    });
    chatMessages.scrollTop = chatMessages.scrollHeight; // 自動スクロール
}

// --- メッセージ状態操作関数 ---
function addMessageToState(role, content, isLoading = false) {
    const newMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`, // ユニークID生成
        role,
        content,
        isLoading
    };
    messages.push(newMessage);
    renderMessages(); // UIを更新
    return newMessage.id; // 追加したメッセージのIDを返す (後で更新するため)
}

function updateMessageInState(messageId, newContent, newIsLoading) {
    const messageIndex = messages.findIndex(msg => msg.id === messageId);
    if (messageIndex !== -1) {
        if (newContent !== undefined) messages[messageIndex].content = newContent;
        if (newIsLoading !== undefined) messages[messageIndex].isLoading = newIsLoading;
        renderMessages(); // UIを更新
    }
}

function removeLastMessageFromStateIfMatches(role, partialContent) {
    // 簡易的なロールバック用：最後に送信しようとしたメッセージを特定して削除する
    if (messages.length > 0) {
        const lastMessage = messages[messages.length - 1];
        if (lastMessage.role === role && lastMessage.content.startsWith(partialContent.substring(0,10))) {
            messages.pop();
            renderMessages();
            return true;
        }
    }
    return false;
}


// --- API呼び出し関数 ---
async function fetchAndDisplayNextAiQuestion() {
    if (!currentThreadId) {
        console.log("No active thread to fetch question for.");
        addMessageToState('system', 'チャットを開始してください。');
        return;
    }

    const loadingMsgId = addMessageToState('system', 'AIが次の質問を準備しています...', true);

    try {
        const response = await fetch(`${API_BASE_URL}/db/questions/users/${currentUserIdForApi}/next`); // currentUserIdForApi を使用
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `次の質問取得エラー: ${response.status}`);
        }
        const nextQuestionData = await response.json();

        updateMessageInState(loadingMsgId, '', false); // システムのローディングメッセージをクリア (または削除)
        // messages = messages.filter(msg => msg.id !== loadingMsgId); // または削除
        // renderMessages();


        if (nextQuestionData && nextQuestionData.question_text) {
            currentQuestionIdToAnswer = nextQuestionData.question_id;
            let aiDisplayMessage = `${nextQuestionData.question_text}`; // "AI: " プレフィックスはロールで表現
            if (nextQuestionData.guidance) {
                aiDisplayMessage += `\n\n(ガイダンス: ${nextQuestionData.guidance})`;
            }
            addMessageToState('assistant', aiDisplayMessage);
        } else {
            currentQuestionIdToAnswer = null;
            addMessageToState('assistant', nextQuestionData.guidance || "次の質問はありません。自由にお話しください。");
        }
    } catch (error) {
        console.error("Error fetching next AI question:", error);
        updateMessageInState(loadingMsgId, `次の質問取得エラー: ${error.message}`, false);
        currentQuestionIdToAnswer = null;
    }
}

// --- イベントハンドラ ---
newChatBtn.addEventListener('click', async () => {
    messages = []; // メッセージ状態をクリア
    renderMessages(); // UIをクリア
    currentThreadId = null;
    currentQuestionIdToAnswer = null;
    editHistory = [];

    const systemMsgId = addMessageToState('system', '新しいチャットを開始しています...', true);

    try {
        const threadPayload = {
            mode: 'chat',
            title: `New Chat ${new Date().toLocaleString()}`
        };
        const response = await fetch(`${API_BASE_URL}/db/threads/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(threadPayload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `スレッド作成エラー: ${response.status}`);
        }
        const newThread = await response.json();
        currentThreadId = newThread.thread_id;

        updateMessageInState(systemMsgId, `新しいチャット (ID: ${currentThreadId}) を開始しました。AIからの最初の質問を待ちます...`, false);
        console.log("New thread created:", currentThreadId);

        await fetchAndDisplayNextAiQuestion();

    } catch (error) {
        console.error("Error starting new chat:", error);
        updateMessageInState(systemMsgId, `チャット開始エラー: ${error.message}`, false);
    }
});

async function sendMessage() {
    const userMessageText = userInput.value.trim();
    if (!userMessageText || sendBtn.disabled) return;

    if (!currentThreadId) {
        addMessageToState('system', 'エラー: チャットが開始されていません。新しいチャットを開始してください。');
        console.error("sendMessage called without a valid currentThreadId.");
        return;
    }

    const inputEndTime = new Date();
    const inputDuration = inputStartTime ? (inputEndTime - inputStartTime) : 0;

    // UIにユーザーメッセージを即座に反映 (状態配列に追加して再描画)
    const userMsgDisplayId = addMessageToState('user', userMessageText);
    const currentUserInputForApi = userMessageText; // API送信用に保持 (userInputはクリアされるため)
    userInput.value = '';
    userInput.style.height = 'auto'; // 入力欄の高さをリセット
    sendBtn.disabled = true;
    userInput.disabled = true;

    const assistantLoadingMsgId = addMessageToState('assistant', '...', true); // AI応答のローディング表示

    // ユーザー入力行動の分析 (ここはそのまま)
    const editSummary = generateEditHistorySummary(editHistory);
    const behaviorInterpretation = interpretUserInputBehavior(inputDuration, editHistory, backspaceCount, currentUserInputForApi.length);
    console.log('--- ユーザー入力分析 ---');
    console.log(`入力時間: ${inputDuration / 1000}秒`, `編集概要: ${editSummary}`, `BS回数: ${backspaceCount}`, `解釈: ${behaviorInterpretation}`);
    console.log('----------------------');

    try {
        const messagePayload = {
            role: 'user',
            context: currentUserInputForApi
        };
        if (currentQuestionIdToAnswer) {
            messagePayload.answered_question_id = currentQuestionIdToAnswer;
        }

        const response = await fetch(`${API_BASE_URL}/db/threads/${currentThreadId}/messages/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(messagePayload)
        });

        if (!response.ok) {
            // 送信失敗: UIから仮表示したユーザーメッセージとAIローディングを削除
            messages = messages.filter(msg => msg.id !== userMsgDisplayId && msg.id !== assistantLoadingMsgId);
            renderMessages();
            const errorData = await response.json();
            addMessageToState('system', `メッセージ送信エラー: ${errorData.detail || response.status}`); // エラーをシステムメッセージとして表示
            throw new Error(errorData.detail || `メッセージ送信エラー: ${response.status}`); // ログ用
        }
        // ユーザーメッセージの保存成功
        const sentMessageData = await response.json();
        console.log("User message sent and saved:", sentMessageData);
        // APIから返ってきた正式なユーザーメッセージ情報でUIの状態を更新 (任意)
        // messages 配列の userMsgDisplayId のメッセージを sentMessageData で置き換えても良い

        // 成功したら、ローディング中のアシスタントメッセージは不要になるか、次の質問表示に置き換わる
        messages = messages.filter(msg => msg.id !== assistantLoadingMsgId); // ローディングを削除
        renderMessages(); // 一旦UIを更新

        currentQuestionIdToAnswer = null; // 回答したのでリセット
        await fetchAndDisplayNextAiQuestion(); // 次のAIの質問を取得・表示

    } catch (error) {
        console.error("Error in sendMessage flow:", error.message);
        // エラーが発生した場合、ローディング中のアシスタントメッセージをエラーメッセージに更新
        updateMessageInState(assistantLoadingMsgId, `エラー: ${error.message}`, false);
    } finally {
        sendBtn.disabled = false;
        userInput.disabled = false;
        if (document.activeElement !== userInput) { // 他の要素にフォーカスが移っていなければ
            userInput.focus();
        }
        // 入力セッションリセット処理
        inputStartTime = new Date();
        previousText = '';
        lastInputTime = inputStartTime;
        backspaceCount = 0;
        editHistory = [];
        isThinking = false;
    }
}

// --- UIイベントリスナー (フォーカス、IME、入力、キーダウン) ---
// これらは前回提示したもので問題ないはずです。
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

// newChatBtn.addEventListener('click', () => {
//     chatMessages.innerHTML = '';
//     userInput.value = '';
//     userInput.style.height = 'auto';
//     editHistory = []; // 新しいチャットで編集履歴もクリア
//     // console.log("New chat started.");
// });

// sendBtn.addEventListener('click', sendMessage);


// --- ユーティリティ関数 (escapeHtml, recordEdit, generateEditHistorySummary, interpretUserInputBehavior) ---
// これらも前回提示したもので問題ないはずです。
function escapeHtml(unsafe) {
    if (unsafe === null || typeof unsafe === 'undefined') { // ★ undefined や null の場合は空文字列を返す
        return "";
    }
    if (typeof unsafe !== 'string') {
        try { unsafe = String(unsafe); } catch (e) { return ""; }
    }
    return unsafe
         .replace(/&/g, "&")
         .replace(/</g, "<")
         .replace(/>/g, ">")
         .replace(/"/g, '"')
         .replace(/'/g, "'");
}

// recordEdit は jsdiff ライブラリ (Diff) が必要。もし使うならHTMLに <script src="https://cdnjs.cloudflare.com/ajax/libs/jsdiff/5.1.0/diff.min.js"></script> を追加
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



// 初期フォーカス
userInput.focus();
// 初期状態で最初の質問を取得 (任意)
// (async () => {
//     await new Promise(resolve => setTimeout(resolve, 100)); // DOM描画を待つ (もっと良い方法がある)
//     if (!currentThreadId) { // まだチャットが開始されていなければ
//          addMessageToState('system', '「新しいチャット」ボタンを押して会話を開始してください。');
//     }
// })();