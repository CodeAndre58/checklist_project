# 🚀 Quick Start: Remote Ollama Setup

**Tempo stimato:** 5 minuti

---

## Step 1️⃣: Prepara le Credenziali Cloud

Ottieni i dati dal tuo provider Ollama:

```
Provider URL:    https://api.example.com
API Key:         sk_your_key_here_long_string
Model Name:      gemma4:31b-cloud (o quello che usi)
```

**Provider Consigliati:**
- **Replicate.com** - https://api.replicate.com/v1
- **Together AI** - https://api.together.xyz/v1
- **Anyscale** - https://api.anyscale.com/v1

---

## Step 2️⃣: Configura il File .env

```bash
# Copia il template
cp .env.example .env

# Apri e modifica
nano .env
```

**Contenuto di .env (remoto):**
```env
OLLAMA_BASE_URL=https://api.provider.com
OLLAMA_MODEL=gemma4:31b-cloud
OLLAMA_API_KEY=sk_your_key_here_long_string
```

**Salva:** Ctrl+O, Invio, Ctrl+X

---

## Step 3️⃣: Test Connessione

```bash
# Attiva virtualenv (se non già fatto)
source .venv/bin/activate

# Testa
python3 test_remote.py
```

**Output di successo:**
```
✅ All tests passed! Remote Ollama is ready to use.
```

**Output di errore?**
→ Vedi sezione "Troubleshooting" sotto

---

## Step 4️⃣: Analizza il Primo Paper

```bash
# Se hai un PDF
python3 cli.py your_paper.pdf

# O se hai un TXT
python3 cli.py your_paper.txt

# Visualizza risultati
ls output/reports/
cat output/reports/your_paper_*.md
```

---

## ⚡ Comandi Rapidi

```bash
# Setup da zero
git clone <repo>
cd checklist_uni
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configura remoto
cp .env.example .env
nano .env  # Inserisci credenziali

# Test
python3 test_remote.py

# Analizza
python3 cli.py paper.pdf

# Risultati in:
output/reports/paper_*.md
```

---

## 🔧 Alternative (senza .env)

### Via CLI Arguments
```bash
python3 cli.py paper.pdf \
  --url https://api.provider.com \
  --api-key sk_your_key
```

### Via Env Variables
```bash
export OLLAMA_BASE_URL=https://api.provider.com
export OLLAMA_MODEL=gemma4:31b-cloud
export OLLAMA_API_KEY=sk_your_key

python3 cli.py paper.pdf
```

---

## 🆘 Troubleshooting Rapido

### ❌ "Connection refused"
```bash
# Verifica URL:
curl https://api.provider.com/api/tags

# Controlla che non sia HTTP (dovrebbe essere HTTPS)
```

### ❌ "401 Unauthorized"
```bash
# Chiave API errata o scaduta
# Rigenerala sul provider
# Aggiorna .env e testa di nuovo
```

### ❌ "Model not found"
```bash
# Il modello non esiste su quel server
# Lista modelli disponibili:
curl -H "Authorization: Bearer YOUR_KEY" \
  https://api.provider.com/api/tags
```

### ❌ "Timeout"
```bash
# Server remoto lento
# Attendi qualche secondo e ritenta
# O aumenta timeout in src/llm_engine/ollama_client.py
```

---

## ✅ Verifica Setup

Il sistema è pronto quando:
1. ✓ `.env` contiene OLLAMA_BASE_URL valido
2. ✓ `.env` contiene OLLAMA_API_KEY valido
3. ✓ `python3 test_remote.py` passa (✅ All tests passed!)
4. ✓ `python3 cli.py test_paper.pdf` genera report

---

## 📚 Documentazione Completa

Per dettagli: vedi **REMOTE_OLLAMA.md**

Per overview generale: vedi **README_FULL.md**

---

**Pronto? Inizia con:**
```bash
python3 test_remote.py
```

Se tutto è ✓, allora analizza il tuo primo paper!
