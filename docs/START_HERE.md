# 🎯 START HERE - Your First Analysis in 5 Minutes

## What This Is
A local AI tool that analyzes scientific papers against the **PRISMA 2020 checklist**, adapted for scoping reviews. Uses Ollama (local LLM) - no cloud, fully auditable.

## What You Need
- Python 3.10+ (already on your system ✓)
- Ollama + gemma4 model (setup below)
- Your PDF paper to analyze

## 🚀 Quick Start

### 1. One-Time Setup (2 min)
```bash
cd /home/andre/uni_repo/checklist_uni
source .venv/bin/activate
pip install -e .
```

### 2. Verify Installation (30 sec)
```bash
python3 tests/demo.py
# Should show beautiful formatted output
```

### 3. Setup Ollama (5 min)

**Open a NEW terminal and keep it running:**
```bash
ollama serve
```

**In another terminal (one-time):**
```bash
ollama pull gemma4:31b-cloud
```

### 4. Analyze Your Paper (in main terminal)
```bash
python3 cli.py /path/to/your_paper.pdf
```

**Example:**
```bash
python3 cli.py ~/Documents/my_research_paper.pdf
```

### 5. View Results
```bash
# Results automatically saved to:
open output/reports/*.md    # Beautiful report
cat output/reports/*.json   # Raw data
```

## 📊 What You're Analyzing

5 key PRISMA checklist items:
1. ✅ **Title** - Is it a scoping review?
2. ✅ **Abstract** - Methods + results summarized?
3. ✅ **Eligibility** - Inclusion/exclusion criteria stated?
4. ✅ **Search Strategy** - Databases + methods clear?
5. ✅ **Study Mapping** - Included studies characterized?

Each gets classified as:
- ✅ **presente** - Clearly there
- ⚠️ **parziale** - Partly there
- ❌ **assente** - Not found
- ⊘ **non_applicabile** - Not relevant
- ❓ **incerto** - Unclear

## 📁 Output: What You Get

### 1. Markdown Report (Human-Readable)
```markdown
# PRISMA 2020 Analysis

Document: your_paper.pdf (12 pages)

## Summary
✅ presente: 3 items
⚠️ parziale: 1 item
❌ assente: 1 item
...

## Item Details
✅ Title
Status: presente | Confidence: 95%

Evidence Found:
"Systematic Mapping of..."
Page: 1
Type: explicit (explicit statement in text)
```

### 2. JSON Report (Machine-Readable)
```json
{
  "document": "your_paper.pdf",
  "items": [
    {
      "item_id": "1",
      "title": "Title",
      "status": "presente",
      "evidence": ["quote from paper"],
      "page": 1
    }
  ]
}
```

## 🎯 Example Full Workflow

```bash
# Terminal 1: Start Ollama (keep running)
$ ollama serve
Listening on 127.0.0.1:11434

# Terminal 2: Download model (one-time)
$ ollama pull gemma4:31b-cloud
[Getting model...]
success

# Terminal 3: Analyze your paper
$ source .venv/bin/activate
$ python3 cli.py ~/Downloads/scoping_review.pdf

📖 Extracting PDF...
✓ 15 pages extracted

✂️ Chunking document...
✓ Created 12 chunks

🤖 Analyzing against PRISMA...
[Queries Ollama for each item...]

✓ Analysis complete!
📄 Reports saved:
  - output/reports/scoping_review_20260407_143022.json
  - output/reports/scoping_review_20260407_143022.md

$ # View beautiful report
$ open output/reports/scoping_review_*143022.md
```

## ⚡ Speed Tips

### Slow Analysis?
- First run queries Ollama 10 times (2 per item)
- This takes 4-6 minutes total (normal)
- Subsequent papers: same time per paper

### Faster Testing
```bash
# Analyze only first 2 items (instead of 5)
python3 cli.py paper.pdf --limit 2
```

## 🆘 Troubleshooting

### "Ollama not available"
→ Check Terminal 1: `ollama serve` must be running

### "Model not found"
→ Run: `ollama pull gemma4:31b-cloud` in Terminal 2

### "Python not in path"
→ Make sure venv is activated: `source .venv/bin/activate`

### PDF extraction fails
→ Make sure PDF has selectable text (not scanned image)

## 📚 Learn More

Want deeper dive?
- **QUICKSTART.md** - 30-second version (if you're in a hurry)
- **HOW_TO_RUN.md** - Detailed step-by-step commands
- **README_FULL.md** - Complete feature guide
- **SETUP.md** - Installation & troubleshooting

## 🎓 How It Works (Simple Version)

1. **Extract** - Reads PDF, extracts text
2. **Chunk** - Splits into manageable pieces (keeps track of page numbers)
3. **Query LLM** - For each PRISMA item:
   - "Find evidence for Item X in this text"
   - LLM finds quotes + page numbers
   - LLM classifies: presente/parziale/assente/etc.
4. **Report** - Generates beautiful report showing:
   - Each item's status
   - Evidence found (with page numbers)
   - Confidence scores
   - Suggestions for improvement

## ✨ Key Features

✅ **Local** - Everything runs on your computer
✅ **Auditable** - Every conclusion traces back to source text
✅ **Transparent** - Shows confidence + reasoning
✅ **Adapted** - PRISMA adapted for scoping reviews
✅ **Beautiful** - Readable Markdown + JSON output
✅ **Fast** - 4-6 minutes per paper

## 🚀 You're Ready!

The system is installed, tested, and ready to use.

**Next:** Follow the Quick Start above to analyze your first paper!

---

**Have questions?**
- Check the docs (QUICKSTART.md, HOW_TO_RUN.md, etc.)
- Look at example output from: `python3 tests/demo.py`
- Read code comments in `src/` if you're curious

**Happy analyzing!** 📊
