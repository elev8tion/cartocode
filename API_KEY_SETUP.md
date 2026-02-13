# DeepSeek API Key Setup Guide

## 🎉 New Feature: Persistent API Key Storage

Your API key is now saved to a config file and will persist across server restarts!

---

## 📍 Config File Location

```
/Users/kcdacre8tor/.cartographer_config.json
```

---

## 🔧 Setup Instructions

### Option 1: Manual Setup (Recommended)

**Step 1: Edit the config file**
```bash
open ~/.cartographer_config.json
```

**Step 2: Replace the placeholder with your real API key**

Change this:
```json
{
  "api_key": "PASTE_YOUR_DEEPSEEK_API_KEY_HERE",
  "model": "deepseek-chat"
}
```

To this (with your actual key):
```json
{
  "api_key": "sk-abc123def456...",
  "model": "deepseek-chat"
}
```

**Step 3: Save the file**

**Step 4: Start (or restart) Cartographer**
```bash
python3 cartographer.py /path/to/your/project
```

You should see:
```
🔑 API key loaded from config file
```

**Step 5: Test it**
- Open browser to http://localhost:3000
- Click "💬 Chat with Codebase"
- Send a message - it should work without configuring!

---

### Option 2: Configure via UI (Also Works)

1. Start Cartographer
2. Open http://localhost:3000
3. Click "💬 Chat with Codebase"
4. Click "⚙️ Configure API Key"
5. Enter your DeepSeek API key
6. Key is **automatically saved** to the config file!
7. Next time you restart, it will load automatically

---

## 🔑 Get Your DeepSeek API Key

1. Go to https://platform.deepseek.com
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create New Key**
5. Copy the key (starts with `sk-...`)
6. Paste it into the config file or UI

---

## 📊 How It Works

### Priority Order

Cartographer checks for API key in this order:

1. **Environment Variable** (highest priority)
   ```bash
   export DEEPSEEK_API_KEY="sk-..."
   ```

2. **Config File** (second priority)
   ```
   ~/.cartographer_config.json
   ```

3. **UI Configuration** (saves to config file)

### When You Configure via UI:

```
You enter key → Server saves to config file → Key persists forever
```

### When You Start Server:

```
Server starts → Loads config file → API key available
```

---

## 🔒 Security

### ✅ Your API Key is Protected

1. **Not committed to git**
   - Added `.cartographer_config.json` to `.gitignore`
   - Even if you accidentally `git add .`, it won't be staged

2. **Stored in your home directory**
   - Location: `~/.cartographer_config.json`
   - Only you can access it (file permissions)

3. **Not exposed in browser**
   - Never sent to frontend
   - Only used on backend for API calls

### ⚠️ Keep Your Key Safe

- ❌ Don't share your config file
- ❌ Don't commit it to public repos
- ❌ Don't paste it in public forums
- ✅ Store it in `~/.cartographer_config.json` (already done)

---

## 🧪 Testing

### Test 1: Config File Loading

```bash
# Check if config file exists
ls -l ~/.cartographer_config.json

# View contents (hide key)
cat ~/.cartographer_config.json | grep -o '"api_key": "sk-[^"]*"' | sed 's/sk-.*/sk-***HIDDEN***"/'

# Start server
python3 cartographer.py /path/to/project

# Look for this line:
# 🔑 API key loaded from config file
```

### Test 2: Chat Functionality

```bash
# Server running? Open browser:
# http://localhost:3000

# 1. Click "💬 Chat with Codebase"
# 2. Send message: "What does this project do?"
# 3. Should get response WITHOUT configuring API key!
```

### Test 3: Persistence

```bash
# Restart server (Ctrl+C, then start again)
python3 cartographer.py /path/to/project

# Should still see:
# 🔑 API key loaded from config file

# Chat should still work without re-entering key
```

---

## 🔄 Model Selection

You can choose between two models in the config file:

```json
{
  "api_key": "sk-...",
  "model": "deepseek-chat"
}
```

**Options:**
- `"deepseek-chat"` - DeepSeek V3 (fast, cheap: $0.28/M tokens)
- `"deepseek-reasoner"` - DeepSeek R1 (reasoning, expensive: $2.19/M tokens)

**Default:** `deepseek-chat` (recommended)

You can also change this in the UI's model selector dropdown.

---

## 📝 Config File Format

```json
{
  "api_key": "sk-your-actual-key-here",
  "model": "deepseek-chat",
  "saved_at": "2026-02-12T16:37:00.123456"
}
```

**Fields:**
- `api_key` (required) - Your DeepSeek API key
- `model` (optional) - Default model to use
- `saved_at` (auto) - Timestamp when config was saved

---

## 🆘 Troubleshooting

### Issue: "API key not loaded"

**Check 1: File exists?**
```bash
ls -l ~/.cartographer_config.json
```

**Check 2: Valid JSON?**
```bash
python3 -c "import json; print(json.load(open('~/.cartographer_config.json'.replace('~', '$HOME'))))"
```

**Check 3: Has real key?**
```bash
grep "PASTE_YOUR" ~/.cartographer_config.json
# If this shows anything, you didn't replace the placeholder!
```

### Issue: "Still asking for API key"

Your key might still be the placeholder. Edit the file:
```bash
open ~/.cartographer_config.json
```

Replace `PASTE_YOUR_DEEPSEEK_API_KEY_HERE` with your real key.

### Issue: "Invalid API key"

Your key might be wrong. Get a new one:
1. Go to https://platform.deepseek.com
2. Create new API key
3. Update config file
4. Restart server

---

## 📚 Quick Reference

| Action | Command |
|--------|---------|
| View config | `cat ~/.cartographer_config.json` |
| Edit config | `open ~/.cartographer_config.json` |
| Test config | `python3 -c "import json; print(json.load(open('/Users/kcdacre8tor/.cartographer_config.json')))"` |
| Delete config | `rm ~/.cartographer_config.json` |
| Start server | `python3 cartographer.py /path/to/project` |

---

## ✅ Summary

**Before:**
- ❌ Had to enter API key every time
- ❌ Key stored in memory only
- ❌ Lost on server restart

**After:**
- ✅ Enter once, works forever
- ✅ Saved to config file
- ✅ Auto-loads on startup
- ✅ Secure (not committed to git)

---

**Your config file is ready at:**
```
/Users/kcdacre8tor/.cartographer_config.json
```

**Next step:** Edit that file and paste your DeepSeek API key!
