# 🆘 Troubleshooting: Remote Ollama Connection Issues

---

## ⚡ Quick Diagnostics

Run this first:
```bash
python3 test_remote.py
```

**If it says ✅ All tests passed:** → Skip to [Analysis](#-analyze-your-first-paper)

**If it fails:** → See section below matching your error

---

## 🔴 Common Issues & Fixes

### Issue: "Connection refused" or "Cannot connect to server"

**Cause:** URL is wrong or server is down

**Check:**
```bash
# 1. Verify URL format (HTTPS, no trailing slash)
grep OLLAMA_BASE_URL .env
# Should look like: https://api.provider.com (not http://)

# 2. Test URL directly
curl https://your-url/api/tags

# 3. Check if .env exists
ls -la .env
```

**Fix:**
```bash
# Re-copy template and fill carefully
cp .env.example .env
nano .env

# Make sure your URL is valid:
OLLAMA_BASE_URL=https://api.together.xyz    # ✓ Correct
OLLAMA_BASE_URL=http://api.together.xyz     # ✗ Wrong (use https://)
OLLAMA_BASE_URL=localhost:11434              # ✗ Wrong (if remote)
```

---

### Issue: "401 Unauthorized" or "Unauthorized"

**Cause:** API key is invalid, expired, or wrong format

**Check:**
```bash
# 1. Verify API key exists in .env
grep OLLAMA_API_KEY .env

# 2. Test API key manually
curl -H "Authorization: Bearer YOUR_KEY_HERE" \
  https://your-url/api/tags

# If you see: {"error": "Unauthorized"}
#   → API key is invalid
```

**Fix:**
```bash
# 1. Go to your provider dashboard
# 2. Generate a NEW API key
# 3. Copy it exactly (no extra spaces)
# 4. Update .env

nano .env
# Replace: OLLAMA_API_KEY=YOUR_NEW_KEY_HERE

# 5. Test again
python3 test_remote.py
```

---

### Issue: "Model not found" or "Model 'gemma4:31b-cloud' not available"

**Cause:** Model doesn't exist on this server or is named differently

**Check:**
```bash
# List available models on your server
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-url/api/tags
```

**Output example:**
```json
{
  "models": [
    {"name": "mistral-7b"},
    {"name": "llama2"},
    {"name": "neural-chat"}
  ]
}
```

**Fix:**
```bash
# 1. Pick a model from the list above (e.g., "mistral-7b")
# 2. Update .env

nano .env
# Change: OLLAMA_MODEL=mistral-7b

# 3. Test again
python3 test_remote.py
```

---

### Issue: "Timeout" or "Request timed out after 120 seconds"

**Cause:** Server is very slow or network is slow

**Check:**
```bash
# Test response time
time curl https://your-url/api/tags

# Should respond in < 2 seconds
# If > 5 seconds: server is slow
```

**Fix (Options):**

**Option 1: Wait (server may be overloaded)**
```bash
# Simple retry
python3 test_remote.py

# Or wait 5 minutes and try again
```

**Option 2: Switch to faster provider**
- Together AI (usually fast)
- Replicate (usually responsive)
- Increase timeout in code (advanced)

**Option 3: Increase timeout in code**
```python
# Edit src/llm_engine/ollama_client.py
# Find: timeout=120
# Change to: timeout=300  (5 minutes instead of 2)
```

---

### Issue: Test passes but analysis fails with "Connection Error"

**Cause:** Network connection lost during long analysis, or server restarted

**Check:**
```bash
# Network OK?
ping google.com

# Server still up?
python3 test_remote.py
```

**Fix:**
```bash
# Retry analysis on smaller file first
python3 cli.py small_paper.txt --limit 1

# If that works, try full paper
python3 cli.py your_paper.pdf
```

---

### Issue: "PRISMA config not found" or "prisma_2020.yaml missing"

**Cause:** File is in wrong location

**Check:**
```bash
ls src/checklist_engine/prisma_2020.yaml
```

**Fix:**
```bash
# Make sure you're in the right directory
pwd
# Should be: /home/andre/uni_repo/checklist_uni

# If not, navigate there
cd /home/andre/uni_repo/checklist_uni

# Verify files exist
ls src/checklist_engine/
# Should see: prisma_2020.yaml, analyzer.py, models.py, etc.
```

---

### Issue: "Permission denied" when running script

**Cause:** Script isn't executable, or Python isn't found

**Fix:**
```bash
# Make sure Python 3 is installed
python3 --version
# Should show: Python 3.10.x or higher

# Make scripts executable
chmod +x cli.py
chmod +x test_remote.py

# Try running again
python3 cli.py paper.pdf
```

---

### Issue: "FileNotFoundError: paper.pdf" or "No such file"

**Cause:** File path is wrong or file doesn't exist

**Fix:**
```bash
# Make sure file exists
ls your_paper.pdf

# Or use absolute path
python3 cli.py /full/path/to/your_paper.pdf

# Or use relative path correctly
cd /directory/containing/paper/
python3 /full/path/to/cli.py your_paper.pdf
```

---

### Issue: Virtual environment not activated

**Cause:** Missing dependencies because venv not activated

**Check:**
```bash
which python3
# Should show: /home/andre/uni_repo/checklist_uni/.venv/bin/python3
# If it shows: /usr/bin/python3 → venv not active
```

**Fix:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Check again
which python3
# Should now show: .../venv/bin/python3

# Now try running
python3 cli.py paper.pdf
```

---

## 🧪 Step-by-Step Diagnostic

Run these in order:

```bash
# 1. Check Python
python3 --version
# Expected: Python 3.10+

# 2. Check venv active
which python3
# Expected: */checklist_uni/.venv/bin/python3

# 3. Check .env exists
ls -la .env
# Should show file size > 0

# 4. Check .env content
grep OLLAMA .env
# Should show 3 lines (URL, MODEL, KEY)

# 5. Quick import test
python3 -c "from src.llm_engine.ollama_client import OllamaClient; print('✓')"
# Should print: ✓

# 6. Test remote connectivity
python3 test_remote.py
# Should show: ✅ All tests passed!

# 7. Test full analysis
python3 cli.py test_paper.txt --limit 1
# Should generate report
```

---

## 📋 Verification Checklist

Before asking for help, verify:

- [ ] `python3 --version` shows 3.10+
- [ ] `which python3` shows `.../venv/bin/python3`
- [ ] `.env` file exists and contains OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_API_KEY
- [ ] `.env` values don't have quotes around them
- [ ] OLLAMA_BASE_URL starts with `https://` (not http)
- [ ] OLLAMA_API_KEY is from your provider (not placeholder)
- [ ] `python3 test_remote.py` passes (shows ✅)
- [ ] `python3 -c "import requests; print('OK')"` works
- [ ] Firewall/proxy allows https:// outbound connections

---

## 🌐 Provider-Specific Issues

### Together AI (api.together.xyz)

**Common issue:** API key has wrong format

```bash
# Correct format:
# api_key = "3e0xxxxxxxxxxxxx"

# In .env:
OLLAMA_API_KEY=3e0xxxxxxxxxxxxx

# Test:
curl -H "Authorization: Bearer 3e0xxxxxxxxxxxxx" \
  https://api.together.xyz/v1/api/tags
```

### Replicate (api.replicate.com)

**Common issue:** Model name is different

```bash
# Check available models:
curl -H "Authorization: Bearer YOUR_KEY" \
  https://api.replicate.com/v1/models

# Might need to use full path:
OLLAMA_MODEL=meta/llama-2-7b
```

### Local Ollama (localhost:11434)

**Common issue:** Ollama not running

```bash
# Start Ollama in separate terminal:
ollama serve

# Then in main terminal:
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_API_KEY=  # Leave empty for local

python3 test_remote.py
```

---

## 🔍 Check Logs

When something fails, check the logs:

```bash
# List recent logs
ls -la output/logs/

# View last log
tail output/logs/checklist_analysis*.log

# View with timestamps
tail -f output/logs/checklist_analysis*.log
```

Logs show detailed error messages and help debug.

---

## 📞 Need More Help?

1. **Check full documentation:** See `REMOTE_OLLAMA.md`
2. **Check project status:** See `PROJECT_STATUS.md`
3. **Check quick start:** See `QUICKSTART_REMOTE.md`
4. **Enable verbosity:**
   ```bash
   export LOGLEVEL=DEBUG
   python3 test_remote.py
   ```

---

## ✨ Still Stuck?

Collect this info:

```bash
# Run diagnostic
echo "=== Python ===" && python3 --version
echo "=== Venv ===" && which python3
echo "=== Config ===" && cat .env | head -3
echo "=== Connectivity ===" && python3 test_remote.py 2>&1
echo "=== Imports ===" && python3 -c "from src.llm_engine.ollama_client import OllamaClient; print('OK')" 2>&1
```

Share the output above when asking for help.

---

**Most issues resolve by:**
1. Using correct HTTPS URL (not http)
2. Using valid API key from provider
3. Ensuring model exists on remote server
4. Activating virtual environment before running
5. Checking logs for detailed error messages
