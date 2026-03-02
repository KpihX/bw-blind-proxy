# 💡 BW-MCP: Ideas for Future Evolution

This document tracks architectural enhancements, protocol-specific optimizations, and new features to further strengthen the sovereign bridge between LLMs and Bitwarden.

## 🛠️ MCP Protocol Extensions
- [ ] **Unified Administrative & Maintenance Layer**: Consolidate management and maintenance tasks directly into native MCP constructs (Tools, Resources, Prompts) for full remote operability.
    *   **Admin Tools**: `purge_logs(keep_n)`, `clear_wal()`, `update_config(key, value)`.
    *   **Dynamic Resources**: `bw://status` (health, limits), `bw://audit/recent` (execution traces).
    *   **Standard Prompts**: `/wal-clean` (guided recovery), `/hygiene` (system maintenance).
