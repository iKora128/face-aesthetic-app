"""LINE Bot service for facial beauty analysis."""

import asyncio
import hashlib
import hmac
import json
import base64
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import httpx
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage,
    ImageMessage,
    TemplateMessage,
    ButtonsTemplate,
    CarouselTemplate,
    CarouselColumn,
    MessageAction,
    URIAction,
    QuickReply,
    QuickReplyButton,
    FlexMessage
)
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    FollowEvent,
    UnfollowEvent
)
from loguru import logger
from supabase import Client

from app.config import settings
from app.models.linebot import (
    LineBotUser, LineBotUserCreate, LineBotAnalysisRequest, LineBotResponse
)
from app.services.analysis_service import get_analysis_service
from app.services.chatbot_service import get_chatbot_service
from app.utils.exceptions import LineBotError, AnalysisError


class LineBotService:
    """LINE Bot service for beauty analysis integration."""

    def __init__(self, supabase_client: Client) -> None:
        """Initialize LINE Bot service with v3 API."""
        self.supabase = supabase_client
        
        # Initialize LINE Bot v3 API
        configuration = Configuration(access_token=settings.line_channel_access_token)
        self.async_api_client = AsyncApiClient(configuration)
        self.line_bot_api = AsyncMessagingApi(self.async_api_client)
        self.parser = WebhookParser(settings.line_channel_secret)
        
        # Analysis and chat services
        self.analysis_service = get_analysis_service(supabase_client)
        self.chatbot_service = get_chatbot_service(supabase_client)

    async def _handle_events(self, events: list) -> None:
        """Handle LINE Bot events with v3 API."""
        for event in events:
            try:
                if isinstance(event, MessageEvent):
                    if isinstance(event.message, TextMessageContent):
                        await self._handle_text_message_async(event)
                    elif isinstance(event.message, ImageMessageContent):
                        await self._handle_image_message_async(event)
                elif isinstance(event, FollowEvent):
                    await self._handle_follow_async(event)
                elif isinstance(event, UnfollowEvent):
                    await self._handle_unfollow_async(event)
            except Exception as e:
                logger.error(f"Error handling event {event.type}: {str(e)}")

    async def verify_signature(self, body: bytes, signature: str) -> bool:
        """Verify LINE webhook signature."""
        try:
            hash_value = hmac.new(
                settings.line_channel_secret.encode('utf-8'),
                body,
                hashlib.sha256
            ).digest()
            expected_signature = base64.b64encode(hash_value).decode('utf-8')
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False

    async def handle_webhook(self, body: str, signature: str) -> dict[str, Any]:
        """Handle LINE webhook events with v3 API."""
        try:
            # Parse events using v3 parser
            events = self.parser.parse(body, signature)
            
            # Handle events
            await self._handle_events(events)
            
            return {"status": "success", "message": "Events processed"}
            
        except InvalidSignatureError:
            logger.error("Invalid LINE webhook signature")
            raise LineBotError("Invalid signature", provider="line")
        except Exception as e:
            logger.error(f"Webhook handling failed: {str(e)}")
            raise LineBotError(f"Webhook handling failed: {str(e)}", provider="line")

    async def _handle_text_message_async(self, event: MessageEvent) -> None:
        """Handle text message events."""
        try:
            user_id = event.source.user_id
            message_text = event.message.text.strip()
            
            logger.info(f"📱 Received text from {user_id}: {message_text}")
            
            # Get or create user
            bot_user = await self._get_or_create_user(user_id)
            
            # Handle different text commands
            if message_text.lower() in ['help', 'ヘルプ', '使い方']:
                await self._send_help_message(user_id)
            elif message_text.lower() in ['start', 'スタート', '開始']:
                await self._send_welcome_message(user_id)
            elif message_text.lower() in ['analysis', '分析', '美容分析']:
                await self._send_analysis_instruction(user_id)
            elif message_text.lower() in ['chat', 'チャット', '相談']:
                await self._handle_chat_request(user_id, message_text)
            else:
                # Default: treat as chat message
                await self._handle_chat_message(user_id, message_text)
                
        except Exception as e:
            logger.error(f"Failed to handle text message: {str(e)}")
            await self._send_error_message(event.source.user_id)

    async def _handle_image_message_async(self, event: MessageEvent) -> None:
        """Handle image message events."""
        try:
            user_id = event.source.user_id
            message_id = event.message.id
            
            logger.info(f"📷 Received image from {user_id}: {message_id}")
            
            # Get or create user
            bot_user = await self._get_or_create_user(user_id)
            
            # Send processing message
            await self._send_processing_message(user_id)
            
            # Download and analyze image
            image_data = await self._download_image(message_id)
            analysis_result = await self._analyze_image(user_id, image_data, message_id)
            
            # Send analysis results
            await self._send_analysis_results(user_id, analysis_result)
            
        except Exception as e:
            logger.error(f"Failed to handle image message: {str(e)}")
            await self._send_error_message(event.source.user_id)

    async def _handle_follow_async(self, event: FollowEvent) -> None:
        """Handle follow events."""
        try:
            user_id = event.source.user_id
            logger.info(f"👥 New follower: {user_id}")
            
            # Create user
            await self._get_or_create_user(user_id)
            
            # Send welcome message
            await self._send_welcome_message(user_id)
            
        except Exception as e:
            logger.error(f"Failed to handle follow event: {str(e)}")

    async def _handle_unfollow_async(self, event: UnfollowEvent) -> None:
        """Handle unfollow events."""
        try:
            user_id = event.source.user_id
            logger.info(f"👋 User unfollowed: {user_id}")
            
            # Deactivate user
            await self._deactivate_user(user_id)
            
        except Exception as e:
            logger.error(f"Failed to handle unfollow event: {str(e)}")

    async def _get_or_create_user(self, line_user_id: str) -> LineBotUser:
        """Get or create LINE Bot user."""
        try:
            # Try to get existing user
            response = (
                self.supabase.table("line_bot_users")
                .select("*")
                .eq("line_user_id", line_user_id)
                .single()
                .execute()
            )
            
            if response.data:
                return LineBotUser(**response.data)
            
            # Create new user
            profile = await self._get_user_profile(line_user_id)
            
            user_data = LineBotUserCreate(
                line_user_id=line_user_id,
                display_name=profile.get("displayName"),
                picture_url=profile.get("pictureUrl"),
                status_message=profile.get("statusMessage"),
            )
            
            response = (
                self.supabase.table("line_bot_users")
                .insert({
                    "id": str(uuid4()),
                    "line_user_id": user_data.line_user_id,
                    "display_name": user_data.display_name,
                    "picture_url": user_data.picture_url,
                    "status_message": user_data.status_message,
                    "language": user_data.language,
                })
                .execute()
            )
            
            return LineBotUser(**response.data[0])
            
        except Exception as e:
            logger.error(f"Failed to get/create user: {str(e)}")
            raise LineBotError(f"User management failed: {str(e)}", provider="line")

    async def _get_user_profile(self, line_user_id: str) -> dict[str, Any]:
        """Get LINE user profile."""
        try:
            profile = self.line_bot_api.get_profile(line_user_id)
            return {
                "displayName": profile.display_name,
                "pictureUrl": profile.picture_url,
                "statusMessage": profile.status_message,
            }
        except LineBotApiError as e:
            logger.warning(f"Failed to get user profile: {str(e)}")
            return {}

    async def _download_image(self, message_id: str) -> bytes:
        """Download image from LINE."""
        try:
            message_content = self.line_bot_api.get_message_content(message_id)
            return message_content.content
        except LineBotApiError as e:
            logger.error(f"Failed to download image: {str(e)}")
            raise LineBotError(f"Image download failed: {str(e)}", provider="line")

    async def _analyze_image(self, user_id: str, image_data: bytes, message_id: str) -> dict[str, Any]:
        """Analyze image using analysis service."""
        try:
            # Perform analysis
            result = await self.analysis_service.analyze_face_image(
                image_data=image_data,
                filename=f"line_image_{message_id}.jpg",
                user_id=None,  # Anonymous analysis for LINE users
                analysis_type="full"
            )
            
            return result
            
        except AnalysisError as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise LineBotError(f"Analysis failed: {str(e)}", provider="analysis")

    async def _send_welcome_message(self, user_id: str) -> None:
        """Send welcome message."""
        welcome_text = """🌟 Face Aesthetic AI へようこそ！

私はあなたの美容パートナーです ✨

【できること】
📷 顔写真の美容分析
💬 美容相談・アドバイス
📊 詳細レポート生成

【使い方】
1. 写真を送信 → 即座に分析
2. 「相談」と送信 → AI美容コンサル
3. 「ヘルプ」と送信 → 詳しい使い方

まずは写真を送ってみてください！"""

        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="📷 写真分析", text="写真を送信してください")),
            QuickReplyButton(action=MessageAction(label="💬 美容相談", text="相談")),
            QuickReplyButton(action=MessageAction(label="❓ ヘルプ", text="ヘルプ")),
        ])

        await self.line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=welcome_text, quick_reply=quick_reply)]
            )
        )

    async def _send_help_message(self, user_id: str) -> None:
        """Send help message."""
        help_text = """📖 Face Aesthetic AI 使い方ガイド

【写真分析の手順】
1. 顔全体が写った正面写真を送信
2. AI が468点の顔面ランドマークを検出
3. 韓国美容基準で詳細分析
4. 美容スコアとアドバイスを提供

【写真撮影のコツ】
✅ 正面を向いて表情なし
✅ 明るい場所で撮影
✅ 髪で顔が隠れないように
✅ メイクは薄めがベスト

【分析項目】
• Eライン • パーツ調和性
• 顔の対称性 • 輪郭分析
• Vライン • 鼻唇角

【コマンド】
- 「分析」→ 分析について
- 「相談」→ AI美容コンサル
- 「スタート」→ 最初から"""

        await self.line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=help_text)]
            )
        )

    async def _send_analysis_instruction(self, user_id: str) -> None:
        """Send analysis instruction."""
        instruction_text = """📸 美容分析を始めましょう！

以下の点にご注意ください：

✨ より正確な分析のために
• 正面を向いた写真
• 十分な明るさ
• 表情は自然な状態
• 顔全体がはっきり見える

📊 分析される項目
• 総合美容スコア
• Eライン評価
• パーツ調和性
• 対称性分析
• 輪郭・Vライン
• 詳細な改善アドバイス

準備ができたら写真を送信してください 📷"""

        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="📷 写真を送信", text="写真を送信します")),
            QuickReplyButton(action=MessageAction(label="💡 撮影のコツ", text="撮影のコツを教えて")),
        ])

        self.line_bot_api.push_message(
            user_id,
            TextSendMessage(text=instruction_text, quick_reply=quick_reply)
        )

    async def _send_processing_message(self, user_id: str) -> None:
        """Send processing message."""
        processing_text = """🔍 AI分析中です...

お写真を受信しました！
最先端のAI技術で詳細に分析しています。

⏱️ 分析時間: 約30-60秒
🧠 AI処理: 468点の顔面ランドマーク検出
📊 評価項目: 8つの美容指標

少々お待ちください ✨"""

        self.line_bot_api.push_message(
            user_id,
            TextSendMessage(text=processing_text)
        )

    async def _send_analysis_results(self, user_id: str, analysis_result: dict[str, Any]) -> None:
        """Send analysis results."""
        try:
            # Extract key metrics
            overall_score = analysis_result.get("overall_score", {})
            score = overall_score.get("score", 0)
            level = overall_score.get("level", "分析中")
            emoji = overall_score.get("emoji", "✨")
            
            # Main result message
            result_text = f"""🎉 分析完了！

{emoji} 総合スコア: {score:.1f}点
🏆 美容レベル: {level}

【詳細スコア】"""

            # Add detailed scores
            detailed_scores = overall_score.get("detailed_scores", {})
            for key, value in list(detailed_scores.items())[:5]:  # Top 5 scores
                feature_name = self._get_feature_name(key)
                result_text += f"\n• {feature_name}: {value:.1f}点"

            # Add advice preview
            advice = analysis_result.get("beauty_advice", [])
            if advice:
                result_text += f"\n\n💡 改善アドバイス（抜粋）\n• {advice[0][:50]}..."

            # Quick reply options
            quick_reply = QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="💬 詳しく相談", text="この結果について相談したい")),
                QuickReplyButton(action=MessageAction(label="📊 詳細レポート", text="詳細レポートが欲しい")),
                QuickReplyButton(action=MessageAction(label="🔄 再分析", text="別の写真で分析")),
            ])

            self.line_bot_api.push_message(
                user_id,
                TextSendMessage(text=result_text, quick_reply=quick_reply)
            )

            # Send carousel with detailed breakdown
            await self._send_detailed_carousel(user_id, analysis_result)

        except Exception as e:
            logger.error(f"Failed to send analysis results: {str(e)}")
            await self._send_error_message(user_id)

    async def _send_detailed_carousel(self, user_id: str, analysis_result: dict[str, Any]) -> None:
        """Send detailed analysis carousel."""
        try:
            columns = []
            
            # Overall Score Card
            overall_score = analysis_result.get("overall_score", {})
            columns.append(CarouselColumn(
                thumbnail_image_url="https://example.com/overall-score.jpg",  # Replace with actual image
                title=f"総合スコア {overall_score.get('score', 0):.1f}点",
                text=f"{overall_score.get('emoji', '✨')} {overall_score.get('level', '')}",
                actions=[
                    MessageAction(label="詳しく見る", text="総合スコアについて教えて"),
                    URIAction(label="Webで確認", uri="https://your-domain.com/analysis")  # Replace with actual URL
                ]
            ))

            # Feature cards
            features = [
                ("eline", "Eライン", "💋"),
                ("facial_harmony", "パーツ調和", "🌟"),
                ("symmetry", "対称性", "⚖️"),
                ("vline", "Vライン", "✨")
            ]

            for feature_key, feature_name, emoji in features[:3]:  # Limit to 3 more cards
                feature_data = analysis_result.get(f"{feature_key}_analysis", 
                                                 analysis_result.get(feature_key, {}))
                
                if feature_data:
                    score = self._extract_score(feature_data)
                    evaluation = feature_data.get("evaluation", "分析中")
                    
                    columns.append(CarouselColumn(
                        thumbnail_image_url=f"https://example.com/{feature_key}.jpg",  # Replace with actual images
                        title=f"{emoji} {feature_name}",
                        text=f"スコア: {score:.1f}点\n{evaluation}",
                        actions=[
                            MessageAction(label="詳細", text=f"{feature_name}について詳しく教えて"),
                            MessageAction(label="改善方法", text=f"{feature_name}の改善方法は？")
                        ]
                    ))

            if columns:
                carousel_template = CarouselTemplate(columns=columns)
                template_message = TemplateSendMessage(
                    alt_text="詳細分析結果",
                    template=carousel_template
                )
                
                self.line_bot_api.push_message(user_id, template_message)

        except Exception as e:
            logger.error(f"Failed to send carousel: {str(e)}")

    async def _handle_chat_request(self, user_id: str, message: str) -> None:
        """Handle chat consultation request."""
        chat_text = """💬 AI美容コンサルテーション

韓国美容のプロフェッショナルAIがあなたの美容に関する質問にお答えします！

【相談できること】
• 分析結果の詳しい説明
• 具体的な改善方法
• おすすめコスメ・スキンケア
• メイクテクニック
• K-Beauty トレンド

どんなことでもお気軽にご質問ください ✨"""

        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="分析結果について", text="分析結果について詳しく教えて")),
            QuickReplyButton(action=MessageAction(label="改善方法", text="美容改善の具体的な方法は？")),
            QuickReplyButton(action=MessageAction(label="韓国コスメ", text="おすすめの韓国コスメを教えて")),
        ])

        self.line_bot_api.push_message(
            user_id,
            TextSendMessage(text=chat_text, quick_reply=quick_reply)
        )

    async def _handle_chat_message(self, user_id: str, message: str) -> None:
        """Handle chat message with AI."""
        try:
            # Get bot user
            bot_user = await self._get_or_create_user(user_id)
            
            # Create or get chat session
            session = await self.chatbot_service.create_chat_session(
                user_id=UUID(str(bot_user.id)),  # Convert to proper UUID
                title="LINE相談",
                context_type="line_chat",
                initial_message=message
            )
            
            # Get AI response
            response = await self.chatbot_service.send_message(
                session_id=session.id,
                user_id=UUID(str(bot_user.id)),
                message=message
            )
            
            # Send response back to LINE
            await self._send_chat_response(user_id, response.message, response.suggestions)
            
        except Exception as e:
            logger.error(f"Chat handling failed: {str(e)}")
            await self._send_error_message(user_id)

    async def _send_chat_response(self, user_id: str, response_text: str, suggestions: list[str]) -> None:
        """Send chat response to LINE user."""
        # Limit response length for LINE
        if len(response_text) > 2000:
            response_text = response_text[:1950] + "...\n\n詳細はWebサイトでご確認ください。"

        quick_reply_items = []
        for suggestion in suggestions[:3]:  # Limit to 3 suggestions
            if len(suggestion) <= 20:  # LINE quick reply label limit
                quick_reply_items.append(
                    QuickReplyButton(action=MessageAction(label=suggestion, text=suggestion))
                )

        quick_reply = QuickReply(items=quick_reply_items) if quick_reply_items else None

        self.line_bot_api.push_message(
            user_id,
            TextSendMessage(text=response_text, quick_reply=quick_reply)
        )

    async def _send_error_message(self, user_id: str) -> None:
        """Send error message."""
        error_text = """😅 申し訳ございません

一時的な問題が発生しました。
しばらく時間をおいてから再度お試しください。

📞 サポートが必要な場合
• 「ヘルプ」と送信
• Webサイトでお問い合わせ

ご不便をおかけして申し訳ありません 🙏"""

        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="🔄 再試行", text="もう一度")),
            QuickReplyButton(action=MessageAction(label="❓ ヘルプ", text="ヘルプ")),
        ])

        self.line_bot_api.push_message(
            user_id,
            TextSendMessage(text=error_text, quick_reply=quick_reply)
        )

    async def _deactivate_user(self, line_user_id: str) -> None:
        """Deactivate LINE user."""
        try:
            self.supabase.table("line_bot_users").update({
                "is_active": False,
                "updated_at": datetime.now().isoformat()
            }).eq("line_user_id", line_user_id).execute()
            
        except Exception as e:
            logger.error(f"Failed to deactivate user: {str(e)}")

    def _get_feature_name(self, key: str) -> str:
        """Get Japanese feature name."""
        feature_names = {
            "eline": "Eライン",
            "harmony": "パーツ調和",
            "symmetry": "対称性",
            "proportions": "顔の比率",
            "vline": "Vライン",
            "nasolabial": "鼻唇角",
            "dental": "歯列・唇",
            "contour": "輪郭",
            "philtrum_chin": "人中・顎",
        }
        return feature_names.get(key, key)

    def _extract_score(self, data: dict[str, Any]) -> float:
        """Extract score from analysis data."""
        if "score" in data:
            return float(data["score"])
        elif "evaluation" in data:
            evaluation = data["evaluation"].lower()
            if "理想" in evaluation or "優秀" in evaluation:
                return 90.0
            elif "良好" in evaluation:
                return 80.0
            elif "標準" in evaluation:
                return 70.0
            else:
                return 60.0
        return 70.0


# Global service instance
_linebot_service_instance: LineBotService | None = None


def get_linebot_service(supabase_client: Client) -> LineBotService:
    """Get or create LINE Bot service instance."""
    global _linebot_service_instance
    if _linebot_service_instance is None:
        _linebot_service_instance = LineBotService(supabase_client)
    return _linebot_service_instance