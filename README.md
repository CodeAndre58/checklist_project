# 🎯 PRISMA 2020 Scoping Review Analyzer - MVP v0.1

**Status:** ✅ **COMPLETE & READY TO USE**

---

## 🚀 NEW HERE? START HERE!

### 🌐 Using Remote Ollama (Cloud/API) - RECOMMENDED

```bash
# 1. Copy config template
cp .env.example .env

# 2. Edit with your cloud credentials
nano .env
# OLLAMA_BASE_URL=https://your-provider-url
# OLLAMA_API_KEY=your_api_key_here

# 3. Test connection
python3 test_remote.py

# 4. Analyze your paper
python3 cli.py your_paper.pdf

# 5. View results
open output/reports/*.md
```

👉 **Quick setup (5 min):** See [docs/QUICKSTART_REMOTE.md](docs/QUICKSTART_REMOTE.md)  
👉 **Detailed guide (all providers):** See [docs/REMOTE_OLLAMA.md](docs/REMOTE_OLLAMA.md)

---

### 💻 Using Local Ollama (Alternative)

```bash
# 1. Start Ollama (Terminal A - keep running)
ollama serve

# 2. Download model (Terminal B - one-time)
ollama pull gemma4:31b-cloud

# 3. Verify setup
python3 tests/demo.py

# 4. Analyze your PDF (Main terminal)
python3 cli.py your_paper.pdf

# 5. View results
open output/reports/*.md
```

👉 **Local setup instructions:** See [docs/START_HERE.md](docs/START_HERE.md)

---

## 📚 Documentation