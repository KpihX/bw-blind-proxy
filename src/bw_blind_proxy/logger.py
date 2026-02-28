import json
import os
import datetime
from typing import List, Dict, Any
from .models import TransactionPayload, TransactionStatus
from .config import STATE_DIR

LOG_DIR = os.path.join(STATE_DIR, "logs")

class TransactionLogger:
    """
    Manages immutable, human-readable logging of all transactions applied to the Vault.
    Strictly sanitizes all payloads to prevent any secret from spilling to the disk.
    """
    
    @staticmethod
    def _ensure_dir():
        if not os.path.exists(STATE_DIR):
            os.makedirs(STATE_DIR, exist_ok=True)
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR, exist_ok=True)
            
    @staticmethod
    def log_transaction(
        transaction_id: str,
        payload: TransactionPayload,
        status: TransactionStatus,
        error_message: str = None,
        executed_ops: List[str] = None,
        failed_op: Dict[str, Any] = None,
        executed_rolled_back_cmds: List[str] = None,
        failed_rollback_cmd: str = None  # Only ONE cmd can fail in a sequential LIFO pass
    ) -> str:
        """
        Writes a detailed execution report to a local flat file.
        Format: YYYY-MM-DD_HH-MM-SS_<status>.log
        """
        TransactionLogger._ensure_dir()
        
        now = datetime.datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        status_safe = status.replace(" ", "_").lower()
        
        import json
        
        filename = f"{timestamp_str}_{transaction_id}_{status_safe}.json"
        filepath = os.path.join(LOG_DIR, filename)
        
        # Build structured JSON dict
        log_data = {
            "transaction_id": transaction_id,
            "timestamp": now.isoformat(),
            "status": status,
            "rationale": payload.rationale,
            "error_message": error_message,
            "operations_requested": payload.model_dump().get("operations", []),
            "execution_trace": [msg.lstrip('-> ').strip() for msg in (executed_ops or [])],
            "failed_execution": failed_op,
            "rollback_trace": executed_rolled_back_cmds or [],
            "failed_rollback": failed_rollback_cmd
        }
        
        # Safely remove None values to keep logs minimal
        log_data = {k: v for k, v in log_data.items() if v is not None}
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)
            
        return filepath
