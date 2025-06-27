import React, { useState, useEffect, useRef } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  Platform,
  KeyboardAvoidingView,
  ActivityIndicator,
} from 'react-native';

// インストールしたライブラリをインポート
import { GoogleSignin, GoogleSigninButton, statusCodes } from '@react-native-google-signin/google-signin';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Svg, Path, Rect, Polyline } from 'react-native-svg';
import * as Diff from 'diff';

// --- アイコンコンポーネント ---
const SendIcon = () => (
  <Svg viewBox="0 0 24 24" width="24" height="24" stroke="white" strokeWidth="2" fill="none">
    <Path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z" />
  </Svg>
);
const CopyIcon = () => (
    <Svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <Rect x="9" y="9" width="13" height="13" rx="2" ry="2"></Rect>
        <Path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></Path>
    </Svg>
);
const CopiedIcon = () => (
    <Svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <Polyline points="20 6 9 17 4 12"></Polyline>
    </Svg>
);


const App = () => {
  // --- API設定 ---
  const API_BASE_URL = "http://localhost:49604"; // あなたのFastAPIサーバーのURL

  // --- 状態変数 (useState) ---
  const [messages, setMessages] = useState([]);
  const [currentThreadId, setCurrentThreadId] = useState(null);
  const [currentQuestionIdToAnswer, setCurrentQuestionIdToAnswer] = useState(null);
  const [userInput, setUserInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [userInfo, setUserInfo] = useState(null); // ログインユーザー情報

  // --- ユーザー入力分析関連 (useRef) ---
  // useRefは再レンダリングを引き起こさずに値を保持するために使用
  const inputStartTime = useRef(null);
  const previousText = useRef('');
  const backspaceCount = useRef(0);
  const editHistory = useRef([]);
  
  const flatListRef = useRef(null);

  // --- Googleログイン設定 ---
  useEffect(() => {
    GoogleSignin.configure({
      // webClientIdは必須。バックエンドでトークンを検証するために使用します。
      webClientId: '1005374369285-8bpog8tb96bk34rc7l0qo82fcqm76s2g.apps.googleusercontent.com',
      offlineAccess: true, // idTokenを取得するために必要
    });
    // 既存のログインセッションを確認
    checkCurrentUser();
  }, []);

  const checkCurrentUser = async () => {
    try {
        const idToken = await AsyncStorage.getItem('googleIdToken');
        if (idToken) {
            // ここでトークンを使ってユーザー情報を取得する処理を入れても良い
            const userInfo = await GoogleSignin.signInSilently();
            setUserInfo(userInfo);
            console.log("User already logged in:", userInfo);
            // TODO: ログイン後のチャット履歴読み込みなどを実装
        }
    } catch (error) {
        if (error.code !== statusCodes.SIGN_IN_REQUIRED) {
            console.error("checkCurrentUser error", error);
        }
    }
  };


  // --- Googleログイン処理 ---
  const handleGoogleSignIn = async () => {
    try {
      await GoogleSignin.hasPlayServices();
      const { idToken } = await GoogleSignin.signIn();
      console.log("Got Google ID token:", idToken);

      // FastAPIのバックエンドにトークンを送信して認証
      const res = await fetch(`${API_BASE_URL}/auth/google/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: idToken }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Backend authentication failed');
      }

      const loginData = await res.json();
      console.log("Backend login successful:", loginData);

      // トークンをAsyncStorageに保存
      await AsyncStorage.setItem('googleIdToken', idToken);
      
      // ユーザー情報を状態に保存してUIを更新
      const gUserInfo = await GoogleSignin.getCurrentUser();
      setUserInfo(gUserInfo);

    } catch (error) {
      if (error.code === statusCodes.SIGN_IN_CANCELLED) {
        console.log('User cancelled the login flow');
      } else if (error.code === statusCodes.IN_PROGRESS) {
        console.log('Sign in is in progress already');
      } else if (error.code === statusCodes.PLAY_SERVICES_NOT_AVAILABLE) {
        console.log('Play services not available or outdated');
      } else {
        console.error("Error during Google Sign-In:", error.message);
      }
    }
  };

  // --- メッセージ状態操作関数 ---
  // UI更新は setMessages が自動的に行う
  const addMessage = (role, content, isLoading = false) => {
    const newMessage = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      role,
      content,
      isLoading,
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  };

  const updateMessage = (messageId, newContent, newIsLoading) => {
    setMessages(prev =>
      prev.map(msg => {
        if (msg.id === messageId) {
          const updatedMsg = { ...msg };
          if (newContent !== undefined) updatedMsg.content = newContent;
          if (newIsLoading !== undefined) updatedMsg.isLoading = newIsLoading;
          return updatedMsg;
        }
        return msg;
      })
    );
  };
  
  const removeMessage = (messageId) => {
    setMessages(prev => prev.filter(msg => msg.id !== messageId));
  };


  // --- API呼び出し関数 ---
  const fetchAndDisplayNextAiQuestion = async (threadId) => {
    const loadingMsgId = addMessage('system', 'AIが次の質問を準備しています...', true);

    try {
      const response = await fetch(`${API_BASE_URL}/db/questions/users/1/next`); // TODO: ログインユーザーIDを使う
      if (!response.ok) {
        throw new Error(`次の質問取得エラー: ${response.status}`);
      }
      const nextQuestionData = await response.json();
      
      removeMessage(loadingMsgId); // システムのローディングメッセージを削除

      if (nextQuestionData && nextQuestionData.question_text) {
        setCurrentQuestionIdToAnswer(nextQuestionData.question_id);
        let aiDisplayMessage = `${nextQuestionData.question_text}`;
        if (nextQuestionData.guidance) {
          aiDisplayMessage += `\n\n(ガイダンス: ${nextQuestionData.guidance})`;
        }
        addMessage('assistant', aiDisplayMessage);
      } else {
        setCurrentQuestionIdToAnswer(null);
        addMessage('assistant', nextQuestionData.guidance || "次の質問はありません。自由にお話しください。");
      }
    } catch (error) {
      console.error("Error fetching next AI question:", error);
      updateMessage(loadingMsgId, `次の質問取得エラー: ${error.message}`, false);
      setCurrentQuestionIdToAnswer(null);
    }
  };

  // --- イベントハンドラ ---
  const handleNewChat = async () => {
    setMessages([]);
    setCurrentThreadId(null);
    setCurrentQuestionIdToAnswer(null);
    editHistory.current = [];

    const systemMsgId = addMessage('system', '新しいチャットを開始しています...', true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/db/threads/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'chat', title: `New Chat ${new Date().toLocaleString()}` }),
      });
      if (!response.ok) throw new Error(`スレッド作成エラー: ${response.status}`);
      
      const newThread = await response.json();
      setCurrentThreadId(newThread.thread_id);
      
      updateMessage(systemMsgId, `新しいチャット (ID: ${newThread.thread_id}) を開始しました。`, false);
      
      await fetchAndDisplayNextAiQuestion(newThread.thread_id);
    } catch (error) {
      console.error("Error starting new chat:", error);
      updateMessage(systemMsgId, `チャット開始エラー: ${error.message}`, false);
    }
  };

  const handleSendMessage = async () => {
    const userMessageText = userInput.trim();
    if (!userMessageText || isSending) return;

    if (!currentThreadId) {
      addMessage('system', 'エラー: チャットが開始されていません。「新しいチャット」を開始してください。');
      return;
    }

    setIsSending(true);
    addMessage('user', userMessageText);
    setUserInput(''); // 入力欄をクリア

    const assistantLoadingMsgId = addMessage('assistant', '', true);

    try {
        const messagePayload = {
            role: 'user',
            context: userMessageText,
            ...(currentQuestionIdToAnswer && { answered_question_id: currentQuestionIdToAnswer }),
        };

        const response = await fetch(`${API_BASE_URL}/db/threads/${currentThreadId}/messages/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(messagePayload),
        });

        if (!response.ok) {
            // TODO: エラーハンドリングを改善
            throw new Error(`メッセージ送信エラー: ${response.status}`);
        }
        
        removeMessage(assistantLoadingMsgId);
        setCurrentQuestionIdToAnswer(null);
        await fetchAndDisplayNextAiQuestion(currentThreadId);

    } catch (error) {
        console.error("Error in sendMessage flow:", error);
        updateMessage(assistantLoadingMsgId, `エラー: ${error.message}`, false);
    } finally {
        setIsSending(false);
    }
  };
  
  // 入力分析ロジック (元の関数を流用)
  const handleTextInputChange = (text) => {
    // jsdiffを使った編集履歴の記録
    const diff = Diff.diffChars(previousText.current, text);
    const edit = {
        time: new Date(),
        changes: diff.map(part => ({
            type: part.added ? 'added' : part.removed ? 'removed' : 'common',
            value: part.value
        }))
    };
    editHistory.current.push(edit);
    previousText.current = text;
    setUserInput(text);
  };


  // --- レンダリング部分 ---
  const renderMessageItem = ({ item }) => {
    const isUser = item.role === 'user';
    const isAssistant = item.role === 'assistant';
    const isSystem = item.role === 'system';

    return (
      <View style={[styles.messageRow, isUser ? styles.userMessageRow : styles.assistantMessageRow]}>
        <View style={[styles.messageBubble, isUser ? styles.userMessageBubble : isAssistant ? styles.assistantMessageBubble : styles.systemMessageBubble]}>
          {item.isLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.messageText}>{item.content}</Text>
          )}
          {isAssistant && !item.isLoading && item.content && (
              <TouchableOpacity style={styles.copyButton}>
                  <CopyIcon />
              </TouchableOpacity>
          )}
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.sidebar}>
        <TouchableOpacity style={styles.newChatButton} onPress={handleNewChat}>
          <Text style={styles.newChatButtonText}>+ 新しいチャット</Text>
        </TouchableOpacity>
        <View style={styles.historyContainer}>
          {/* TODO: チャット履歴リストをここに表示 */}
          {!userInfo ? (
             <GoogleSigninButton
                style={{ width: '100%', height: 48, marginTop: 20 }}
                size={GoogleSigninButton.Size.Wide}
                color={GoogleSigninButton.Color.Dark}
                onPress={handleGoogleSignIn}
                disabled={false}
              />
          ) : (
            <View style={styles.userInfo}>
                <Text style={styles.userInfoText}>ログイン中:</Text>
                <Text style={styles.userInfoText}>{userInfo.user.email}</Text>
            </View>
          )}
        </View>
      </View>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.mainContent}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessageItem}
          keyExtractor={(item) => item.id}
          style={styles.chatMessages}
          contentContainerStyle={{ paddingVertical: 20 }}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          onLayout={() => flatListRef.current?.scrollToEnd({ animated: true })}
        />
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.userInput}
            value={userInput}
            onChangeText={handleTextInputChange}
            placeholder="メッセージを入力..."
            placeholderTextColor="#8e8ea0"
            multiline
            editable={!isSending}
          />
          <TouchableOpacity style={styles.sendButton} onPress={handleSendMessage} disabled={isSending || !userInput.trim()}>
             <SendIcon />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};


// --- スタイル (StyleSheet) ---
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#202123',
    flexDirection: 'row',
  },
  sidebar: {
    width: 260,
    backgroundColor: '#202123',
    padding: 10,
    borderRightWidth: 1,
    borderRightColor: '#343541',
  },
  newChatButton: {
    padding: 12,
    backgroundColor: '#343541',
    borderWidth: 1,
    borderColor: '#565869',
    borderRadius: 4,
    alignItems: 'center',
    marginBottom: 16,
  },
  newChatButtonText: {
    color: '#fff',
    fontSize: 16,
  },
  historyContainer: {
    flex: 1,
  },
  userInfo: {
    marginTop: 'auto',
    padding: 10,
    borderTopWidth: 1,
    borderColor: '#565869'
  },
  userInfoText: {
    color: '#ccc',
    fontSize: 12,
  },
  mainContent: {
    flex: 1,
    backgroundColor: '#343541',
  },
  chatMessages: {
    flex: 1,
    paddingHorizontal: 16,
  },
  messageRow: {
    flexDirection: 'row',
    marginVertical: 8,
  },
  userMessageRow: {
    justifyContent: 'flex-end',
  },
  assistantMessageRow: {
    justifyContent: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 8,
    position: 'relative',
  },
  userMessageBubble: {
    backgroundColor: '#2b2c2f',
  },
  assistantMessageBubble: {
    backgroundColor: '#444654',
  },
  systemMessageBubble: {
      backgroundColor: 'transparent',
      alignSelf: 'center',
  },
  messageText: {
    color: '#fff',
    fontSize: 16,
    lineHeight: 22,
  },
  copyButton: {
    position: 'absolute',
    top: 8,
    right: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderTopWidth: 1,
    borderTopColor: '#565869',
    backgroundColor: '#40414f',
  },
  userInput: {
    flex: 1,
    backgroundColor: '#40414f',
    color: '#fff',
    padding: 10,
    borderRadius: 8,
    fontSize: 16,
    lineHeight: 20,
    maxHeight: 120, // 複数行の最大高さを設定
  },
  sendButton: {
    marginLeft: 12,
    padding: 8,
  },
});

export default App;