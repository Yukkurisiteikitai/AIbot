import json
import logging
from typing import Dict, List, Optional, Union, Set
import db_manager
from datetime import datetime
from question_agent.llm_analyzer import LLMAnalyzer
import asyncio

logger = logging.getLogger('discord')

class EpisodeHandler:
    def __init__(self, llm_analyzer: LLMAnalyzer):
        self.llm_analyzer = llm_analyzer
        # 進行中のエピソードを追跡
        self.active_episodes: Dict[int, Dict] = {}  # user_id -> active_episode
        # エピソードの完了に必要な情報
        self.required_info: Set[str] = {'when', 'where', 'who', 'what', 'how'}

        self.content_type_prompt = """
        以下のテキストは、どのような種類の情報を含んでいますか？
        選択肢：事実の記述、意見の表明、感情の吐露、過去の出来事の回想、価値観の表明、目標設定、質問、その他
        最も適切なものを一つ選んでください。

        テキスト：{text}

        種類：
        """

        self.emotion_analysis_prompt = """
        以下のテキストから読み取れる主要な感情、その強度（0.0-1.0）、全体的な感情の極性（positive, negative, neutral, mixed）をJSON形式で出力してください。

        テキスト：{text}

        JSON出力：
        """

        self.keywords_prompt = """
        以下のテキストの主要なキーワードを5つ以内でリストアップしてください。

        テキスト：{text}

        キーワード：
        """

        self.topics_prompt = """
        以下のテキストが主に扱っているトピックを短いフレーズで2つ以内で示してください。

        テキスト：{text}

        トピック：
        """

        self.named_entities_prompt = """
        以下のテキストに含まれる人名、地名、組織名、日付、出来事などの固有表現を抽出し、その種類と共にJSON形式のリストで出力してください。

        テキスト：{text}

        JSON出力：
        """

        self.summarization_prompt = """
        以下の長いテキストを3つの主要なポイントに要約してください。

        テキスト：{text}

        要約：
        """

        self.sensitivity_prompt = """
        以下のテキストの内容は、プライバシーの観点からどの程度の機微性（低、中、高、非常に高い、極めて高い）を持つと考えられますか？

        テキスト：{text}

        機微度：
        """

    async def process_conversation_message(self, user_id: int, role: str, content: str) -> bool:
        """会話メッセージを処理し、エピソードとして保存する"""
        try:
            # 短い相槌や空のメッセージは処理しない
            if not self._should_process_as_episode(content):
                return True

            # 現在のエピソードを取得または新規作成
            current_episode = self._get_or_create_episode(user_id, role, content)

            # メッセージを現在のエピソードに追加
            current_episode['messages'].append({
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            })

            # エピソードの情報を分析
            await self._analyze_episode_info(current_episode)

            # エピソードが完了したかどうかをチェック
            if self._is_episode_complete(current_episode):
                # エピソードを保存
                await self._save_episode(current_episode)
                # アクティブなエピソードから削除
                del self.active_episodes[user_id]

            return True

        except Exception as e:
            logger.error(f"Error processing conversation message: {e}")
            return False

    def _get_or_create_episode(self, user_id: int, role: str, content: str) -> Dict:
        """現在のエピソードを取得または新規作成する"""
        if user_id not in self.active_episodes:
            # 新しいエピソードを作成
            self.active_episodes[user_id] = {
                'user_id': user_id,
                'messages': [],
                'collected_info': set(),
                'start_time': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat()
            }
        return self.active_episodes[user_id]

    async def _analyze_episode_info(self, episode: Dict) -> None:
        """エピソードの情報を分析し、必要な情報を抽出する"""
        # 最新のメッセージを取得
        latest_message = episode['messages'][-1]['content']

        # 情報の抽出を試みる
        info_tasks = [
            self._extract_when(latest_message),
            self._extract_where(latest_message),
            self._extract_who(latest_message),
            self._extract_what(latest_message),
            self._extract_how(latest_message)
        ]

        # 並行して情報を抽出
        results = await asyncio.gather(*info_tasks, return_exceptions=True)

        # 成功した抽出結果を記録
        for info_type, result in zip(['when', 'where', 'who', 'what', 'how'], results):
            if not isinstance(result, Exception) and result:
                episode['collected_info'].add(info_type)
                if info_type not in episode:
                    episode[info_type] = []
                episode[info_type].append(result)

    async def _extract_when(self, text: str) -> Optional[str]:
        """テキストから時間情報を抽出する"""
        prompt = f"""
        以下のテキストから、出来事が発生した時間や時期に関する情報を抽出してください。
        具体的な日付、曜日、時間、季節、相対的な時間表現（昨日、先週など）を探してください。

        テキスト：{text}

        時間情報：
        """
        try:
            response = await self.llm_analyzer._call_llm_api(prompt)
            return response.strip() if response.strip() else None
        except Exception as e:
            logger.error(f"Error extracting when: {e}")
            return None

    async def _extract_where(self, text: str) -> Optional[str]:
        """テキストから場所情報を抽出する"""
        prompt = f"""
        以下のテキストから、出来事が発生した場所に関する情報を抽出してください。
        具体的な地名、施設名、相対的な位置表現（近所、家の近くなど）を探してください。

        テキスト：{text}

        場所情報：
        """
        try:
            response = await self.llm_analyzer._call_llm_api(prompt)
            return response.strip() if response.strip() else None
        except Exception as e:
            logger.error(f"Error extracting where: {e}")
            return None

    async def _extract_who(self, text: str) -> Optional[str]:
        """テキストから人物情報を抽出する"""
        prompt = f"""
        以下のテキストから、出来事に関わった人物に関する情報を抽出してください。
        具体的な人名、役割、関係性（友達、家族など）を探してください。

        テキスト：{text}

        人物情報：
        """
        try:
            response = await self.llm_analyzer._call_llm_api(prompt)
            return response.strip() if response.strip() else None
        except Exception as e:
            logger.error(f"Error extracting who: {e}")
            return None

    async def _extract_what(self, text: str) -> Optional[str]:
        """テキストから出来事の内容を抽出する"""
        prompt = f"""
        以下のテキストから、何が起きたのかという出来事の内容を抽出してください。
        具体的な行動、イベント、状態変化などを探してください。

        テキスト：{text}

        出来事の内容：
        """
        try:
            response = await self.llm_analyzer._call_llm_api(prompt)
            return response.strip() if response.strip() else None
        except Exception as e:
            logger.error(f"Error extracting what: {e}")
            return None

    async def _extract_how(self, text: str) -> Optional[str]:
        """テキストから出来事の方法や状況を抽出する"""
        prompt = f"""
        以下のテキストから、出来事がどのように起きたのかという方法や状況を抽出してください。
        具体的な手段、方法、状況、感情などを探してください。

        テキスト：{text}

        方法や状況：
        """
        try:
            response = await self.llm_analyzer._call_llm_api(prompt)
            return response.strip() if response.strip() else None
        except Exception as e:
            logger.error(f"Error extracting how: {e}")
            return None

    def _is_episode_complete(self, episode: Dict) -> bool:
        """エピソードが完了したかどうかを判定する"""
        # 必要な情報がすべて揃っているかチェック
        has_required_info = len(episode['collected_info']) == len(self.required_info)
        
        # 最後の更新から一定時間が経過しているかチェック
        last_update = datetime.fromisoformat(episode['last_update'])
        time_elapsed = (datetime.now() - last_update).total_seconds() > 300  # 5分

        # 会話が終了したと判断できるかチェック
        is_conversation_ended = self._is_conversation_ended(episode['messages'])

        return has_required_info or (time_elapsed and is_conversation_ended)

    def _is_conversation_ended(self, messages: List[Dict]) -> bool:
        """会話が終了したかどうかを判定する"""
        if len(messages) < 2:
            return False

        # 最後の2つのメッセージを取得
        last_message = messages[-1]['content'].lower()
        second_last_message = messages[-2]['content'].lower()

        # 会話終了を示す表現をチェック
        end_indicators = {
            'ありがとう', '了解', '了解です', '承知しました',
            'わかりました', '了解しました', 'お疲れ様です',
            'お疲れ様でした', '失礼します', '失礼しました'
        }

        return any(indicator in last_message for indicator in end_indicators)

    async def _save_episode(self, episode: Dict) -> bool:
        """エピソードをデータベースに保存する"""
        try:
            # エピソードの基本情報を作成
            episode_data = {
                'user_id': episode['user_id'],
                'text_content': self._combine_messages(episode['messages']),
                'author': 'user',  # 主にユーザーの発言からなるエピソード
                'timestamp': episode['start_time'],
                'collected_info_json': json.dumps({
                    'when': episode.get('when', []),
                    'where': episode.get('where', []),
                    'who': episode.get('who', []),
                    'what': episode.get('what', []),
                    'how': episode.get('how', [])
                }),
                'completeness': len(episode['collected_info']) / len(self.required_info)
            }

            # エピソードを保存
            success = await db_manager.add_episode(**episode_data)
            if not success:
                logger.error(f"Failed to save episode for user {episode['user_id']}")
                return False

            # 追加の分析を実行
            await self._perform_additional_analysis(episode_data)
            return True

        except Exception as e:
            logger.error(f"Error saving episode: {e}")
            return False

    def _combine_messages(self, messages: List[Dict]) -> str:
        """メッセージを結合して1つのテキストにする"""
        return "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])

    async def _perform_additional_analysis(self, episode_data: Dict) -> None:
        """エピソードに対して追加の分析を実行する"""
        try:
            # 非同期で追加の分析を実行
            analysis_tasks = [
                self.llm_analyzer.analyze_content_type(episode_data['text_content']),
                self.llm_analyzer.analyze_emotions(episode_data['text_content']),
                self.llm_analyzer.extract_keywords(episode_data['text_content']),
                self.llm_analyzer.identify_topics(episode_data['text_content']),
                self.llm_analyzer.extract_named_entities(episode_data['text_content']),
                self.llm_analyzer.assess_sensitivity(episode_data['text_content'])
            ]

            # すべての分析を並行実行
            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

            # 分析結果を整形
            analysis_data = {
                'content_type': results[0] if not isinstance(results[0], Exception) else 'その他',
                'emotion_analysis_json': json.dumps(results[1]) if not isinstance(results[1], Exception) else '{}',
                'keywords_json': json.dumps(results[2]) if not isinstance(results[2], Exception) else '[]',
                'topics_json': json.dumps(results[3]) if not isinstance(results[3], Exception) else '[]',
                'named_entities_json': json.dumps(results[4]) if not isinstance(results[4], Exception) else '[]',
                'sensitivity_level': results[5] if not isinstance(results[5], Exception) else '低'
            }

            # 分析結果を更新
            await db_manager.update_episode(episode_data['episode_id'], **analysis_data)

        except Exception as e:
            logger.error(f"Error performing additional analysis: {e}")

    def _is_short_acknowledgement(self, text: str) -> bool:
        """短い相槌や確認のメッセージかどうかを判定する"""
        short_acknowledgements = {
            'はい', 'うん', 'へえ', 'なるほど', '了解', '了解です',
            'ok', 'okです', '了解しました', '承知しました'
        }
        return text.strip().lower() in short_acknowledgements

    def _should_process_as_episode(self, text: str) -> bool:
        """テキストをエピソードとして処理すべきかどうかを判定する"""
        # 短い相槌は処理しない
        if self._is_short_acknowledgement(text):
            return False
        
        # 空のメッセージは処理しない
        if not text.strip():
            return False
        
        return True

    async def get_user_episodes(self, user_id: int, limit: Optional[int] = None) -> List[Dict]:
        """ユーザーのエピソードを取得する"""
        try:
            episodes = await db_manager.get_episodes(user_id, limit)
            return episodes
        except Exception as e:
            logger.error(f"Error getting user episodes: {e}")
            return []

    async def update_episode_metadata(self, episode_id: int, metadata: Dict) -> bool:
        """エピソードのメタデータを更新する"""
        try:
            success = await db_manager.update_episode(episode_id, **metadata)
            return success
        except Exception as e:
            logger.error(f"Error updating episode metadata: {e}")
            return False 