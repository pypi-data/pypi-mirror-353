# Bloggerkit

A Python toolkit for interacting with the Google Blogger API with **simplified authentication** and **enhanced features**.

## ✨ What's New in v0.7.0

🔧 **Environment Variable Support** - No more manual `credentials.json` management!  
🚀 **Auto-generated Credentials** - Automatically creates credentials from environment variables  
🔄 **Full Backward Compatibility** - All existing code continues to work unchanged  
📝 **Enhanced Post Features** - Added `labels` and `is_draft` parameters  
💬 **Improved User Experience** - Better error messages and helpful logging  

## 📦 Installation

```bash
pip install bloggerkit
```

## 🚀 Quick Start

### Method 1: Environment Variables (Recommended)

1. **Set up Google Cloud Console:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the **Blogger API**
   - Go to **APIs & Services** → **Credentials**
   - Create **OAuth 2.0 Client ID** (Desktop Application)
   - Copy the **Client ID** and **Client Secret**

2. **Set environment variables:**
   ```bash
   # Add to your .env file or export directly
   export GOOGLE_CLIENT_ID="your_client_id_here"
   export GOOGLE_CLIENT_SECRET="your_client_secret_here"
   export BLOG_ID="your_blog_id_here"
   ```

3. **Use bloggerkit:**
   ```python
   from bloggerkit.client import BloggerClient
   
   # Simple initialization - uses environment variables automatically
   client = BloggerClient("your_blog_id")
   
   # Create a post
   post = client.create_post(
       title="My First Post",
       content="<p>Hello World!</p>",
       labels=["python", "blogging"],
       is_draft=False
   )
   print(f"✅ Post created: {post['url']}")
   ```

### Method 2: Traditional credentials.json (Still Supported)

```python
from bloggerkit.client import BloggerClient

client = BloggerClient(
    blog_id="your_blog_id",
    client_secrets_file="path/to/credentials.json"
)
```

### Method 3: Direct Parameters

```python
from bloggerkit.client import BloggerClient

client = BloggerClient(
    blog_id="your_blog_id",
    client_id="your_client_id",
    client_secret="your_client_secret"
)
```

## 📖 Usage Examples

### List Posts
```python
posts = client.list_posts()
if posts:
    for post in posts.items:
        print(f"📄 {post.title}: {post.url}")
```

### Create a Post
```python
# Basic post
new_post = client.create_post(
    title="My New Post",
    content="<p>This is my new blog post content.</p>"
)

# Advanced post with labels and draft mode
draft_post = client.create_post(
    title="Draft Post",
    content="<p>This is a draft post.</p>",
    labels=["draft", "work-in-progress"],
    is_draft=True
)
```

### Get a Specific Post
```python
post = client.get_post("POST_ID")
if post:
    print(f"📖 Title: {post.title}")
    print(f"🔗 URL: {post.url}")
    print(f"🏷️ Labels: {post.labels}")
```

### Update a Post
```python
updated_post = client.update_post(
    post_id="POST_ID",
    title="Updated Title",
    content="<p>Updated content goes here.</p>",
    labels=["updated", "python"]
)
```

### Delete a Post
```python
client.delete_post("POST_ID")
print("🗑️ Post deleted successfully!")
```

## 🔐 Authentication Flow

1. **First Run**: Browser opens for Google OAuth authentication
2. **Token Storage**: Creates `token.json` for future automatic authentication  
3. **Auto-refresh**: Automatically refreshes expired tokens
4. **Seamless Experience**: No manual intervention needed after initial setup

## 🔧 Configuration Priority

bloggerkit uses the following priority order for authentication:

1. **Direct Parameters** (`client_id`, `client_secret`)
2. **Environment Variables** (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`)
3. **Credentials File** (`client_secrets_file`)

## 🏷️ API Reference

### BloggerClient

```python
BloggerClient(
    blog_id: str,
    client_secrets_file: str = None,
    client_id: str = None,
    client_secret: str = None
)
```

### Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| `list_posts()` | Get all posts | None |
| `create_post()` | Create new post | `title`, `content`, `labels=None`, `is_draft=False` |
| `get_post()` | Get specific post | `post_id` |
| `update_post()` | Update existing post | `post_id`, `title`, `content`, `labels=None` |
| `delete_post()` | Delete post | `post_id` |

## 🔄 Migration Guide

### From v0.6.x to v0.7.0

**No changes required!** Your existing code works exactly the same:

```python
# This still works perfectly
client = BloggerClient(blog_id, client_secrets_file)
```

**Optional enhancement** - Simplify with environment variables:

```python
# Before (v0.6.x)
client = BloggerClient("blog_id", "credentials.json")

# After (v0.7.0) - Optional improvement
os.environ['GOOGLE_CLIENT_ID'] = 'your_id'
os.environ['GOOGLE_CLIENT_SECRET'] = 'your_secret'
client = BloggerClient("blog_id")  # Much cleaner!
```

## 🛠️ Development Setup

```bash
git clone https://github.com/StatPan/bloggerkit.git
cd bloggerkit
pip install -e .
```

## 📋 Requirements

- Python 3.10+
- Google Blogger API access
- OAuth 2.0 credentials

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Change Log

See [changelog.md](changelog.md) for detailed version history.

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- 📖 [Documentation](https://github.com/StatPan/bloggerkit)
- 🐛 [Issues](https://github.com/StatPan/bloggerkit/issues)
- 💬 [Discussions](https://github.com/StatPan/bloggerkit/discussions)

---

**Happy Blogging! 🚀📝**
