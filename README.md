# LastPerson07Bot - Premium Wallpaper Fetching Telegram Bot

![LastPerson07Bot Logo](https://via.placeholder.com/300x100/4CAF50/000000?text=LastPerson07Bot)

A beautiful, feature-rich Telegram bot that fetches high-quality wallpapers from multiple sources with premium features and stunning UI.

## 🌟 Features

### 🎨 Core Functionality

- **Multi-source Wallpaper Fetching**: Automatic fallback chain (Unsplash → Pexels → Pixabay)
- **Smart Image Validation**: Minimum 1920×1080 resolution with OpenCV
- **Automatic Reactions**: Bot sets random emoji reactions on all sent wallpapers
- **Category Support**: Browse by categories (nature, architecture, people, etc.)
- **Scheduled Posting**: Automatic wallpaper delivery to groups/channels

### 💎 Premium System

- **Free Tier**: 5 fetches/day with promotional buttons
- **Premium Tier**: Unlimited fetches, no ads, custom emoji support
- **Manual Premium**: Owner manually grants premium via /addpremium command
- **Beautiful Premium UI**: Stformatted upgrade process with custom emojis

### 🎮 Bot API 9.4 Features

- Custom emoji support in messages and buttons
- Button styling with icon_custom_emoji_id
- Message reactions with bot.set_message_reaction()
- Enhanced formatting and markdown support

### 🔧 Admin Tools

- **User Management**: Ban/unban, premium management, user statistics
- **Broadcast System**: Send messages to groups, channels, or DMs
- **API Management**: Add/remove wallpaper API endpoints
- **Maintenance Mode**: Toggle bot availability
- **Comprehensive Stats**: Database statistics with unicode formatting

### 🌟 Beautiful UI System

- **Stunning Messages**: Beautiful formatting with ASCII art and borders
- **Professional Design**: Consistent theme throughout all interactions
- **Interactive Elements**: Custom emoji reactions and styled buttons
- **Responsive Layout**: Optimized for mobile and desktop viewing

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Telegram Bot Token from @BotFather
- Optional: Docker & Docker Compose

### Installation

#### 1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/LastPerson07.git
cd LastPerson07
```

2. Set Up Environment

# Copy environment template

cp .env.example .env

# Edit .env with your configuration

nano .env 3. Install Dependencies

# Create virtual environment (recommended)

python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install requirements

pip install -r requirements.txt 4. Create Required Directories
mkdir logs data 5. Run the Bot
python app.py 6. With Docker (Recommended)

# Build and run with Docker Compose

docker-compose up -d

# View logs

docker-compose logs -f bot
📋 Commands
👤 User Commands
/start - Welcome message and bot overview
/fetch <category> - Get beautiful wallpapers
/categories - Browse all available categories
/premium - View premium plans and benefits
/myplan - Check your subscription status
/buy - Process premium subscription
/info - Bot information and statistics
/schedule <interval> <category> - Set automatic delivery
/help - Get help and usage instructions
/report <issue> - Report problems
/feedback <message> - Send thoughts to owner
👑 Admin Commands
/approve <id> - Approve pending requests
/logs - View recent bot logs
/ban <user_id> - Ban problematic users
/unban <user_id> - Unban users
/addpremium <user_id> [days] - Grant premium status
/removepremium <user_id> - Remove premium status
/users [page] [tier] - View user list with pagination
/stats - View comprehensive statistics
/maintenance on|off - Toggle maintenance mode
/db - Database statistics in unicode format
🏗️ Architecture
Project Structure
LastPerson07/
├── app.py # Main bot application
├── requirements.txt # Dependencies
├── .env.example # Environment template
├── README.md # Documentation
├── config/
│ └── config.py # Configuration management
├── db/
│ ├── **init**.py # Database package init
│ ├── client.py # MongoDB connection client
│ ├── models.py # Database models/schemas
│ └── queries.py # Database query operations
├── handlers/
│ ├── **init**.py # Handlers package init
│ ├── user_handlers.py # User command handlers
│ ├── admin_handlers.py # Admin command handlers
│ └── error_handler.py # Error handling module
├── utils/
│ ├── **init**.py # Utils package init
│ ├── ui.py # Beautiful UI templates
│ ├── reactions.py # Emoji reactions system
│ ├── fetcher.py # Wallpaper fetching logic
│ ├── scheduler.py # Task scheduling utilities
│ ├── promoter.py # User promotion utilities
│ ├── broadcaster.py # Broadcasting utilities
│ ├── stats.py # Statistics utilities
│ └── metadata.py # Image metadata processing
├── logs/ # Log files directory
├── Dockerfile # Docker container config
├── docker-compose.yml # Docker Compose setup
└── .gitignore # Git ignore file
Database Design
Collections
users: User data, premium status, statistics
api_urls: Wallpaper API configurations
schedules: Automatic posting schedules
bot_settings: Global bot configuration
logs: Event logging and monitoring
Component Relationships
app.py
├── utils/
│ ├── ui.py ←→ LastPerson07UI (templates)
│ ├── fetcher.py ←→ LastPerson07WallpaperFetcher
│ ├── reactions.py ←→ LastPerson07Reactions
│ └── metadata.py ←→ LastPerson07ImageProcessor
├── handlers/
│ ├── user_handlers.py ←→ UserHandlers
│ ├── admin_handlers.py ←→ AdminHandlers
│ └── error_handler.py ←→ ErrorHandler
└── db/
├── client.py ←→ LastPerson07DatabaseClient
├── models.py ←→ User, WallpaperInfo, PremiumPlan
└── queries.py ←→ LastPerson07Queries
🔧 Configuration
Environment Variables
Key variables you must set in .env:

# Required

TELEGRAM_TOKEN=your_bot_token
MONGODB_URI=mongodb://localhost:27017/lastperson07_bot

# Optional but Recommended

UNSPLASH_KEY=your_unsplash_key
PEXELS_KEY=your_pexels_key
PIXABAY_KEY=your_pixabay_key
OWNER_USERNAME=your_username
OWNER_USER_ID=123456789

# Premium Features

OWNER_HAS_PREMIUM=true
CUSTOM_EMOJI_ID=5478468873233959132
API Keys Setup
Unsplash: Sign up at https://unsplash.com/developers
Pexels: Get API key at https://www.pexels.com/api/
Pixabay: Register at https://pixabay.com/api/docs/
Telegram Bot: Create bot with @BotFather
💎 Premium System
Free Tier Features
5 wallpapers per day (UTC midnight reset)
Basic category browsing
Standard emoji reactions
Promotional buttons on wallpapers
Premium Features ($2/month)
✅ Unlimited wallpaper downloads
✅ No advertisements
✅ Custom emoji in captions
✅ Priority API access
✅ Advanced categories
✅ Download statistics
✅ Priority support
✅ Faster response times
Premium Activation Flow
User runs /buy or /premium
Bot shows beautiful purchase options
User contacts owner manually
Owner grants premium via /addpremium <user_id> [days]
🤖 Bot Behavior
Message Flow
Start: Beautiful welcome with interactive menu
Fetch: Validates limits → fetches wallpaper → adds reaction
Premium Flow: Beautiful upgrade process with multiple touchpoints
Error Handling: Graceful error recovery with user-friendly messages
Rate Limiting
Free Users: 5 fetches per day
Premium Users: Unlimited fetches
API Calls: Respects all API rate limits
Messages: Configurable per-minute limits
Content Filtering
All wallpapers automatically validated
Minimum 1920×1080 resolution
Content filter set to "high"
Safe mode enabled for all sources
🔍 Monitoring & Debugging
Logging Levels
INFO: Normal bot operation
WARNING: Non-critical issues
ERROR: Errors requiring attention
DEBUG: Detailed debugging information
Key Log Files
logs/bot.log: Main application log
Database logs stored in MongoDB
Error logs with full stack traces
Debug Mode
Enable by setting DEBUG=true in .env for detailed logging.

🐳 Docker Deployment
Quick Start with Docker

# Clone repository

git clone https://github.com/yourusername/LastPerson07.git
cd LastPerson07

# Copy environment

cp .env.example .env

# Edit .env with your configuration

# Run with Docker Compose

docker-compose up -d

# Scale up (optional)

docker-compose up -d --scale bot=3
Production Dockerfile Features
Python 3.11-slim base image
Security-focused user setup
Health checks for monitoring
Optimized for production use
Multi-stage build for smaller image size
Docker Compose Benefits
Automatic MongoDB setup
Volume persistence for data
Network isolation
Easy scaling and load balancing
Environment variable management
📊 API Integration
Supported Sources
Unsplash (Priority 1)
High-quality, artistic wallpapers
50 requests/hour rate limit
Pexels (Priority 2)

Free stock photography
200 requests/hour rate limit
Pixabay (Priority 3)

Royalty-free images
5,000 requests/hour rate limit
Fallback Strategy
try:
fetch from unsplash
except rate_limit:
try:
fetch from pexels
except rate_limit:
fetch from pixabay
except error:
use placeholder/demodata
🔄 Continuous Integration
GitHub Actions (Recommended)
name: CI/CD Pipeline

on:
push:
branches: [main]
pull_request:
branches: [main]

jobs:
test:
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v3 - name: Set up Python
uses: actions/setup-python@v4
with:
python-version: '3.11' - name: Install dependencies
run: pip install -r requirements.txt - name: Run tests
run: python -m pytest tests/ - name: Lint code
run: flake8 .

build:
needs: test
runs-on: ubuntu-latest
steps: - uses: actions/checkout@v3 - name: Build Docker image
run: docker build -t lastperson07bot . - name: Push to registry
run: docker push ${{ secrets.DOCKER_HUB_USERNAME }}/lastperson07bot
Testing Strategy
Unit tests for all core functions
Integration tests for database operations
E2E tests for critical user flows
Load testing for performance validation
🛡️ Security
Security Best Practices
Input validation on all user inputs
SQL injection prevention with Pydantic models
Rate limiting to prevent abuse
No hardcoded credentials
Secure MongoDB connection with authentication
Privacy Protection
No storage of personal messages
Minimal user data collection
Optional data deletion on request
GDPR compliance ready
Access Control
Admin-only commands with permission checks
Premium features gated behind subscription
Bot owner validation system
📈 Performance & Scaling
Performance Metrics
Response Time: <2 seconds for wallpaper fetch
Memory Usage: <512MB per bot instance
CPU Usage: <50% under normal load
Database Queries: Optimized with proper indexes
Scaling Options
Horizontal: Multiple bot instances with load balancer
Vertical: Increase server resources as needed
Database: MongoDB sharding for large user base
Caching: Redis for frequently accessed data
Optimization Techniques
Connection pooling for database operations
Async/await throughout the codebase
Image caching for repeated requests
Efficient data structures and algorithms
🤝 Contributing
How to Contribute
Fork the repository
Create a feature branch: git checkout -b feature/amazing-feature
Make your changes
Add tests if applicable
Commit your changes: git commit -m 'Add amazing feature'
Push to branch: git push origin feature/amazing-feature
Open a Pull Request
Development Guidelines
Follow the existing code style
Add comprehensive comments
Include tests for new features
Update documentation as needed
Ensure all tests pass
Code Style
Use Black for code formatting
Follow PEP 8 style guidelines
Type hints for all functions
Max line length 88 characters
📄 License
This project is licensed under the MIT License - see the LICENSE [blocked] file for details.

🙏 Support & Community
Get Help
GitHub Issues: Report bugs and feature requests
Telegram: @lastperson07_support for quick help
Documentation: Check the README and code comments
Community: Join our Telegram channel for discussions
Contributing Guidelines
Be respectful and constructive
Provide clear bug reports with reproduction steps
Follow the code style and testing requirements
Start discussions for major changes
Recognition
Top contributors will be featured in the bot
Special badges for community members
Annual report recognizing contributions
Built with ❤️ using python-telegram-bot v20.7+ and MongoDB

LastPerson07Bot - Making wallpapers beautiful, one fetch at a time! 🎨