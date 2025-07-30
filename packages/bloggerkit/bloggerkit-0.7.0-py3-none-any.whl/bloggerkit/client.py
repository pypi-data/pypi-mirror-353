import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json
from typing import Optional, List, Dict, Any

from bloggerkit.model import Author, Blog, Replies, Post, PostList, Error

# Blogger API에 필요한 Scope 설정
SCOPES = ['https://www.googleapis.com/auth/blogger']
# API 이름 및 버전
API_SERVICE_NAME = 'blogger'
API_VERSION = 'v3'
# 토큰 파일 이름 (클래스 내부에서 관리)
TOKEN_FILE = 'token.json'

class BloggerClient:
    """A client for interacting with the Google Blogger API using OAuth 2.0."""

    def __init__(self, blog_id: str, client_secrets_file: str = None, client_id: str = None, client_secret: str = None) -> None:
        """Initializes the BloggerClient with a blog ID and OAuth 2.0 credentials.

        Args:
            blog_id: The ID of the blog to interact with.
            client_secrets_file: The path to the client_secrets.json file (optional if client_id/client_secret provided).
            client_id: Google OAuth 2.0 client ID (optional, can be set via GOOGLE_CLIENT_ID env var).
            client_secret: Google OAuth 2.0 client secret (optional, can be set via GOOGLE_CLIENT_SECRET env var).
        """
        self.blog_id = blog_id
        
        # 우선순위: 직접 파라미터 > 환경변수 > client_secrets_file
        self.client_id = client_id or os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('GOOGLE_CLIENT_SECRET')
        
        if self.client_id and self.client_secret:
            # 환경변수나 파라미터로 제공된 경우 자동으로 credentials.json 생성
            self.client_secrets_file = self._create_credentials_json()
            print(f"✅ Auto-generated credentials file: {self.client_secrets_file}")
        elif client_secrets_file and os.path.exists(client_secrets_file):
            # 기존 방식: client_secrets_file 직접 제공
            self.client_secrets_file = client_secrets_file
        else:
            # 에러 메시지 개선
            error_msg = """
❌ Authentication credentials not found!

Please provide credentials in one of these ways:

1. Environment Variables (Recommended):
   Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file
   
2. Direct Parameters:
   BloggerClient(blog_id, client_id='your_id', client_secret='your_secret')
   
3. Credentials File:
   BloggerClient(blog_id, client_secrets_file='path/to/credentials.json')

To get your credentials:
1. Go to https://console.cloud.google.com/
2. APIs & Services → Credentials
3. Create OAuth 2.0 Client ID (Desktop Application)
4. Copy Client ID and Client Secret
            """
            raise ValueError(error_msg.strip())
        
        self.service = self._authenticate()

    def _create_credentials_json(self) -> str:
        """환경변수나 파라미터로부터 credentials.json 자동 생성"""
        credentials_data = {
            "installed": {
                "client_id": self.client_id,
                "project_id": "blogger-automation",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": self.client_secret,
                "redirect_uris": ["http://localhost"]
            }
        }
        
        credentials_file = "auto_credentials.json"
        try:
            with open(credentials_file, 'w') as f:
                json.dump(credentials_data, f, indent=2)
            return credentials_file
        except Exception as e:
            raise RuntimeError(f"Failed to create credentials file: {e}")

    def _authenticate(self):
        """Authenticates with Google using OAuth 2.0 and returns the Blogger service."""
        creds = None

        # token.json 파일에 사용자 인증 정보가 저장되어 있는지 확인
        if os.path.exists(TOKEN_FILE):
            try:
                creds = google.oauth2.credentials.Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            except Exception as e:
                print(f"⚠️ Error loading existing token: {e}")
                # 토큰 파일이 손상된 경우 삭제
                os.remove(TOKEN_FILE)

        # (아직) 유효한 인증 정보가 없다면, 사용자에게 로그인 요청
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("🔄 Refreshing expired token...")
                    creds.refresh(google.auth.transport.requests.Request())
                    print("✅ Token refreshed successfully!")
                except Exception as e:
                    print(f"❌ Error refreshing credentials: {e}")
                    print("🔄 Starting new authentication flow...")
                    if os.path.exists(TOKEN_FILE):
                        os.remove(TOKEN_FILE)  # 토큰 갱신에 실패하면 토큰 파일 삭제 후 재인증 시도
                    return self._authenticate()  # 재귀 호출을 통해 다시 인증 시도
            else:
                print("🚀 Starting OAuth 2.0 authentication flow...")
                print("📱 Your browser will open for authentication...")
                try:
                    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                        self.client_secrets_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                    print("✅ Authentication successful!")
                except Exception as e:
                    raise RuntimeError(f"Authentication failed: {e}")

            # 인증 정보를 token.json 파일에 저장
            try:
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                print(f"💾 Authentication token saved to {TOKEN_FILE}")
            except Exception as e:
                print(f"⚠️ Warning: Could not save token file: {e}")

        try:
            # Construct the service object for the Blogger API.
            service = build(API_SERVICE_NAME, API_VERSION, credentials=creds)
            print("🎉 Blogger API client initialized successfully!")
            return service
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Blogger API service: {e}")

    def list_posts(self) -> Optional[PostList]:
        """Lists all posts in the blog.

        Returns:
            A PostList object containing the list of posts, or None if an error occurred.
        """
        try:
            results = self.service.posts().list(blogId=self.blog_id).execute()
            posts = []
            for item in results.get("items", []):
                author_data = item.get("author", {})
                author = Author(
                    displayName=author_data.get("displayName", ""),
                    id=author_data.get("id", ""),
                    image=author_data.get("image", {}),
                    url=author_data.get("url", ""),
                )
                blog_data = item.get("blog", {})
                blog = Blog(id=blog_data.get("id", ""))
                replies_data = item.get("replies", {})
                replies = Replies(
                    selfLink=replies_data.get("selfLink", ""),
                    totalItems=replies_data.get("totalItems", ""),
                )
                post = Post(
                    author=author,
                    blog=blog,
                    content=item.get("content", ""),
                    etag=item.get("etag", ""),
                    id=item.get("id", ""),
                    kind=item.get("kind", ""),
                    labels=item.get("labels", []),
                    published=item.get("published", ""),
                    replies=replies,
                    selfLink=item.get("selfLink", ""),
                    title=item.get("title", ""),
                    updated=item.get("updated", ""),
                    url=item.get("url", ""),
                )
                posts.append(post)
            return PostList(
                kind=results.get("kind", ""),
                nextPageToken=results.get("nextPageToken", ""),
                items=posts,
                etag=results.get("etag", ""),
            )
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None

    def create_post(self, title: str, content: str, labels: List[str] = None, is_draft: bool = False) -> Optional[Dict[str, Any]]:
        """Creates a new post in the blog.

        Args:
            title: The title of the new post.
            content: The content of the new post.
            labels: Optional list of labels/tags for the post.
            is_draft: Whether to save the post as a draft.

        Returns:
            A dictionary containing the new post, or None if an error occurred.
        """
        post_body = {
            'title': title,
            'content': content,
        }
        
        if labels:
            post_body['labels'] = labels
            
        if is_draft:
            post_body['isDraft'] = True
            
        try:
            print(f"📝 Creating post: '{title}'...")
            results = self.service.posts().insert(blogId=self.blog_id, body=post_body, isDraft=is_draft).execute()
            print(f"✅ Post created successfully!")
            print(f"🔗 URL: {results.get('url', 'N/A')}")
            return results
        except HttpError as e:
            print(f"❌ An HTTP error occurred: {e}")
            return None

    def get_post(self, post_id: str) -> Optional[Post]:
        """Retrieves a specific post from the blog.

        Args:
            post_id: The ID of the post to retrieve.

        Returns:
            A Post object containing the post, or None if an error occurred.
        """
        try:
            results = self.service.posts().get(blogId=self.blog_id, postId=post_id).execute()

            author_data = results.get("author", {})
            author = Author(
                displayName=author_data.get("displayName", ""),
                id=author_data.get("id", ""),
                image=author_data.get("image", {}),
                url=author_data.get("url", ""),
            )
            blog_data = results.get("blog", {})
            blog = Blog(id=blog_data.get("id", ""))
            replies_data = results.get("replies", {})
            replies = Replies(
                selfLink=replies_data.get("selfLink", ""),
                totalItems=replies_data.get("totalItems", ""),
            )
            return Post(
                author=author,
                blog=blog,
                content=results.get("content", ""),
                etag=results.get("etag", ""),
                id=results.get("id", ""),
                kind=results.get("kind", ""),
                labels=results.get("labels", []),
                published=results.get("published", ""),
                replies=replies,
                selfLink=results.get("selfLink", ""),
                title=results.get("title", ""),
                updated=results.get("updated", ""),
                url=results.get("url", ""),
            )
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None

    def update_post(self, post_id: str, title: str, content: str, labels: List[str] = None) -> Optional[Dict[str, Any]]:
        """Updates a specific post in the blog.

        Args:
            post_id: The ID of the post to update.
            title: The new title of the post.
            content: The new content of the post.
            labels: Optional list of labels/tags for the post.

        Returns:
            A dictionary containing the updated post, or None if an error occurred.
        """
        post_body = {
            'title': title,
            'content': content
        }
        
        if labels:
            post_body['labels'] = labels
            
        try:
            print(f"📝 Updating post: '{title}'...")
            results = self.service.posts().update(blogId=self.blog_id, postId=post_id, body=post_body).execute()
            print(f"✅ Post updated successfully!")
            print(f"🔗 URL: {results.get('url', 'N/A')}")
            return results
        except HttpError as e:
            print(f"❌ An HTTP error occurred: {e}")
            return None

    def delete_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Deletes a specific post from the blog.

        Args:
            post_id: The ID of the post to delete.

        Returns:
            A dictionary containing the deleted post, or None if an error occurred.
        """
        try:
            print(f"🗑️ Deleting post ID: {post_id}...")
            self.service.posts().delete(blogId=self.blog_id, postId=post_id).execute()
            print(f"✅ Post deleted successfully!")
            return {} # 성공적으로 삭제된 경우 빈 딕셔너리 반환
        except HttpError as e:
            print(f"❌ An HTTP error occurred: {e}")
            return None

if __name__ == "__main__":
    # Replace with your blog ID and client_secrets.json path
    blog_id = "YOUR_BLOG_ID"
    client_secrets_file = "YOUR_CLIENT_SECRETS_FILE_PATH"
    client = BloggerClient(blog_id, client_secrets_file)

    # Example usage
    # List posts
    posts = client.list_posts()
    if posts:
        print("Posts:")
        for post in posts.items:
            print(f"- {post.title}: {post.url}")

    # Create a new post
    new_post = client.create_post("Test Post3", "This is a test post created using the Blogger API.")
    if new_post:
        print(f"New post created: {new_post.get('url')}")

    # Get a specific post
    # post = client.get_post("POST_ID")  # Replace with a valid post ID
    # if post:
    #     print(f"Post: {post.title}, {post.content}")

    # Update a post
    # updated_post = client.update_post("POST_ID", "Updated Test Post", "This is the updated content.")
    # if updated_post:
    #     print(f"Post updated: {updated_post.get('url')}")

    # Delete a post
    # deleted = client.delete_post("POST_ID")
