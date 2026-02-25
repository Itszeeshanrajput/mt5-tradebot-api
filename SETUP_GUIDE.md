# 🚀 Quick Setup Guide - MT5-TradeBot API

Get up and running in **5 minutes**!

## ✅ Prerequisites Checklist

Before starting, make sure you have:
- [ ] Windows OS (MT5 requirement)
- [ ] Python 3.8+ installed
- [ ] MetaTrader 5 installed
- [ ] MT5 demo/live account credentials
- [ ] Internet connection

---

## 📥 Step 1: Download the Project

### Option A: Download ZIP (Easiest)
1. Click the green **"Code"** button on GitHub
2. Select **"Download ZIP"**
3. Extract to: `C:\MT5-TradeBot`

### Option B: Clone with Git
```bash
git clone https://github.com/yourusername/mt5-tradebot-api.git
cd mt5-tradebot-api
```

---

## 🔧 Step 2: Install Python Dependencies

Open **Command Prompt** in the project folder:

```bash
# Navigate to project folder
cd C:\MT5-TradeBot

# Install all required packages
pip install -r requirements.txt
```

**Wait for installation to complete** (1-2 minutes)

---

## ⚙️ Step 3: Configure MT5 Credentials

### Find Your MT5 Credentials

Open MetaTrader 5 and note:
1. **Login:** Your account number (e.g., 262323581)
2. **Password:** Your account password
3. **Server:** Server name (e.g., Exness-MT5Trial16)

### Create Configuration File

1. Find file: `.env.example`
2. **Copy** it and rename to: `.env`
3. Open `.env` with Notepad
4. Fill in your details:

```env
MT5_LOGIN=262323581
MT5_PASSWORD=YourPassword123
MT5_SERVER=Exness-MT5Trial16
MT5_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
API_HOST=0.0.0.0
API_PORT=8001
LOG_LEVEL=INFO
```

5. **Save** the file

---

## 🎯 Step 4: Start the API Server

### Method 1: Using Batch File (Windows)
Double-click: `start_api.bat`

### Method 2: Using Command Line
```bash
python main.py
```

### You Should See:
```
INFO:     Started server process [7284]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**✅ Success!** The server is running.

---

## 🧪 Step 5: Test the Connection

### Open Interactive Documentation
1. Open your browser
2. Go to: **http://localhost:8001/docs**
3. You'll see the Swagger UI

### Test Health Check
1. Find: `GET /api/v1/health`
2. Click **"Try it out"**
3. Click **"Execute"**
4. Should return: `{"status": "healthy"}`

### Connect to MT5
1. Find: `POST /api/v1/connect`
2. Click **"Try it out"**
3. Enter your credentials:
```json
{
  "login": 262323581,
  "password": "YourPassword123",
  "server": "Exness-MT5Trial16"
}
```
4. Click **"Execute"**
5. Should return your account info!

---

## 🎉 You're All Set!

### What's Next?

**For Beginners:**
- Read: `BEGINNER_GUIDE.md`
- Try the examples in the docs
- Start with demo account

**For Developers:**
- Check: `GITHUB_README.md`
- Explore API endpoints
- Run backtests

**Quick Links:**
- 📖 API Docs: http://localhost:8001/docs
- 📚 Beginner Guide: `BEGINNER_GUIDE.md`
- 🚀 Quick Start: `QUICKSTART.md`
- 📊 Examples: `test_client.py`

---

## ❌ Troubleshooting

### "Python not found"
**Solution:** Install Python from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation

### "MT5 initialization failed"
**Solutions:**
1. Ensure MT5 is installed
2. Check credentials in `.env`
3. Make sure MT5 terminal is running
4. Verify server name is correct

### "Port 8001 already in use"
**Solution:** Change port in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8002)
```

### "Module not found"
**Solution:** Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

### "Symbol not found"
**Solution:** 
1. Check available symbols: `GET /api/v1/symbols`
2. Different brokers use different names
3. Try: "EURUSD", "EURUSDm", or "EURUSD.m"

---

## 🆘 Still Having Issues?

1. Check the full README.md
2. Read BEGINNER_GUIDE.md
3. Search existing GitHub Issues
4. Create a new Issue with:
   - Error message
   - What you tried
   - Your environment details

---

## 📞 Support

- 📖 Documentation: Check all .md files
- 💬 GitHub Issues: Report bugs/ask questions
- 📧 Email: your.email@example.com

---

**Happy Trading! 🚀**

Remember: Always use a **demo account** for testing!
