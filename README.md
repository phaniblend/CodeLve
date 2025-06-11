# codElve - A local AI-powered tool to analyze and explain entire codebases across any framework, fully offline &amp; private.
# 🧠 codElve – Your Offline AI Codebase Companion

Ever wished you had a senior engineer to walk you through a messy codebase?  
**codElve** does just that — using local LLMs and some smart logic to help you understand, navigate, and analyze code across any stack.

This tool runs entirely **on your machine** — no cloud, no uploads, no risk.  
Great for work projects, client code, or just keeping things private.

---

## ⚙️ What codElve Does

- Understands your codebase — React, Python, Java, etc.
- Explains services, components, and modules like a tech lead would
- Generates code walkthroughs and architecture summaries
- Finds relevant business logic, APIs, and workflows
- All powered by **local models** — nothing leaves your machine

---

## 🛠 Setup

You’ll need:

- Python 3.8+
- `torch`, `transformers`, and standard Python packages
- A couple of open-source models downloaded locally (see below)

---

## 📥 Model Setup

codElve uses two Hugging Face models for offline code analysis and fallback responses:

| Model             | Purpose                        | Download Link                                          | Expected Path                                                 |
|------------------|----------------------------------|-------------------------------------------------------|---------------------------------------------------------------|
| `codet5p-770m`   | Primary code analysis/generation | [Salesforce/codet5p-770m](https://huggingface.co/Salesforce/codet5p-770m) | `E:\projects\Projects_self\codElve-python\models\codet5p-770m` |
| `dialogpt-small` | Conversational fallback model    | [microsoft/DialoGPT-small](https://huggingface.co/microsoft/DialoGPT-small) | `E:\projects\Projects_self\codElve-python\models\dialogpt-small` |

> ⚠️ **Note to Collaborators:** These models are currently used for **testing and prototyping**.  
> We’re actively working on replacing them with a **compact and higher-quality model like [TinyLlama](https://huggingface.co/cognitivecomputations/TinyLlama-1.1B-Chat-v1.0)** to improve performance and reduce resource usage.

### 📦 How to Download

**Option A: Using Git LFS**
```bash
git lfs install
git clone https://huggingface.co/Salesforce/codet5p-770m
git clone https://huggingface.co/microsoft/DialoGPT-small