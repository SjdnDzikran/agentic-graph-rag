# src/utils/logging_config.py
import os
import logging

def setup_logging():
    """Mengatur konfigurasi logging untuk proyek."""
    log_dir = "../log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Menghapus handler yang ada untuk menghindari duplikasi log
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'multi_agent_cykg.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)