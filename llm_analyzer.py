import json
import logging
from typing import Dict, List, Optional, Union
import aiohttp
import asyncio

logger = logging.getLogger('discord')

class LLMAnalyzer:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    async def analyze_content_type(self, text: str) -> str:
        """テキストの内容種別を分析する"""
        prompt = f"""
        以下のテキストは、どのような種類の情報を含んでいますか？
        選択肢：事実の記述、意見の表明、感情の吐露、過去の出来事の回想、価値観の表明、目標設定、質問、その他
        最も適切なものを一つ選んでください。

        テキスト：{text}

        種類：
        """
        try:
            response = await self._call_llm_api(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Error analyzing content type: {e}")
            return "その他"

    async def analyze_emotions(self, text: str) -> Dict:
        """テキストの感情を分析する"""
        prompt = f"""
        以下のテキストから読み取れる主要な感情、その強度（0.0-1.0）、全体的な感情の極性（positive, negative, neutral, mixed）をJSON形式で出力してください。

        テキスト：{text}

        JSON出力：
        """
        try:
            response = await self._call_llm_api(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error analyzing emotions: {e}")
            return {
                'emotions': {},
                'polarity': 'neutral'
            }

    async def extract_keywords(self, text: str) -> List[str]:
        """テキストからキーワードを抽出する"""
        prompt = f"""
        以下のテキストの主要なキーワードを5つ以内でリストアップしてください。

        テキスト：{text}

        キーワード：
        """
        try:
            response = await self._call_llm_api(prompt)
            # カンマ区切りのリストを想定
            keywords = [k.strip() for k in response.split(',')]
            return keywords[:5]  # 最大5つまで
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []

    async def identify_topics(self, text: str) -> List[str]:
        """テキストのトピックを特定する"""
        prompt = f"""
        以下のテキストが主に扱っているトピックを短いフレーズで2つ以内で示してください。

        テキスト：{text}

        トピック：
        """
        try:
            response = await self._call_llm_api(prompt)
            # カンマ区切りのリストを想定
            topics = [t.strip() for t in response.split(',')]
            return topics[:2]  # 最大2つまで
        except Exception as e:
            logger.error(f"Error identifying topics: {e}")
            return []

    async def extract_named_entities(self, text: str) -> List[Dict]:
        """テキストから固有表現を抽出する"""
        prompt = f"""
        以下のテキストに含まれる人名、地名、組織名、日付、出来事などの固有表現を抽出し、その種類と共にJSON形式のリストで出力してください。

        テキスト：{text}

        JSON出力：
        """
        try:
            response = await self._call_llm_api(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error extracting named entities: {e}")
            return []

    async def summarize_text(self, text: str) -> List[str]:
        """テキストを要約する"""
        prompt = f"""
        以下の長いテキストを3つの主要なポイントに要約してください。

        テキスト：{text}

        要約：
        """
        try:
            response = await self._call_llm_api(prompt)
            # 箇条書きのリストを想定
            points = [p.strip() for p in response.split('\n') if p.strip()]
            return points[:3]  # 最大3つまで
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return []

    async def assess_sensitivity(self, text: str) -> str:
        """テキストの機微度を評価する"""
        prompt = f"""
        以下のテキストの内容は、プライバシーの観点からどの程度の機微性（低、中、高、非常に高い、極めて高い）を持つと考えられますか？

        テキスト：{text}

        機微度：
        """
        try:
            response = await self._call_llm_api(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Error assessing sensitivity: {e}")
            return "低"

    async def _call_llm_api(self, prompt: str) -> str:
        """LLM APIを呼び出す"""
        async with aiohttp.ClientSession() as session:
            try:
                payload = {
                    'prompt': prompt,
                    'max_tokens': 150,
                    'temperature': 0.7
                }
                
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['text'].strip()
                    else:
                        error_text = await response.text()
                        raise Exception(f"API call failed with status {response.status}: {error_text}")
            except Exception as e:
                logger.error(f"Error calling LLM API: {e}")
                raise 