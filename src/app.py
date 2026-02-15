import os
import threading
import json
import webview
import traceback
import sys
from pathlib import Path
from core import VideoProcessor

# Variáveis globais
APP_VERSION = "v1.1"
window = None 
processor = VideoProcessor()

class Api:
    def __init__(self):
        self._cancel_flag = False

    def get_version(self):
        """Retorna a versão do aplicativo."""
        return APP_VERSION

    def start_job(self, source, dest, config):
        """Inicia o processamento."""
        
        # Set callbacks before starting the process
        processor.set_callbacks(self.on_log, self.on_progress)

        def run():
            try:
                # Se source for string (caminho), faz o scan para obter a lista
                if isinstance(source, str):
                    queue = processor.scan_folder(source)
                else:
                    queue = source

                result = processor.process_queue(queue, dest, config)
                
                # Notify UI of completion
                if window:
                    window.evaluate_js(f"window.onJobComplete({json.dumps(result)})")
                    
            except Exception as e:
                err = traceback.format_exc()
                # Use on_log wrapper to handle safe logging
                self.on_log({'level': 'ERROR', 'message': f"ERRO FATAL: {str(e)}"})
                if window:
                    window.evaluate_js(f"window.pythonError({json.dumps(str(e))})")
                
        t = threading.Thread(target=run, daemon=True)
        t.start()
        return True

    def stop_job(self):
        """Para o processamento."""
        processor.request_stop()
        return True

    def pick_source_folder(self):
        folder = window.create_file_dialog(webview.FOLDER_DIALOG)
        return folder[0] if folder else None

    def pick_output_folder(self):
        folder = window.create_file_dialog(webview.FOLDER_DIALOG)
        return folder[0] if folder else None

    def scan_directory(self, path):
        valid_exts = {'.mp4', '.mov', '.avi', '.mkv', '.ts'}
        files = []
        try:
            for entry in os.scandir(path):
                if entry.is_file() and Path(entry.name).suffix.lower() in valid_exts:
                    size_mb = entry.stat().st_size / (1024 * 1024)
                    files.append({
                        'name': entry.name,
                        'path': entry.path,
                        'size': f"{size_mb:.1f} MB"
                    })
        except Exception as e:
            self.on_log({'level': 'ERROR', 'message': f"Erro ao ler pasta: {e}"})
        return files
        
    def log_js(self, msg):
        # Called from JS, just prints to python console safely?
        # But we removed prints for crash prevention.
        # Maybe use logging if needed, or pass.
        pass

    def on_log(self, data):
        """
        Callback de logs vindo do Python -> JS.
        Pode receber um dict (se vindo do core) ou (msg, level) se alterado.
        Mas vamos assumir que core.py envia dict.
        """
        level = "INFO"
        msg = ""

        if isinstance(data, dict):
             level = data.get('level', 'INFO')
             msg = str(data.get('message', ''))
        else:
             # Legacy case just in case
             msg = str(data)
        
        if window:
            # Safe JSON serialization for JS string
            safe_msg = json.dumps(msg)
            # safe_msg already includes quotes ("foo"), so don't quote in JS
            window.evaluate_js(f"window.pythonLog('{level}', {safe_msg})")

    def on_progress(self, data):
        """
        Callback de progresso.
        Core.py envia: {'current': int, 'total': int, 'status': str}
        """
        if window and isinstance(data, dict):
            current = data.get('current', 0)
            total = data.get('total', 0)
            status = data.get('status', 'processing')
            # status is simple string, wrap in quotes
            window.evaluate_js(f"window.updateProgress({current}, {total}, '{status}')")

def main():
    global window
    api = Api() # Instantiate here
    
    # Path Resolution Logic for Onefile
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller Mode
        assets_dir = Path(sys._MEIPASS) / 'assets'
    else:
        # Dev Mode
        assets_dir = Path(__file__).resolve().parent.parent / 'assets'
        
    index_file = assets_dir / "index.html"

    if not index_file.exists():
        # Fallback check
        assets_dir = Path("assets").resolve()
        index_file = assets_dir / "index.html"
        
    if not index_file.exists():
        webview.create_window('Error', html=f'<h1>Critical Error: Assets not found</h1><p>Path: {index_file}</p>')
        webview.start()
        return

    url_safe = index_file.as_uri()

    window = webview.create_window(
        title=f'VideoSpin {APP_VERSION}', 
        url=url_safe,
        js_api=api,
        width=1100,
        height=720,
        resizable=True,
        background_color='#0f172a',
        text_select=False
    )
    
    webview.start(debug=False)

if __name__ == '__main__':
    main()
