# Face Aesthetic AI - デプロイメントガイド

## 🚀 完全デプロイメントガイド

このガイドは、本番環境、開発環境、および各種ホスティングプラットフォームのデプロイメントについて説明します。

## 📋 前提条件

### 必要なサービス
- **Supabaseアカウント** (データベースとストレージ)
- **OpenAI APIキー** (ChatGPT-4o-mini)
- **LINE Developersアカウント** (LINE Bot)
- **ドメインとSSL証明書** (本番環境用)

### 開発ツール
- Docker & Docker Compose
- Node.js 18+ (ローカルフロントエンド開発用)
- Python 3.12+ with uv (ローカルバックエンド開発用)

## 🔧 環境セットアップ

### 1. Supabaseセットアップ

```bash
# 1. https://supabase.com でプロジェクトを作成
# 2. プロジェクトURLとキーを取得
# 3. backend/app/schemas/supabase.py からSQLスキーマを実行
# 4. ストレージバケットとポリシーを設定
```

### 2. 環境変数

`.env`ファイルを作成：

**バックエンド (.env)**:
```env
# アプリケーション設定
SECRET_KEY=your-super-secret-key-here
DEBUG=false
ENVIRONMENT=production

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# OpenAI
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=500

# LINE Bot
LINE_CHANNEL_ACCESS_TOKEN=your-line-channel-access-token
LINE_CHANNEL_SECRET=your-line-channel-secret

# URL
APP_URL=https://your-domain.com
API_PREFIX=/api/v1

# セキュリティ
ALLOWED_ORIGINS=["https://your-frontend-domain.com","https://your-domain.com"]
```

**フロントエンド (.env.local)**:
```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_APP_URL=https://your-frontend-domain.com
```

## 🐳 Dockerデプロイメント

### 開発環境

```bash
# 開発環境の起動
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# ローカルデータベースを使用
docker compose -f docker-compose.yml -f docker-compose.dev.yml --profile development up
```

### 本番環境

```bash
# 本番環境のビルドと起動
docker compose --profile production up -d

# サービスのスケーリング
docker compose --profile production up -d --scale backend=3

# サービスの更新
docker compose pull
docker compose --profile production up -d
```

### モニタリング

```bash
# ログの確認
docker-compose logs -f backend
docker-compose logs -f frontend

# ヘルスチェック
curl http://localhost/health
curl http://localhost/api/v1/health
```

## ☁️ クラウドデプロイメント

### Vercel (フロントエンド)

```bash
# Vercel CLIのインストール
npm i -g vercel

# フロントエンドディレクトリからデプロイ
cd frontend
vercel --prod

# Vercelダッシュボードの環境変数:
# NEXT_PUBLIC_API_URL
# NEXT_PUBLIC_SUPABASE_URL
# NEXT_PUBLIC_SUPABASE_ANON_KEY
```

### Railway/Render (バックエンド)

**クラウド用Dockerfile最適化**:
```dockerfile
# RailwayのPORT環境変数を使用
ENV PORT=8000
EXPOSE $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### AWS ECS/EKS

```yaml
# ECS用docker-compose.prod.yml
version: '3.8'
services:
  backend:
    image: your-registry/face-aesthetic-backend:latest
    environment:
      - AWS_REGION=us-west-2
    secrets:
      - openai_api_key
      - supabase_service_key
```

## 🛠️ LINE Botセットアップ

### 1. LINEチャネルの作成

1. [LINE Developers Console](https://developers.line.biz/)にアクセス
2. 新しいプロバイダーとチャネルを作成
3. チャネルアクセストークンとチャネルシークレットを取得

### 2. Webhook URLの設定

```bash
# LINEコンソールでWebhook URLを設定
https://your-domain.com/api/v1/linebot/webhook

# Webhookのテスト
curl -X POST https://your-domain.com/api/v1/linebot/info
```

### 3. 統合の確認

```bash
# LINE Botの状態確認
curl https://your-domain.com/api/v1/linebot/health

# テストメッセージの送信
curl -X POST "https://your-domain.com/api/v1/linebot/test-message?user_id=test&message=hello"
```

## 🔐 セキュリティとSSL

### SSL証明書のセットアップ

```nginx
# nginx/ssl.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # セキュリティヘッダー
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

### レート制限

```nginx
# nginx.conf内
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=upload:10m rate=2r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
}
```

## 📊 モニタリングとログ

### ヘルスチェック

```bash
# アプリケーションの健全性
curl https://your-domain.com/health

# APIの健全性
curl https://your-domain.com/api/v1/health

# LINE Botの健全性
curl https://your-domain.com/api/v1/linebot/health

# サービスステータス
curl https://your-domain.com/api/v1/analysis/status
curl https://your-domain.com/api/v1/chat/status
```

### ログモニタリング

```bash
# Dockerログ
docker-compose logs -f --tail=100 backend

# Nginxログ
docker-compose exec nginx tail -f /var/log/nginx/access.log
docker-compose exec nginx tail -f /var/log/nginx/error.log
```

## 🔄 CI/CDパイプライン

### GitHub Actionsの例

```yaml
# .github/workflows/deploy.yml
name: 本番環境へのデプロイ

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: バックエンドのビルドとデプロイ
        run: |
          docker build -t face-aesthetic-backend ./backend
          # プラットフォームへのデプロイ
          
      - name: フロントエンドのデプロイ
        run: |
          cd frontend
          npm ci
          npm run build
          # Vercel/Netlifyへのデプロイ
```

## 🧪 デプロイメントのテスト

### 自動テスト

```bash
# バックエンドテストの実行
cd backend
uv run pytest tests/ -v

# フロントエンドテストの実行（実装済みの場合）
cd frontend
npm test

# 統合テスト
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### 手動テストチェックリスト

- [ ] フロントエンドが正しく読み込まれる
- [ ] 画像アップロードが機能する
- [ ] 分析が正常に完了する
- [ ] チャットインターフェースが機能する
- [ ] LINE Botがメッセージに応答する
- [ ] ヘルスチェックが成功する
- [ ] SSL証明書が有効
- [ ] レート制限が機能する
- [ ] エラー処理が適切

## 🚨 トラブルシューティング

### 一般的な問題

**バックエンド起動失敗**:
```bash
# 環境変数の確認
docker-compose exec backend env | grep -E "(SUPABASE|OPENAI|LINE)"

# ログの確認
docker-compose logs backend
```

**フロントエンドがAPIに接続できない**:
```bash
# CORS設定の確認
curl -H "Origin: https://your-frontend.com" https://your-api.com/api/v1/

# ネットワーク接続の確認
docker-compose exec frontend curl backend:8000/health
```

**LINE Botが応答しない**:
```bash
# Webhook URLの確認
curl -X POST https://your-domain.com/api/v1/linebot/webhook \
  -H "X-Line-Signature: test" \
  -d '{"events":[]}'

# LINE設定の確認
curl https://your-domain.com/api/v1/linebot/info
```

### パフォーマンス最適化

```bash
# リソース使用量のモニタリング
docker stats

# サービスのスケーリング
docker-compose up -d --scale backend=3 --scale frontend=2

# 圧縮の有効化
# nginx.confで既に設定済み
```

## 📱 モバイルアプリデプロイメント（将来）

### Flutterアプリの準備

```yaml
# バックエンド統合用pubspec.yamlの追加
dependencies:
  http: ^0.13.5
  image_picker: ^0.8.6
  cached_network_image: ^3.2.3
```

### アプリストア設定

```bash
# iOSデプロイメント
cd mobile_app
flutter build ios --release

# Androidデプロイメント
flutter build appbundle --release
```

## 🔧 メンテナンス

### 定期的なタスク

```bash
# 依存関係の更新
cd backend && uv sync --upgrade
cd frontend && npm update

# 古いデータのクリーンアップ
docker system prune -f
docker volume prune -f

# データベースのバックアップ（ローカルPostgreSQL使用時）
docker-compose exec postgres pg_dump -U postgres face_aesthetic_dev > backup.sql
```

### セキュリティ更新

```bash
# ベースイメージの更新
docker pull node:18-alpine
docker pull python:3.12-slim
docker pull nginx:alpine
docker pull postgres:15-alpine
docker pull redis:7-alpine

# 最新イメージでの再ビルド
docker-compose build --no-cache
```

---

## 📞 サポート

デプロイメントの問題については：
1. 上記のトラブルシューティングセクションを確認
2. アプリケーションログを確認
3. すべての環境変数を確認
4. 各サービスを個別にテスト
5. 必要に応じてサポートチームに連絡

これで本番環境の完全な設定が完了しました！🎉