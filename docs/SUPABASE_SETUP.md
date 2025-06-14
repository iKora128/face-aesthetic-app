# 🗄️ Supabase セットアップガイド

このガイドでは、Face Aesthetic Appで使用するSupabaseプロジェクトの設定方法を説明します。

## 📋 前提条件

- [Supabase](https://supabase.com)アカウント
- 管理者権限でのSupabaseプロジェクトアクセス

## 🚀 1. Supabaseプロジェクト作成

### 1.1 新しいプロジェクトを作成

1. [Supabase Dashboard](https://app.supabase.com)にログイン
2. "New Project"をクリック
3. プロジェクト設定:
   - **Name**: `face-aesthetic-app`
   - **Database Password**: 強力なパスワードを設定
   - **Region**: 日本に最も近いリージョン（Asia Pacific）を選択
4. "Create new project"をクリック

### 1.2 プロジェクト情報の取得

プロジェクト作成後、以下の情報を取得します：

- **Project URL**: `https://your-project-id.supabase.co`
- **API Keys**:
  - `anon` key（公開用）
  - `service_role` key（サーバー用）

## 🗃️ 2. データベーススキーマの設定

### 2.1 SQLエディターでスキーマを実行

1. Supabase Dashboard → **SQL Editor**
2. "New query"をクリック
3. `backend/app/schemas/supabase.py`から`SUPABASE_SCHEMA_SQL`の内容をコピー
4. SQLエディターに貼り付けて実行

### 2.2 作成されるテーブル

| テーブル名 | 説明 |
|-----------|------|
| `user_profiles` | ユーザープロフィール情報 |
| `analysis_results` | 顔面分析結果 |
| `chat_sessions` | チャットセッション |
| `chat_messages` | チャットメッセージ |
| `stored_images` | 画像メタデータ |
| `user_analytics` | ユーザー分析統計 |
| `line_bot_users` | LINE Botユーザー |

## 🗂️ 3. Storageバケットの設定

### 3.1 バケット作成

Supabase Dashboard → **Storage** → "Create bucket"

以下の3つのバケットを作成：

#### 📁 user-images（ユーザーアップロード画像）
```
Name: user-images
Public: No (Private)
File size limit: 10MB
Allowed MIME types: image/jpeg, image/png, image/webp
```

#### 📁 report-images（生成レポート画像）
```
Name: report-images  
Public: No (Private)
File size limit: 5MB
Allowed MIME types: image/jpeg, image/png
```

#### 📁 avatars（プロフィール画像）
```
Name: avatars
Public: Yes (Public)
File size limit: 2MB
Allowed MIME types: image/jpeg, image/png, image/webp
```

### 3.2 Storage Policies設定

各バケットに適切なRLSポリシーを設定：

#### user-images policies
```sql
-- ユーザーは自分の画像のみアップロード可能
CREATE POLICY "Users can upload own images" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'user-images' AND auth.uid()::text = (storage.foldername(name))[1]);

-- ユーザーは自分の画像のみ表示可能
CREATE POLICY "Users can view own images" ON storage.objects
FOR SELECT USING (bucket_id = 'user-images' AND auth.uid()::text = (storage.foldername(name))[1]);

-- ユーザーは自分の画像のみ削除可能
CREATE POLICY "Users can delete own images" ON storage.objects
FOR DELETE USING (bucket_id = 'user-images' AND auth.uid()::text = (storage.foldername(name))[1]);
```

#### report-images policies
```sql
-- サービスロールがレポート生成
CREATE POLICY "Service role can upload reports" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'report-images' AND auth.role() = 'service_role');

-- ユーザーは自分のレポートのみ表示可能
CREATE POLICY "Users can view own reports" ON storage.objects
FOR SELECT USING (bucket_id = 'report-images' AND auth.uid()::text = (storage.foldername(name))[1]);
```

#### avatars policies
```sql
-- ユーザーは自分のアバターのみアップロード
CREATE POLICY "Users can upload own avatar" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'avatars' AND auth.uid()::text = (storage.foldername(name))[1]);

-- 全員がアバターを表示可能（パブリック）
CREATE POLICY "Anyone can view avatars" ON storage.objects
FOR SELECT USING (bucket_id = 'avatars');

-- ユーザーは自分のアバターのみ更新・削除
CREATE POLICY "Users can update own avatar" ON storage.objects
FOR UPDATE USING (bucket_id = 'avatars' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can delete own avatar" ON storage.objects
FOR DELETE USING (bucket_id = 'avatars' AND auth.uid()::text = (storage.foldername(name))[1]);
```

## 🔐 4. 認証設定

### 4.1 Authentication Providers

Supabase Dashboard → **Authentication** → **Providers**

推奨設定：
- **Email**: 有効化（デフォルト）
- **Google**: 有効化（オプション）
- **LINE**: 有効化（LINE Botと連携する場合）

### 4.2 Email Templates

**Authentication** → **Email Templates**でメールテンプレートをカスタマイズ：

- **Confirm signup**: 日本語対応
- **Reset password**: 日本語対応  
- **Magic link**: 日本語対応

### 4.3 URL Configuration

**Authentication** → **URL Configuration**:

- **Site URL**: `http://localhost:3000`（開発時）
- **Redirect URLs**: 
  - `http://localhost:3000/auth/callback`
  - `https://your-production-domain.com/auth/callback`

## ⚙️ 5. 環境変数設定

### 5.1 Backend (.env)
```bash
# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

### 5.2 Frontend (.env.local)  
```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## 🧪 6. 接続テスト

### 6.1 データベース接続確認

```python
# Python (Backend)
from supabase import create_client
import os

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY") 
supabase = create_client(url, key)

# テスト
response = supabase.table('user_profiles').select('*').limit(1).execute()
print("接続成功:", response)
```

### 6.2 フロントエンド接続確認

```javascript
// JavaScript (Frontend)
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

// テスト
const testConnection = async () => {
  const { data, error } = await supabase
    .from('user_profiles')
    .select('*')
    .limit(1)
  
  console.log('接続成功:', data)
}
```

## 📊 7. 本番環境での追加設定

### 7.1 Security

- **RLS**: すべてのテーブルでRow Level Securityを有効化済み
- **API Keys**: 本番環境では環境変数で管理
- **CORS**: 本番ドメインのみ許可

### 7.2 Performance

**Database** → **Settings**:
- **Connection pooling**: 有効化
- **Read replicas**: 必要に応じて設定

### 7.3 Backup

**Database** → **Backups**:
- **Point-in-time recovery**: 有効化
- **Automated backups**: 設定

## 🚨 8. トラブルシューティング

### よくある問題

#### RLS Policy エラー
```
Row level security is enabled but no policy allows this operation
```
**解決法**: 適切なRLSポリシーが設定されているか確認

#### Storage Upload エラー  
```
The resource was not found
```
**解決法**: バケットが存在し、適切なポリシーが設定されているか確認

#### 認証エラー
```
Invalid API key
```
**解決法**: 
- 環境変数が正しく設定されているか確認
- anonキーとservice_roleキーを混同していないか確認

## 📞 サポート

問題が解決しない場合：
1. [Supabase Documentation](https://supabase.com/docs)
2. [Supabase Discord](https://discord.supabase.com)
3. GitHub Issues

## ✅ セットアップ完了チェックリスト

- [ ] Supabaseプロジェクト作成
- [ ] データベーススキーマ実行
- [ ] Storageバケット作成（3個）
- [ ] Storage Policies設定
- [ ] 認証プロバイダー設定
- [ ] 環境変数設定
- [ ] 接続テスト完了
- [ ] RLSポリシー動作確認

すべて完了したら、Face Aesthetic Appの開発を開始できます！