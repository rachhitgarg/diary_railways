# 🎓 AI Student Diary - Railway Deployment

**A comprehensive AI-powered diary application for Indian students (5th-12th standard) with intelligent analysis, mood tracking, and personalized insights.**

## 🚀 Features

- **📝 Smart Diary Writing**: Text-based diary entries with mood tracking
- **🤖 AI Analysis**: OpenAI-powered sentiment, emotion, and topic analysis
- **🧠 Knowledge Graph**: Neo4j-based relationship mapping of student experiences
- **🔍 Semantic Search**: Pinecone vector database for intelligent memory retrieval
- **🌅 Daily Reflections**: AI-generated personalized morning reflections
- **📊 Analytics Dashboard**: Mood trends, progress tracking, and insights
- **🇮🇳 Indian Context**: JEE, NEET, board exams, cultural festival awareness
- **🔒 Privacy-First**: Encrypted storage with user control

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **AI/ML**: OpenAI GPT-3.5, Text Embeddings
- **Vector DB**: Pinecone
- **Graph DB**: Neo4j Aura
- **Frontend**: HTML, CSS, JavaScript
- **Hosting**: Railway.app
- **Database**: PostgreSQL (Railway-managed)

## 📋 Prerequisites

Before deploying, you'll need accounts for:

1. **Railway.app** - Free tier ($5/month credit)
2. **OpenAI** - API access (~$1-5 for testing)
3. **Pinecone** - Free starter plan (1M vectors)
4. **Neo4j Aura** - Free tier (200k nodes)
5. **GitHub** - For repository hosting

## 🚀 Quick Deployment Guide

### Step 1: Create External Service Accounts

#### OpenAI Setup
1. Go to https://platform.openai.com/
2. Sign up and navigate to API keys
3. Create new secret key (starts with `sk-`)
4. Save the key securely

#### Pinecone Setup
1. Visit https://www.pinecone.io/
2. Sign up for free starter plan
3. Create new index:
   - Name: `student-diary-vectors`
   - Dimensions: `1536`
   - Metric: `cosine`
   - Region: `us-east-1` (or closest)
4. Note your API key from dashboard

#### Neo4j Aura Setup
1. Go to https://neo4j.com/aura/
2. Sign up and choose "AuraDB Free"
3. Create instance:
   - Name: `student-diary-graph`
   - Set a strong password
4. Note the connection URI (bolt://...) and password

### Step 2: Deploy to Railway

#### GitHub Repository Setup
1. Create new repository on GitHub named `ai-student-diary`
2. Make it public (required for Railway free tier)
3. Upload all files from this folder to the repository

#### Railway Deployment
1. Go to https://railway.app/
2. Sign up with GitHub account
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `ai-student-diary` repository
5. Railway will auto-detect and start building

#### Add Database
1. In Railway project dashboard
2. Click "New" → "Database" → "Add PostgreSQL"
3. Railway auto-provides `DATABASE_URL`

### Step 3: Configure Environment Variables

In Railway project settings → Variables tab, add:

```bash
# AI Services
OPENAI_API_KEY=sk-your-openai-key-here
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=student-diary-vectors

# Neo4j Database
NEO4J_URI=bolt://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password

# Security
SECRET_KEY=your-long-random-secret-key-here

# App Config
ENVIRONMENT=production
DEBUG=false
```

### Step 4: Test Deployment

1. Wait for Railway build to complete
2. Click on your deployment URL
3. Test the health endpoint: `https://yourapp.railway.app/health`
4. Access the web interface: `https://yourapp.railway.app/`
5. Try creating a diary entry to test AI integration

## 📁 Project Structure

```
ai-student-diary/
├── main.py                     # FastAPI app entry point
├── requirements.txt            # Python dependencies
├── railway.toml               # Railway configuration
├── Procfile                   # Process configuration
├── .env.example              # Environment variables template
├── app/
│   ├── __init__.py
│   ├── routers/              # API endpoints
│   │   ├── auth.py           # Authentication
│   │   ├── diary.py          # Diary management
│   │   └── analytics.py      # Analytics & insights
│   ├── services/             # External service integrations
│   │   ├── openai_service.py # OpenAI API integration
│   │   ├── pinecone_service.py # Vector database
│   │   └── neo4j_service.py  # Graph database
│   ├── core/                 # Core utilities
│   └── database/             # Database models
├── static/                   # Frontend files
│   ├── index.html           # Main web interface
│   ├── style.css            # Styling
│   └── app.js               # Frontend logic
└── README.md                # This file
```

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Current user info

### Diary Management
- `POST /api/v1/diary/entries` - Create diary entry
- `GET /api/v1/diary/entries` - List entries
- `GET /api/v1/diary/entries/{id}/analysis` - Get AI analysis
- `GET /api/v1/diary/reflection/daily` - Daily reflection

### Analytics
- `GET /api/v1/analytics/overview` - Analytics overview
- `GET /api/v1/analytics/mood-trends` - Mood trends
- `GET /api/v1/analytics/insights` - AI insights

### System
- `GET /health` - Health check
- `GET /docs` - API documentation

## 🧪 Testing the Application

### Manual Testing
1. **Health Check**: Visit `/health` endpoint
2. **Web Interface**: Access root URL
3. **Diary Entry**: Create a test entry
4. **AI Analysis**: Check if processing works
5. **Reflection**: Generate daily reflection
6. **Analytics**: View progress dashboard

### Test Data
Use these sample entries to test different scenarios:

**Positive Entry**:
```
Today was amazing! I finally understood calculus in math class. My teacher explained derivatives so clearly, and I solved all the practice problems. Feeling confident about the upcoming test!
```

**Stressed Entry**:
```
JEE preparation is getting overwhelming. Everyone seems to be studying 12 hours a day. My parents keep asking about my rank in mock tests. I'm trying my best but feel like it's never enough.
```

**Cultural Context**:
```
Diwali is next week and I'm excited to celebrate with family, but I also have physics practicals. Trying to balance festival preparations with studies. At least my cousins will be there!
```

## 🔒 Security & Privacy

- All diary entries are encrypted at rest
- API keys are server-side only
- User data is not shared without consent
- GDPR-compliant data handling
- Secure HTTPS connections
- Rate limiting on API endpoints

## 🐛 Troubleshooting

### Common Issues

**Build Fails on Railway**
- Check `requirements.txt` for correct dependencies
- Verify Python version compatibility
- Check Railway build logs for errors

**AI Services Not Working**
- Verify environment variables are set correctly
- Check API key validity and quotas
- Monitor service status pages

**Database Connection Issues**
- Confirm Neo4j instance is running
- Verify connection credentials
- Check network connectivity

**Frontend Not Loading**
- Ensure static files are in `/static` directory
- Check Railway deployment logs
- Verify CORS settings

### Debugging Commands

Check service health:
```bash
curl https://yourapp.railway.app/health
```

Test API endpoints:
```bash
curl -X POST https://yourapp.railway.app/api/v1/diary/entries \
  -H "Content-Type: application/json" \
  -d '{"content": "Test entry", "mood_score": 0.8}'
```

## 🚀 Production Considerations

### Scaling
- Railway auto-scales based on usage
- Consider upgrading plans for higher traffic
- Monitor resource usage in Railway dashboard

### Monitoring
- Set up Railway monitoring alerts
- Track API response times
- Monitor AI service usage and costs

### Backup
- Railway handles database backups automatically
- Consider exporting Neo4j data periodically
- Backup environment variables securely

## 📚 Future Enhancements

### Phase 1 Features
- [ ] User authentication (JWT)
- [ ] Voice diary entries (Whisper)
- [ ] Image attachments with analysis
- [ ] Crisis detection alerts
- [ ] Parent/counselor dashboard

### Phase 2 Features
- [ ] Career guidance recommendations
- [ ] Study pattern optimization
- [ ] Anonymous peer support network
- [ ] Mobile app (React Native)
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: API docs at `/docs` endpoint
- **Issues**: GitHub Issues tab
- **Email**: [Your support email]

## 🎯 Mission

Empowering Indian students with AI-driven insights to navigate academic pressure, build emotional resilience, and achieve personal growth through reflective writing.

---

**Built with ❤️ for Indian students facing academic challenges**

🚀 **Your AI Student Diary is ready to deploy!**
