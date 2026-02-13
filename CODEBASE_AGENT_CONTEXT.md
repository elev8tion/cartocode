# ⚠️ CODEBASE RISK MAP — READ BEFORE MODIFYING

## 🔴 Critical Files (DO NOT modify without review)

- **cartographer.py** — Risk: 42.5/100 | Dependents: 0 | 🏷️ decorated 💾 data-model 📡 event-driven
- **cartographer_mcp.py** — Risk: 22.7/100 | Dependents: 0 | 🏷️ decorated

## 🟡 Binding Points

- `cartographer_mcp.py`: imports, decorators
- `cartographer.py`: imports, signals, decorators, db_models

## 🟢 Safe to Modify

- `test_config_endpoint.py` (risk: 0)
- `test_api_key_bug.py` (risk: 0)