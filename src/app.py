import os
import threading
import json
import webview
import traceback
from pathlib import Path
from core import VideoProcessor

# Variáveis globais
APP_VERSION = "v1.0"
window = None 
processor = VideoProcessor()

class Api:
    def __init__(self):
        self._cancel_flag = False

    def get_version(self):
        """Retorna a versão do aplicativo."""
        return APP_VERSION

    def _get_window(self):
        try:
            return webview.windows[0]
        except IndexError:
            if window: return window
            print("CRITICAL: No active window found for API call.")
            return None

    def log_js(self, msg):
        """Método de debug chamado pelo JS."""
        print(f"🔹 JS LOG: {msg}")

    def pick_source_folder(self):
        """Abre diálogo de seleção de pasta."""
        print("🐍 API CALL: pick_source_folder")
        win = self._get_window()
        if not win:
            print("❌ No window found")
            return None
            
        try:
            result = win.create_file_dialog(webview.FOLDER_DIALOG)
            print(f"📂 API RESULT (Source): {result}")
            return result[0] if result and len(result) > 0 else None
        except Exception as e:
            err_msg = f"Erro ao abrir diálogo: {e}"
            print(f"❌ API EXCEPTION: {err_msg}")
            traceback.print_exc()
            return None

    def pick_output_folder(self):
        """Abre diálogo de seleção de pasta."""
        print("🐍 API CALL: pick_output_folder")
        win = self._get_window()
        if not win:
            return None
            
        try:
            result = win.create_file_dialog(webview.FOLDER_DIALOG)
            print(f"📂 API RESULT (Dest): {result}")
            return result[0] if result and len(result) > 0 else None
        except Exception as e:
            err_msg = f"Erro ao abrir diálogo: {e}"
            print(f"❌ API EXCEPTION: {err_msg}")
            traceback.print_exc()
            return None

    def scan_directory(self, folder_path):
        """Wrapper para o scanner do core."""
        print(f"🐍 API CALL: scan_directory {folder_path}")
        try:
            return processor.scan_folder(folder_path)
        except Exception as e:
            print(f"❌ API SCAN ERROR: {e}")
            return []

    def start_job(self, source, dest, options):
        """Inicia o processamento."""
        print(f"🐍 API CALL: start_job {options}")
        
        if not source or not dest:
            return {'success': 0, 'total': 0, 'error': 'Pastas inválidas'}

        # Setup callbacks
        processor.set_callbacks(self.on_log, self.on_progress)
        
        try:
            # Re-scan to catch changes
            files = processor.scan_folder(source)
            if not files:
                return {'success': 0, 'total': 0, 'error': 'Nenhum arquivo encontrado'}

            result = processor.process_queue(
                files, 
                dest, 
                options
            )
            return result
        except Exception as e:
            msg = str(e)
            print(f"❌ API PROCESS ERROR: {msg}")
            traceback.print_exc()
            self.on_log({'level': 'ERROR', 'message': msg})
            return {'success': 0, 'total': 0, 'error': msg}

    def stop_job(self):
        """Para o processamento."""
        print("🐍 API CALL: stop_job")
        processor.request_stop()
        return True

    def on_log(self, data):
        level = data.get('level', 'INFO')
        msg = str(data.get('message', ''))
        msg_json = json.dumps(msg) 
        
        win = self._get_window()
        if win:
            win.evaluate_js(f"window.pythonLog('{level}', {msg_json})")

    def on_progress(self, data):
        win = self._get_window()
        if win:
            win.evaluate_js(f"window.updateProgress({data['current']}, {data['total']}, '{data['status']}')")

# ... (imports)
import sys

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# ... (Api class)

def main():
    global window
    api = Api()
    
    # Path Resolution Logic for Onefile
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller Mode
        assets_dir = Path(sys._MEIPASS) / 'assets'
    else:
        # Dev Mode (Standard Python)
        # Assumes running from root with `python src/app.py`
        assets_dir = Path(__file__).resolve().parent.parent / 'assets'
        
    index_file = assets_dir / 'index.html'

    if not index_file.exists():
        # Fallback check
        print(f"CRITICAL: {index_file} not found! Trying fallback...")
        assets_dir = Path("assets").resolve()
        index_file = assets_dir / "index.html"
        
    if not index_file.exists():
        webview.create_window('Error', html=f'<h1>Critical Error: Assets not found</h1><p>Path: {index_file}</p>')
        webview.start()
        return

    url_safe = index_file.as_uri()
    print(f"🚀 Loading URL: {url_safe}")

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
