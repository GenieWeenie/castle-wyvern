# Security Fixes - 2026-02-16

## Summary
This document details the security fixes applied to the Castle Wyvern project on 2026-02-16.

---

## 1. CRITICAL: Removed Hardcoded API Key

### File: `eyrie/phoenix_gate.py`

**Issue:** Hardcoded Z.ai API key was present in the source code (line 37).

**Before:**
```python
self.api_key = os.getenv("AI_API_KEY") or "<REDACTED_API_KEY>"
```

**After:**
```python
self.api_key = os.getenv("AI_API_KEY")
```

**Impact:** The API key is no longer exposed in source code. Users must now set the `AI_API_KEY` environment variable or add it to their `.env` file.

---

## 2. Fixed All Bare `except:` Clauses

Fixed **11 instances** of bare `except:` clauses across **6 files**. Bare except clauses catch all exceptions including `SystemExit`, `KeyboardInterrupt`, and `GeneratorExit`, which can mask critical errors and make debugging difficult.

### Files Modified:

#### 1. `eyrie/phoenix_gate.py` (1 fix)
- **Line 319:** Changed `except:` to `except Exception:` in `health_check()` method when checking local Ollama status.

#### 2. `eyrie/llama_cpp_client.py` (3 fixes)
- **Line 42:** Changed `except:` to `except Exception:` in `_check_connection()`
- **Line 51:** Changed `except:` to `except Exception:` in `is_available()`
- **Line 123:** Changed `except:` to `except Exception:` in `get_models()`

#### 3. `eyrie/function_builder.py` (2 fixes)
- **Line 194:** Changed `except:` to `except Exception:` in `_generate_fetcher_code()` (inside generated fetcher code template)
- **Line 297:** Changed `except:` to `except Exception:` in `_generate_converter_code()` (inside generated converter code template)

#### 4. `eyrie/enhanced_memory.py` (2 fixes)
- **Line 404:** Changed `except:` to `except Exception:` in `add()` method when calling original memory store
- **Line 469:** Changed `except:` to `except Exception:` in `get_stats()` method when getting original memory stats

#### 5. `eyrie/omni_parser.py` (1 fix)
- **Line 93:** Changed `except:` to `except Exception:` in `_check_availability()`

#### 6. `eyrie/workflow_nodes.py` (2 fixes)
- **Line 52:** Changed `except:` to `except Exception:` in `execute()` method of `HTTPNode` when parsing JSON body
- **Line 148:** Changed `except:` to `except Exception:` in `_safe_eval()` method of `ConditionNode` when eval fails

---

## Testing

All **98 tests pass** after these changes:

```
pytest tests/ -v
======================== 98 passed, 1 warning in 1.01s =========================
```

---

## Security Best Practices Applied

1. **No hardcoded secrets:** API keys must now be provided via environment variables
2. **Specific exception handling:** All bare `except:` clauses now catch `Exception` instead of catching everything including system-level exceptions
3. **Minimal code changes:** Only the necessary changes were made to fix the issues

---

## Recommendations for Users

1. **Set your API key:** Add `AI_API_KEY=your_key_here` to your `.env` file or export it as an environment variable
2. **Review `.env.example`:** Ensure all required environment variables are documented
3. **Never commit `.env` files:** Add `.env` to `.gitignore` if not already present
