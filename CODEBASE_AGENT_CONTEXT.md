# ⚠️ CODEBASE RISK MAP — READ BEFORE MODIFYING

## 🔴 Critical Files (DO NOT modify without review)

- **cartographer.py** — Risk: 81.3/100 | Dependents: 1 | 🏷️ decorated 📡 event-driven 💾 data-model
- **ui_enhancements.py** — Risk: 52.7/100 | Dependents: 1 | 🏷️ decorated
- **test_deepseek_system.py** — Risk: 23.299999999999997/100 | Dependents: 0 | 🏷️ decorated ⚙️ config-dependent 🌐 api-endpoint 💾 data-model 🧪 test
- **test_system_integration.py** — Risk: 22.299999999999997/100 | Dependents: 0 | ⚙️ config-dependent 🧪 test
- **test_multi_project_chat.py** — Risk: 22.1/100 | Dependents: 0 | 🏷️ decorated ⚙️ config-dependent 🌐 api-endpoint 💾 data-model 🧪 test

## 🟡 Binding Points

- `test_optimizations.py`: imports
- `test_system_integration.py`: imports, env_vars
- `test_multi_project_chat.py`: decorators, api_endpoints, env_vars, db_models, imports
- `cartographer.py`: imports, decorators, db_models, signals
- `test_deepseek_system.py`: decorators, api_endpoints, env_vars, db_models, imports
- `validate_test_suite.py`: imports
- `ui_enhancements.py`: imports, decorators

## 🟢 Safe to Modify

- `test_config_endpoint.py` (risk: 0)
- `validate_test_suite.py` (risk: 0)
- `test_api_key_bug.py` (risk: 0)
- `test_optimizations.py` (risk: 1.8000000000000007)