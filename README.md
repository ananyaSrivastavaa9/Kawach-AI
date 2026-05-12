# 🛡️ Kawach AI - Fight Online Abuse

> A real-time Hindi/English/Hinglish Toxicity Detector powered by a custom multilingual dictionary.

![Kawach AI Dark Theme](https://img.shields.io/badge/Theme-Dark-black?style=for-the-badge)
![Language](https://img.shields.io/badge/Language-Python-blue?style=for-the-badge)
![Framework](https://img.shields.io/badge/Framework-Streamlit-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 🚀 Features

- **Multi-language**: English, Hindi (romanized), and Hinglish detection
- **Real-time scoring**: 0–100 toxicity score with color-coded classification
- **Trigger word highlighting**: See exactly which words flagged the content
- **Polite rewrite suggestions**: AI-generated cleaner alternatives
- **CSV batch analysis**: Process hundreds of comments at once
- **Interactive charts**: Plotly pie + bar charts for batch results
- **Download results**: Export analyzed CSV with score/label/triggers columns
- **Mobile-responsive**: Looks great on phones too

---

## 📦 Setup on Replit

### 1. Fork/Import this Repl

Click **Use Template** or import from GitHub.

### 2. Install Dependencies

Replit will auto-install from `requirements.txt`. If not, run:

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
streamlit run app.py
```

The app runs on **port 5000** by default.

---

## 🗂️ Project Structure

```
kawach-ai/
├── app.py              # Main Streamlit application
├── toxic_words.py      # Dictionary, scoring engine, rewrite logic
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── .streamlit/
    └── config.toml     # Streamlit dark theme config
```

---

## 📊 How Scoring Works

| Score Range | Label    | Color  |
|-------------|----------|--------|
| 0 – 24      | ✅ Safe    | Green  |
| 25 – 54     | ⚠️ Moderate | Yellow |
| 55 – 100    | 🚨 Toxic  | Red    |

**Formula:**
```
weighted_count = Σ(severity_weight × trigger_word)
score = (weighted_count / total_words) × 100 - positive_context_reduction
```

- High severity words → 3× weight
- Medium severity words → 1.5× weight
- Positive context words (not, sorry, please) → −5 points each

---

## 📋 CSV Format

Upload a CSV with a `comment` column:

```csv
comment
"This is a great post!"
"You are so stupid"
"Yaar kya bakwaas hai"
```

The app adds: `score`, `label`, `triggers`, `rewrite` columns and lets you download the result.

---

## 🛡️ Disclaimer

This tool uses a rule-based dictionary approach. It may:
- Miss context-dependent sarcasm or irony
- Produce false positives on technical/academic usage
- Not cover every slang variant

It is intended as a **first-pass filter**, not a legal or judicial tool.

---

## 🤝 Contributing

PRs welcome! To add more toxic words:
1. Edit `toxic_words.py`
2. Add to `ENGLISH_TOXIC`, `HINDI_TOXIC`, or `HINGLISH_TOXIC`
3. Optionally add to `HIGH_SEVERITY` or `MEDIUM_SEVERITY`

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

**Built with ❤️ | Open Source | Fight Hate, Spread Kindness**
