# 🌐 Remote Ollama Configuration Guide

Guida per usare il PRISMA Analyzer con Ollama remoto/cloud.

## 📋 Setup Remoto

### Opzione 1: Via File `.env` (Consigliato)

```bash
# 1. Copia il template
cp .env.example .env

# 2. Modifica .env con dati remoti
nano .env
```

**File `.env`:**
```env
# Ollama Server Configuration
OLLAMA_BASE_URL=https://your-ollama-cloud.example.com
OLLAMA_MODEL=gemma4:31b-cloud
OLLAMA_API_KEY=your_api_key_here_sk_xxx
```

**Poi analizza normalmente:**
```bash
python3 cli.py your_paper.pdf
# Usa automaticamente i dati da .env
```

---

### Opzione 2: Via Linea di Comando

```bash
python3 cli.py your_paper.pdf \
  --url https://your-ollama-cloud.example.com \
  --api-key your_api_key_here
```

---

### Opzione 3: Variabili d'Ambiente

```bash
export OLLAMA_BASE_URL=https://your-cloud.com
export OLLAMA_MODEL=gemma4:31b-cloud
export OLLAMA_API_KEY=your_key_here

python3 cli.py your_paper.pdf
```

---

## 📍 Dove Ottenere Chiave API

### Se usi Ollama Cloud Providers:

**Replicate:**
```
https://api.replicate.com/v1
API Key: r8_xxxxxxxxxxxxx
```

**Together AI:**
```
https://api.together.xyz/v1
API Key: your-api-key
```

**Anyscale (LLM API):**
```
https://api.anyscale.com/v1
API Key: eseckey_xxxxx
```

### Domanda: Come verificare che la chiave funziona?

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-ollama-url/api/tags
```

Se vedi la lista di modelli: ✓ OK
Se errore 401: ✗ Chiave non valida

---

## 🔄 Uso Locale vs Remoto

### LOCALE (Default)
```bash
# .env:
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:31b-cloud
# (no API key needed)

# Comando:
python3 cli.py paper.pdf
```

### REMOTO (Cloud)
```bash
# .env:
OLLAMA_BASE_URL=https://api.provider.com
OLLAMA_MODEL=gemma4:31b-cloud
OLLAMA_API_KEY=sk_xxx...

# Comando:
python3 cli.py paper.pdf
# OR con override:
python3 cli.py paper.pdf --url https://api.provider.com --api-key sk_xxx
```

---

## 🧪 Test Connessione

### Verifica che il server risponde:

```bash
curl \
  -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-ollama-url/api/tags
```

### Output di successo:
```json
{
  "models": [
    {
      "name": "gemma4:31b-cloud",
      "modified_at": "2026-04-07T10:00:00Z"
    }
  ]
}
```

### Output di errore:
```json
{"error": "Unauthorized"}
```
→ Controlla la chiave API

---

## ⚡ Performance Con Remoto

- **Tempo di risposta:** Dipende dalla velocity del provider
- **Costo:** Varia a seconda del provider
- **Affidabilità:** Dipende da SLA del provider

### Tipiche latenze:
- Locale (Ollama sul PC): 3-5 min per 5 items
- Cloud (API remota): 2-4 min per 5 items (spesso più veloce!)

---

## 🔐 Sicurezza

### ⚠️ Best Practices

1. **Non salvare chiavi nel codice**
   ```bash
   # ✗ NO:
   python3 cli.py paper.pdf --api-key sk_xxx

   # ✓ SÍ:
   export OLLAMA_API_KEY=sk_xxx
   python3 cli.py paper.pdf
   ```

2. **Usa .env file (mai committare)**
   ```bash
   # .gitignore:
   .env
   .env.local
   *.key
   ```

3. **Ruota chiavi periodicamente**
   - Se esposta: regenera immediatamente
   - Buona pratica: ogni 30 giorni

4. **Usa HTTPS (mai HTTP)**
   ```env
   # ✓ Corretto:
   OLLAMA_BASE_URL=https://api.provider.com
   
   # ✗ Non usare:
   OLLAMA_BASE_URL=http://unsecure.com
   ```

---

## 🆘 Troubleshooting

### Errore: "Ollama not available at https://..."

**Cause possibili:**
1. URL errato
2. Chiave API errata/scaduta
3. Server remoto down

**Soluzione:**
```bash
# Test URL direttamente:
curl -H "Authorization: Bearer YOUR_KEY" https://your-url/api/tags
```

### Errore: "401 Unauthorized"

**Causa:** Chiave API non valida

**Soluzione:**
```bash
# Verifica chiave:
echo $OLLAMA_API_KEY
# Rigenerala sul provider
# Aggiorna .env
```

### Errore: "Connection timeout"

**Causa:** Server remoto lento o irraggiungibile

**Soluzione:**
```bash
# Prova di ping:
curl -I https://your-url/api/tags

# Aumenta timeout in src/llm_engine/ollama_client.py:
timeout=120  # da 120 secondi
```

### Errore: "Model not found"

**Causa:** Modello non disponibile su server remoto

**Soluzione:**
```bash
# Lista modelli disponibili:
curl -H "Authorization: Bearer YOUR_KEY" \
  https://your-url/api/tags

# Aggiorna OLLAMA_MODEL in .env con uno disponibile
```

---

## 📊 Esempio Completo: Remoto

```bash
# 1. Copia config template
cp .env.example .env

# 2. Modifica .env con dati remoti
cat > .env << EOF
OLLAMA_BASE_URL=https://api.together.xyz/v1
OLLAMA_MODEL=mistral-7b
OLLAMA_API_KEY=$(cat ~/.ollama-api-key)
EOF

# 3. Verifica connessione
curl -H "Authorization: Bearer $(grep OLLAMA_API_KEY .env | cut -d= -f2)" \
  https://api.together.xyz/v1/api/tags

# 4. Analizza
source .venv/bin/activate
python3 cli.py ~/Documents/my_paper.pdf

# 5. Risultati
open output/reports/my_paper_*.md
```

---

## 🎯 Cheat Sheet

```bash
# LOCALE (default)
python3 cli.py paper.pdf

# REMOTO (via .env)
# 1. Modifica .env
# 2. python3 cli.py paper.pdf

# REMOTO (via CLI)
python3 cli.py paper.pdf \
  --url https://api.xxx.com \
  --api-key sk_xxxx

# REMOTO (via env vars)
export OLLAMA_BASE_URL=https://api.xxx.com
export OLLAMA_API_KEY=sk_xxxx
python3 cli.py paper.pdf

# Test connessione
curl -H "Authorization: Bearer YOUR_KEY" https://your-url/api/tags

# Visualizza config attuale
grep OLLAMA .env
```

---

## 📞 Provider Raccomandati

### Ollama Cloud Services

**Replicate.com**
- URL: https://api.replicate.com/v1
- Modelli: Vari (incluso gemma, mistral)
- Prezzo: Pay-as-you-go

**Together AI**
- URL: https://api.together.xyz/v1
- Modelli: Vari LLM open-source
- Prezzo: Economico

**Anyscale**
- URL: https://api.anyscale.com/v1
- Modelli: Llama, Mistral community
- Prezzo: Competitivo

---

**Domande? Controlla:**
- `.env.example` per template
- Logs in `output/logs/` per debug
- README_FULL.md per overview generale
