# 💡 BW-MCP: Ideas for Future Evolution

This document tracks architectural enhancements, protocol-specific optimizations, and new features to further strengthen the sovereign bridge between LLMs and Bitwarden.

## 🛠️ MCP Protocol Extensions
- [ ] **Unified Administrative & Maintenance Layer**: Consolidate management and maintenance tasks directly into native MCP constructs (Tools, Resources, Prompts) for full remote operability.
    *   **Admin Tools**: `purge_logs(keep_n)`, `clear_wal()`, `update_config(key, value)`.
    *   **Dynamic Resources**: `bw://status` (health, limits), `bw://audit/recent` (execution traces).
    *   **Standard Prompts**: `/wal-clean` (guided recovery), `/hygiene` (system maintenance).

- [x] **Blind Secret Comparator** (Implemented in v1.7.0)
- [ ] **Organization Collection Browser**: Add a specific tool to list/manage organizational collections as first-class citizens, improving Enterprise vault organization speed.
- [ ] **Auto-Cleanup Daemon**: A background task that automatically purges logs older than X days or alerts the user if a WAL orphan persists for more than 24 hours.
- [ ] **Interactive WAL Recovery Prompt**: A rich MCP Prompt (`/recover`) that guides the LLM through a failed transaction recovery by providing the exact step that failed and offering options to retry or force-delete the WAL.
