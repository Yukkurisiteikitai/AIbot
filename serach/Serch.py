import aiosqlite
import asyncio
import json

class WeightEvaluator:
    def __init__(self):
        self.weight_types = {
            'semantic': self.evaluate_semantic_weight,
            'temporal': self.evaluate_temporal_weight,
            'contextual': self.evaluate_contextual_weight,
            'user_defined': self.evaluate_user_defined_weight
        }

    async def evaluate_relation_weight(
        self,
        message_id: str,
        related_message_id: str,
        weight_type: str,
        context: dict = None
    ) -> dict:
        """関連性の重みを評価"""
        if weight_type not in self.weight_types:
            raise ValueError(f"Unsupported weight type: {weight_type}")
        
        # 重みを計算
        weight_result = await self.weight_types[weight_type](
            message_id,
            related_message_id,
            context
        )
        
        # 重みを保存
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute('''
                INSERT INTO relation_weights (
                    message_id,
                    related_message_id,
                    weight_score,
                    weight_type,
                    confidence_score,
                    metadata
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                message_id,
                related_message_id,
                weight_result['weight'],
                weight_type,
                weight_result['confidence'],
                json.dumps(weight_result['metadata'])
            ))
            await db.commit()
        
        return weight_result

    async def evaluate_semantic_weight(
        self,
        message_id: str,
        related_message_id: str,
        context: dict = None
    ) -> dict:
        """意味的な関連性の重みを評価"""
        async with aiosqlite.connect(DATABASE) as db:
            # メッセージの内容を取得
            async with db.execute('''
                SELECT content FROM messages
                WHERE message_id IN (?, ?)
            ''', (message_id, related_message_id)) as cursor:
                messages = await cursor.fetchall()
            
            # ここで意味的な類似度を計算
            # 例: コサイン類似度、BERT埋め込みの類似度など
            semantic_similarity = await self.calculate_semantic_similarity(
                messages[0][0],
                messages[1][0]
            )
            
            return {
                'weight': semantic_similarity,
                'confidence': 0.8,  # 信頼度スコア
                'metadata': {
                    'similarity_type': 'semantic',
                    'calculation_method': 'cosine_similarity'
                }
            }

    async def evaluate_temporal_weight(
        self,
        message_id: str,
        related_message_id: str,
        context: dict = None
    ) -> dict:
        """時間的な関連性の重みを評価"""
        async with aiosqlite.connect(DATABASE) as db:
            # メッセージの時間情報を取得
            async with db.execute('''
                SELECT created_at FROM messages
                WHERE message_id IN (?, ?)
            ''', (message_id, related_message_id)) as cursor:
                timestamps = await cursor.fetchall()
            
            # 時間差を計算
            time_diff = abs(
                datetime.fromisoformat(timestamps[1][0]) -
                datetime.fromisoformat(timestamps[0][0])
            )
            
            # 時間差に基づいて重みを計算
            # 例: 時間差が小さいほど重みが大きい
            weight = 1.0 / (1.0 + time_diff.total_seconds() / 3600)  # 1時間単位
            
            return {
                'weight': weight,
                'confidence': 0.9,
                'metadata': {
                    'time_diff_seconds': time_diff.total_seconds(),
                    'calculation_method': 'inverse_time_diff'
                }
            }

    async def evaluate_contextual_weight(
        self,
        message_id: str,
        related_message_id: str,
        context: dict = None
    ) -> dict:
        """文脈的な関連性の重みを評価"""
        # 会話の文脈を取得
        context = await get_conversation_context(message_id)
        
        # 文脈に基づいて重みを計算
        # 例: 同じトピック、同じ感情、同じ参照など
        contextual_weight = await self.analyze_contextual_similarity(
            context,
            message_id,
            related_message_id
        )
        
        return {
            'weight': contextual_weight,
            'confidence': 0.7,
            'metadata': {
                'context_analysis': context,
                'calculation_method': 'contextual_analysis'
            }
        }
    async def save_weight_evaluation(
    message_id: str,
    related_message_id: str,
    evaluation: dict
) -> bool:
    """重みの評価結果を保存"""
    async with aiosqlite.connect(DATABASE) as db:
        try:
            await db.execute('''
                INSERT INTO relation_weights (
                    message_id,
                    related_message_id,
                    weight_score,
                    weight_category,
                    weight_interpretation,
                    confidence_score,
                    metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_id,
                related_message_id,
                evaluation['weight'],
                evaluation['category']['name'],
                evaluation['category']['interpretation'],
                evaluation['confidence'],
                json.dumps(evaluation['metadata'])
            ))
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving weight evaluation: {e}")
            return False


# AI重み評価器のインスタンス化
evaluator = AIWeightEvaluator(llm_client)

# 重みを評価
evaluation = await evaluator.evaluate_weight_with_ai(
    message_id="msg_123",
    related_message_id="msg_456",
    context={
        'thread_context': '...',
        'user_profile': '...',
        'conversation_history': '...'
    }
)

# 評価結果を保存
await save_weight_evaluation(
    message_id="msg_123",
    related_message_id="msg_456",
    evaluation=evaluation
)

# 評価結果の例
{
    'weight': 0.75,
    'category': {
        'name': 'important',
        'label': '大事',
        'interpretation': '感情的な影響や価値がある',
        'description': '強い関連性があり、感情や価値観に影響を与える'
    },
    'explanation': 'このメッセージは、ユーザーの重要な価値観に関連しており、感情的な影響が強い',
    'confidence': 0.85,
    'metadata': {
        'ai_analysis': '...',
        'context_used': {...}
    }
}