"""ChatGPT-powered beauty consultation chatbot service."""

import asyncio
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from openai import AsyncOpenAI
from loguru import logger
from supabase import Client

from app.config import settings
from app.models.analysis import FaceAnalysisResult
from app.models.chat import ChatMessage, ChatRequest, ChatResponse, ChatSession
from app.utils.exceptions import ChatbotError, DatabaseError


class BeautyChatbotService:
    """AI-powered beauty consultation chatbot using GPT-4o-mini."""

    def __init__(self, supabase_client: Client) -> None:
        """Initialize chatbot service."""
        self.supabase = supabase_client
        self.openai = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model or "gpt-4o-mini"  # Default to gpt-4o-mini
        
        # System prompt for beauty consultation
        self.system_prompt = """
あなたは韓国の美容業界で豊富な経験を持つ、親しみやすい美容カウンセラーです。
顔面分析の結果に基づいて、個別化された美容アドバイスを提供してください。

【あなたの特徴】
- 韓国の最新美容トレンドに詳しい
- K-POPアイドルの美容法に精通
- 親しみやすく、励ましの言葉をかける
- 具体的で実践的なアドバイスを提供
- 医学的なアドバイスは避け、美容・メイクの範囲で回答

【回答スタイル】
- 絵文字を適度に使用して親しみやすく
- 韓国語の美容用語も交えて説明
- ポジティブで励ましの気持ちを込める
- 具体的な商品やテクニックを提案
- 質問者の気持ちに共感する

【注意事項】
- 医学的診断や治療の推奨は禁止
- 整形手術の具体的な推奨は避ける
- 個人の美しさを尊重する姿勢を保つ
- 危険な美容法は推奨しない
"""

    async def create_chat_session(
        self,
        user_id: UUID,
        title: str | None = None,
        context_type: str = "general",
        analysis_id: UUID | None = None,
        initial_message: str | None = None,
    ) -> ChatSession:
        """Create new chat session."""
        try:
            session_id = uuid4()
            
            # Auto-generate title if not provided
            if not title:
                if analysis_id:
                    title = "分析結果について相談"
                else:
                    title = "美容相談"

            # Prepare session data
            session_data = {
                "id": str(session_id),
                "user_id": str(user_id),
                "title": title,
                "context_type": context_type,
                "analysis_id": str(analysis_id) if analysis_id else None,
                "is_active": True,
                "message_count": 0,
                "metadata": {},
                "conversation_context": await self._build_conversation_context(
                    user_id, analysis_id
                ),
            }

            # Insert session
            response = (
                self.supabase.table("chat_sessions")
                .insert(session_data)
                .execute()
            )

            session = ChatSession(**response.data[0])

            # Send initial message if provided
            if initial_message:
                await self.send_message(
                    session_id=session_id,
                    user_id=user_id,
                    message=initial_message,
                )

            logger.info(f"💬 Created chat session {session_id}")
            return session

        except Exception as e:
            logger.error(f"Failed to create chat session: {str(e)}")
            raise ChatbotError(
                f"Failed to create chat session: {str(e)}",
                provider="supabase",
            ) from e

    async def send_message(
        self,
        session_id: UUID,
        user_id: UUID,
        message: str,
        analysis_id: UUID | None = None,
    ) -> ChatResponse:
        """Send message and get AI response."""
        try:
            logger.info(f"💬 Processing message in session {session_id}")

            # Get session and validate ownership
            session = await self._get_session(session_id, user_id)

            # Build conversation history
            conversation_history = await self._get_conversation_history(session_id)

            # Get analysis context if available
            analysis_context = await self._get_analysis_context(
                analysis_id or session.analysis_id
            )

            # Store user message
            user_message_id = await self._store_message(
                session_id=session_id,
                role="user",
                content=message,
                analysis_reference=analysis_id,
            )

            # Generate AI response
            ai_response = await self._generate_ai_response(
                user_message=message,
                conversation_history=conversation_history,
                analysis_context=analysis_context,
                session_context=session.conversation_context,
            )

            # Store AI response
            ai_message_id = await self._store_message(
                session_id=session_id,
                role="assistant",
                content=ai_response["content"],
                metadata={
                    "model_used": ai_response["model"],
                    "tokens_used": ai_response["tokens"],
                    "response_time_ms": ai_response["response_time"],
                },
            )

            # Generate follow-up suggestions
            suggestions = await self._generate_suggestions(
                ai_response["content"], analysis_context
            )

            # Extract beauty tips from response
            beauty_tips = self._extract_beauty_tips(ai_response["content"])

            # Create response
            response = ChatResponse(
                message=ai_response["content"],
                session_id=session_id,
                message_id=ai_message_id,
                suggestions=suggestions,
                analysis_insights=analysis_context or {},
                beauty_tips=beauty_tips,
                created_at=datetime.now(),
            )

            logger.info(f"✅ Generated AI response for session {session_id}")
            return response

        except Exception as e:
            logger.error(f"Failed to process message: {str(e)}")
            raise ChatbotError(
                f"Failed to process message: {str(e)}",
                provider="openai",
            ) from e

    async def get_chat_sessions(
        self, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> list[ChatSession]:
        """Get user's chat sessions."""
        try:
            response = (
                self.supabase.table("chat_sessions")
                .select("*")
                .eq("user_id", str(user_id))
                .order("updated_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            sessions = [ChatSession(**data) for data in response.data]
            return sessions

        except Exception as e:
            logger.error(f"Failed to get chat sessions: {str(e)}")
            raise DatabaseError(
                f"Failed to retrieve chat sessions: {str(e)}",
                operation="get_chat_sessions",
            ) from e

    async def get_session_messages(
        self, session_id: UUID, user_id: UUID, limit: int = 50
    ) -> list[ChatMessage]:
        """Get messages from a chat session."""
        try:
            # Verify session ownership
            await self._get_session(session_id, user_id)

            response = (
                self.supabase.table("chat_messages")
                .select("*")
                .eq("session_id", str(session_id))
                .order("created_at", desc=False)
                .limit(limit)
                .execute()
            )

            messages = [ChatMessage(**data) for data in response.data]
            return messages

        except Exception as e:
            logger.error(f"Failed to get session messages: {str(e)}")
            raise DatabaseError(
                f"Failed to retrieve session messages: {str(e)}",
                operation="get_session_messages",
            ) from e

    async def _generate_ai_response(
        self,
        user_message: str,
        conversation_history: list[dict[str, str]],
        analysis_context: dict[str, Any] | None,
        session_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate AI response using OpenAI GPT-4o-mini."""
        try:
            start_time = datetime.now()

            # Build messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]

            # Add analysis context if available
            if analysis_context:
                context_message = self._format_analysis_context(analysis_context)
                messages.append({"role": "system", "content": context_message})

            # Add conversation history
            messages.extend(conversation_history[-10:])  # Last 10 messages for context

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Call OpenAI API
            response = await self.openai.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=settings.openai_max_tokens,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            # Extract response data
            content = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0
            response_time = int((datetime.now() - start_time).total_seconds() * 1000)

            return {
                "content": content,
                "model": self.model,
                "tokens": tokens_used,
                "response_time": response_time,
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise ChatbotError(
                f"AI response generation failed: {str(e)}",
                provider="openai",
            ) from e

    async def _get_session(self, session_id: UUID, user_id: UUID) -> ChatSession:
        """Get session and verify ownership."""
        try:
            response = (
                self.supabase.table("chat_sessions")
                .select("*")
                .eq("id", str(session_id))
                .eq("user_id", str(user_id))
                .single()
                .execute()
            )

            if not response.data:
                raise ChatbotError("Chat session not found or access denied")

            return ChatSession(**response.data)

        except Exception as e:
            raise ChatbotError(f"Failed to get session: {str(e)}") from e

    async def _get_conversation_history(
        self, session_id: UUID
    ) -> list[dict[str, str]]:
        """Get recent conversation history."""
        try:
            response = (
                self.supabase.table("chat_messages")
                .select("role, content")
                .eq("session_id", str(session_id))
                .order("created_at", desc=False)
                .limit(20)
                .execute()
            )

            return [
                {"role": msg["role"], "content": msg["content"]}
                for msg in response.data
            ]

        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            return []

    async def _get_analysis_context(
        self, analysis_id: UUID | None
    ) -> dict[str, Any] | None:
        """Get analysis result for context."""
        if not analysis_id:
            return None

        try:
            response = (
                self.supabase.table("analysis_results")
                .select("overall_score, facial_harmony, eline_analysis, symmetry_analysis")
                .eq("id", str(analysis_id))
                .single()
                .execute()
            )

            return response.data

        except Exception as e:
            logger.error(f"Failed to get analysis context: {str(e)}")
            return None

    async def _store_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        analysis_reference: UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UUID:
        """Store message in database."""
        try:
            message_id = uuid4()
            message_data = {
                "id": str(message_id),
                "session_id": str(session_id),
                "role": role,
                "content": content,
                "metadata": metadata or {},
                "analysis_reference": str(analysis_reference) if analysis_reference else None,
            }

            if role == "assistant" and metadata:
                message_data.update({
                    "model_used": metadata.get("model_used"),
                    "tokens_used": metadata.get("tokens_used"),
                    "response_time_ms": metadata.get("response_time_ms"),
                })

            self.supabase.table("chat_messages").insert(message_data).execute()
            return message_id

        except Exception as e:
            logger.error(f"Failed to store message: {str(e)}")
            raise DatabaseError(f"Failed to store message: {str(e)}") from e

    async def _build_conversation_context(
        self, user_id: UUID, analysis_id: UUID | None
    ) -> dict[str, Any]:
        """Build conversation context for better responses."""
        context = {
            "user_goals": ["美しくなりたい", "自信を持ちたい"],
            "consultation_type": "beauty_advice",
            "language_preference": "japanese",
            "style_preference": "korean_beauty",
        }

        # Add analysis summary if available
        if analysis_id:
            analysis_context = await self._get_analysis_context(analysis_id)
            if analysis_context:
                context["analysis_summary"] = analysis_context

        return context

    def _format_analysis_context(self, analysis_context: dict[str, Any]) -> str:
        """Format analysis context for AI prompt."""
        context_text = "【分析結果情報】\n"
        
        if "overall_score" in analysis_context:
            score_data = analysis_context["overall_score"]
            context_text += f"総合スコア: {score_data.get('score', 'N/A')}/100\n"
            context_text += f"美容レベル: {score_data.get('level', 'N/A')}\n"
            context_text += f"説明: {score_data.get('description', 'N/A')}\n"

        if "facial_harmony" in analysis_context:
            harmony_data = analysis_context["facial_harmony"]
            context_text += f"パーツ調和性: {harmony_data.get('harmony_score', 'N/A')}/100\n"
            context_text += f"美しさレベル: {harmony_data.get('beauty_level', 'N/A')}\n"

        context_text += "\nこの分析結果を踏まえて、具体的で励ましのあるアドバイスをしてください。"
        return context_text

    async def _generate_suggestions(
        self, ai_response: str, analysis_context: dict[str, Any] | None
    ) -> list[str]:
        """Generate follow-up question suggestions."""
        base_suggestions = [
            "メイクのコツを教えて",
            "おすすめの美容製品は？",
            "スキンケアについて相談したい",
            "韓国コスメのおすすめは？",
        ]

        # Add analysis-specific suggestions
        if analysis_context and "overall_score" in analysis_context:
            score = analysis_context["overall_score"].get("score", 0)
            if score >= 80:
                base_suggestions.extend([
                    "この美しさを維持する方法は？",
                    "さらに魅力的になるには？",
                ])
            else:
                base_suggestions.extend([
                    "改善できるポイントは？",
                    "効果的な美容法を教えて",
                ])

        return base_suggestions[:4]  # Return top 4 suggestions

    def _extract_beauty_tips(self, ai_response: str) -> list[str]:
        """Extract actionable beauty tips from AI response."""
        tips = []
        
        # Simple extraction based on common patterns
        sentences = ai_response.split('。')
        for sentence in sentences:
            if any(keyword in sentence for keyword in ['おすすめ', 'コツ', '方法', 'ポイント', 'テクニック']):
                clean_sentence = sentence.strip() + '。' if sentence.strip() else ''
                if len(clean_sentence) > 10:  # Minimum length
                    tips.append(clean_sentence)
        
        return tips[:3]  # Return top 3 tips


# Global service instance
_chatbot_service_instance: BeautyChatbotService | None = None


def get_chatbot_service(supabase_client: Client) -> BeautyChatbotService:
    """Get or create chatbot service instance."""
    global _chatbot_service_instance
    if _chatbot_service_instance is None:
        _chatbot_service_instance = BeautyChatbotService(supabase_client)
    return _chatbot_service_instance