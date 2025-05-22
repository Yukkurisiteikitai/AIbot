document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const newChatBtn = document.getElementById('newChatBtn');

    let inputStartTime = null;
    let lastInputValue = '';
    let lastInputTime = null;
    let backspaceCount = 0;
    let inputHistory = [];
    let isThinking = false;
    let editHistory = [];

    // 差分検出と編集履歴の記録
    // function recordEdit(oldText, newText) {
    //     const diff = Diff.diffChars(oldText, newText);
    //     const edit = {
    //         time: new Date(),
    //         changes: diff.map(part => ({
    //             type: part.added ? 'added' : part.removed ? 'removed' : 'unchanged',
    //             value: part.value,
    //             count: part.count
    //         }))
    //     };
    //     editHistory.push(edit);
    //     return edit;
    // }
    function escapeHtml(unsafe) {
    if (typeof unsafe !== 'string') {
        // 文字列でない場合は、そのまま返すか、エラーを出すか、空文字にするなど
        // ここでは念のため文字列に変換しようと試みる
        try {
            unsafe = String(unsafe);
        } catch (e) {
            return ""; // 変換できなければ空文字
        }
    }
    return unsafe
         .replace(/&/g, "&")
         .replace(/</g, "<")
         .replace(/>/g, ">")
         .replace(/"/g, '"')
         .replace(/'/g, "'");
    }
    // 単一の編集イベントをHTMLに変換するヘルパー（デバッグ用や部分表示用）
    function generateSingleEditHTML(edit) {
        if (!edit || !edit.changes) return "";
        return edit.changes.map(change => {
            if (change.type === 'added') {
                return `<ins>${escapeHtml(change.value)}</ins>`;
            } else if (change.type === 'removed') {
                return `<del>${escapeHtml(change.value)}</del>`;
            }
            return escapeHtml(change.value);
        }).join('');
    }


    function recordEdit(oldText, newText) {
        if (oldText === newText) return null;
        const diff = Diff.diffChars(oldText, newText);
        const edit = {
            time: new Date(),
            changes: diff.map(part => ({
                type: part.added ? 'added' : part.removed ? 'removed' : 'common',
                value: part.value
            }))
        };
        editHistory.push(edit);
        console.log("Edit Recorded:", generateSingleEditHTML(edit)); // デバッグ用に単一の編集結果を表示
        return edit;
    }

    // 編集履歴のHTML表現を生成
    function generateEditHistoryHTML() {
        return editHistory.map(edit => {
            const changes = edit.changes.map(change => {
                if (change.type === 'added') {
                    return `<ins>${change.value}</ins>`;
                } else if (change.type === 'removed') {
                    return `<del>${change.value}</del>`;
                }
                return change.value;
            }).join('');
            return `${new Date(edit.time).toLocaleTimeString()}: ${changes}`;
        }).join('\n');
    }
    // 編集履歴のHTML表現を生成
    function generateEditHistory_text() {
        let temp_text = ""
        return editHistory.map(edit => {
            const changes_function = edit.changes.map(change => {
                if (change.type === 'added') {
                    temp_text+= `<ins>${change.value}</ins>`;
                     
                } else if (change.type === 'removed') {
                    temp_text+= `<del>${change.value}</del>`;
                }
                // return change.value;
            }).join('');
            // return `${new Date(edit.time).toLocaleTimeString()}: ${changes}`;
            return `${temp_text}`
        }).join('\n');
    }

    // 入力欄の状態分析
    function analyzeInputState() {
        const currentTime = new Date();
        const timeSinceLastInput = currentTime - lastInputTime;
        const currentValue = userInput.value;

        // 入力パターンの分析
        const inputPattern = {
            最後の入力からの経過時間: `${timeSinceLastInput}ミリ秒`,
            バックスペース使用回数: backspaceCount,
            入力履歴の長さ: inputHistory.length,
            現在の入力長: currentValue.length,
            思考中フラグ: isThinking,
            編集履歴: editHistory
        };

        // 思考状態の判定
        if (timeSinceLastInput > 5000 && currentValue.length > 0) {
            isThinking = true;
        } else if (timeSinceLastInput < 1000) {
            isThinking = false;
        }

        console.log('入力状態の分析:', inputPattern);
        return inputPattern;
    }

    // テキストエリアの自動リサイズと入力時間の計測
    // userInput.addEventListener('focus', () => {
    //     inputStartTime = new Date();
    //     lastInputTime = inputStartTime;
    //     lastInputValue = userInput.value;
    //     backspaceCount = 0;
    //     inputHistory = [];
    //     isThinking = false;
    //     editHistory = [];
    // });
    userInput.addEventListener('focus', () => {
        inputStartTime = new Date();
        lastInputTime = inputStartTime; // 思考中判定用
        previousText = userInput.value;   // フォーカス時のテキストを最初のスナップショットとする
        textBeforeComposition = userInput.value; // 同様に初期化
        backspaceCount = 0;
        isThinking = false;
        editHistory = [];
    });

    userInput.addEventListener('compositionstart', () => {
        isIMEComposing = true;
        textBeforeComposition = userInput.value; // 変換開始時のテキストを保存
    });

    userInput.addEventListener('compositionend', (event) => {
        isIMEComposing = false;
        const currentText = userInput.value; // 変換確定後のテキスト
        // 変換開始前のテキストと確定後のテキストで差分を取る
        recordEdit(textBeforeComposition, currentText);
        previousText = currentText; // 最後に記録したスナップショットを更新
        lastInputTime = new Date(); // 入力があったとみなす
    });

    userInput.addEventListener('input', (event) => {
        const currentTime = new Date();
        const currentValue = userInput.value;

        if (isIMEComposing) {
            // IME変換中は、ここでは詳細な差分記録をしない。
            // compositionend でまとめて処理する。
            // ただし、UIの更新（自動リサイズなど）や、変換中の最新テキストを
            // 他の何かに使う必要がある場合は、ここで処理する。
            userInput.style.height = 'auto';
            userInput.style.height = userInput.scrollHeight + 'px';
            // lastInputTime は更新しても良いかもしれない (思考中判定のため)
            // lastInputTime = currentTime;
            return;
        }

        // IME変換中でない場合の通常の編集 (半角入力、削除、コピペなど)
        // (ただし、compositionend直後にもinputイベントが発火する場合があるので、
        //  previousTextがcompositionendで更新された直後だと差分が出ない可能性がある。
        //  その場合は、compositionendでpreviousTextを更新した後に、
        //  ここで改めて差分を取る意味は薄いかもしれない。
        //  むしろ、BackspaceやDeleteなど、IMEを介さない明示的な編集を捉えるのが主目的)

        // 以下の条件を追加して、compositionend直後の不要なrecordEdit呼び出しを避ける
        if (currentValue !== previousText) {
             recordEdit(previousText, currentValue);
             previousText = currentValue; // スナップショットを更新
        }


        lastInputTime = currentTime; // 入力があったとみなす

        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';

        clearTimeout(thinkingTimeout);
        isThinking = false;
        thinkingTimeout = setTimeout(() => {
            if (userInput.value.length > 0) { // 入力がある場合のみ思考中と判断
                isThinking = true;
                console.log("思考中と判定されました。");
            }
        }, 3000);
    });


    userInput.addEventListener('input', () => {
        const currentTime = new Date();
        const currentValue = userInput.value;

        // 入力履歴の記録
        if (currentValue !== lastInputValue) {
            inputHistory.push({
                time: currentTime,
                value: currentValue,
                length: currentValue.length
            });

            // 編集履歴の記録
            recordEdit(lastInputValue, currentValue);
        }

        lastInputTime = currentTime;
        lastInputValue = currentValue;

        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    });

    // バックスペースキーの検出
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace') {
            backspaceCount++;
        }
    });

    // メッセージ送信処理
    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            const inputEndTime = new Date();
            const inputDuration = inputEndTime - inputStartTime;
            const inputChanges = message.length - lastInputValue.length;
            const inputState = analyzeInputState();

            console.log('入力の分析結果:', {
                文字数の変化: inputChanges,
                入力時間: `${inputDuration}ミリ秒`,
                最終入力内容: message,
                編集履歴: generateEditHistoryHTML(),
                編集テキスト: generateEditHistory_text(),
                入力状態: inputState
            });

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

    // // Enterキーで送信（Shift + Enterで改行）
    // userInput.addEventListener('keydown', (e) => {
    //     if (e.key === 'Enter' && !e.shiftKey) {
    //         e.preventDefault();
    //         sendMessage();
    //     }
    // });
    userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        if (e.isComposing || e.keyCode === 229) { // 229 は一部ブラウザでIME変換中を示すkeyCode
            // IME変換中のEnterなので、送信しない
            return;
        }

        if (!e.shiftKey) {
            // IME変換中でなく、Shiftキーも押されていないEnterなので送信する
            e.preventDefault(); // デフォルトの改行動作を防ぐ
            sendMessage();
        }
        // Shift + Enter の場合は、デフォルトの改行動作に任せる (送信しない)
    }
});

    // 新しいチャット開始
    newChatBtn.addEventListener('click', () => {
        chatMessages.innerHTML = '';
    });
}); 