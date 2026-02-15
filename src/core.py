import os
import subprocess
import json
import time
from pathlib import Path

class VideoProcessor:
    def __init__(self):
        self.is_processing = False
        self.stop_requested = False
        self.log_callback = None
        self.progress_callback = None
        self.use_gpu = self.check_hardware()
        self.current_process = None # Track active process for kill

    def request_stop(self):
        """Sinaliza para parar o processamento."""
        if self.is_processing:
            self.stop_requested = True
            self.log("[STOP] Solicitacao de parada recebida...", "WARNING")
            
            # Força encerramento do processo atual se existir
            if self.current_process:
                try:
                    self.log("[STOP] Encerrando processo FFmpeg atual...", "WARNING")
                    self.current_process.terminate() # Tenta SIGTERM
                except Exception as e:
                    self.log(f"[STOP] Erro ao matar processo: {e}", "ERROR")

    def check_hardware(self):
        """Verifica se há suporte a NVIDIA NVENC."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-encoders"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            if "h264_nvenc" in result.stdout:
                return True
        except:
            pass
        return False

    def set_callbacks(self, log_cb, progress_cb):
        """Define callbacks para logs e progresso da UI."""
        self.log_callback = log_cb
        self.progress_callback = progress_cb

    def log(self, message, level="INFO"):
        """Envia log para a UI e console."""
        # print(f"[{level}] {message}") # Removed print
        if self.log_callback:
            self.log_callback({'level': level, 'message': message})

    def scan_folder(self, folder_path):
        """Lista arquivos de vídeo compatíveis na pasta."""
        
        # Notificar status do hardware no primeiro scan
        if self.use_gpu:
             self.log("[GPU] Acelaracao de Hardware (NVENC) ATIVA.", "SUCCESS")
        else:
             self.log("[CPU] NVENC nao detectado. Usando CPU (Lento).", "WARNING")

        if not os.path.isdir(folder_path):
            return []
        
        valid_exts = {'.mp4', '.mov', '.mkv', '.avi', '.ts'}
        files = []
        try:
            for f in os.listdir(folder_path):
                file_path = Path(folder_path) / f
                if file_path.is_file() and file_path.suffix.lower() in valid_exts:
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    files.append({
                        'name': f,
                        'path': str(file_path),
                        'size': f"{size_mb:.1f} MB"
                    })
            self.log(f"Scan concluido: {len(files)} videos encontrados em {folder_path}")
            return files
        except Exception as e:
            self.log(f"Erro ao escanear pasta: {e}", "ERROR")
            return []

    def build_ffmpeg_command(self, input_path, output_path, options):
        """Constrói o comando FFmpeg baseado nas configurações e hardware."""
        
        # Opções de Rotação
        rotation = options.get('rotation', '90_ccw')
        if rotation == '90_cw':
            transpose_filter = "transpose=1"
        elif rotation == '90_ccw':
            transpose_filter = "transpose=2"

        # Opções de Bitrate
        bitrate = options.get('bitrate', '10') # Default 10 Mbps
        bitrate_val = f"{bitrate}M"

        cmd = ["ffmpeg", "-y"]

        if self.use_gpu:
            # Opções GPU (NVENC)
            cmd.extend(["-hwaccel", "cuda"])
            cmd.extend(["-i", input_path])
            cmd.extend(["-c:v", "h264_nvenc"])
            cmd.extend(["-b:v", bitrate_val])
        else:
            # Opções CPU (libx264)
            # Sem hwaccel
            cmd.extend(["-i", input_path])
            cmd.extend(["-c:v", "libx264"])
            cmd.extend(["-preset", "fast"]) # Compromisso velocidade/qualidade
            cmd.extend(["-b:v", bitrate_val]) 

        # Filtros comuns
        if transpose_filter:
            cmd.extend(["-vf", transpose_filter])
        
        cmd.extend(["-c:a", "copy"])
        cmd.extend(["-map", "0:v"])
        cmd.extend(["-map", "0:a"])
        cmd.append(output_path)

        return cmd

    def process_queue(self, queue, output_folder, options):
        """Processa a lista de arquivos."""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.stop_requested = False # Reset flag
        total = len(queue)
        
        self.log(f"Iniciando processamento de {total} arquivos...")
        self.log(f"Modo: {'NVENC (GPU)' if self.use_gpu else 'CPU Software'}")
        self.log(f"Destino: {output_folder}")
        self.log(f"Opcoes: {options}")

        success_count = 0
        
        for idx, item in enumerate(queue):
            if self.stop_requested:
                self.log("[STOP] Processamento interrompido pelo usuario.", "WARNING")
                break

            input_path = item['path']
            filename = item['name']
            
            # Atualizar UI: Iniciando este arquivo
            if self.progress_callback:
                 self.progress_callback({'current': idx, 'total': total, 'status': f'Iniciando {filename}...'})

            # Validação: Origem != Destino
            if Path(input_path).parent == Path(output_folder):
                self.log(f"PULADO: Origem e destino sao iguais para {filename}", "WARNING")
                if self.progress_callback:
                    self.progress_callback({'current': idx + 1, 'total': total, 'status': 'skipped'})
                continue

            stem = Path(filename).stem
            suffix = Path(filename).suffix
            output_file = Path(output_folder) / f"{stem}_spin{suffix}"
            
            cmd = self.build_ffmpeg_command(input_path, str(output_file), options)
            
            self.log(f"Processando: {filename}...")
            
            try:
                # Executa FFmpeg
                # start_new_session=True para não abrir janela de console no Windows se empacotado
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, # FFmpeg logs to stderr
                    text=True,
                    encoding='utf-8', 
                    errors='replace'
                )
                
                # Ler stderr em tempo real para logs seria ideal, 
                # mas para simplificar vamos esperar e pegar o erro se falhar.
                # Para barra de progresso real do FFmpeg precisaríamos parsear o stderr.
                # Por enqaunto, bloqueante simples por arquivo.
                stdout, stderr = self.current_process.communicate()
                
                if self.stop_requested:
                     self.log(f"[STOP] Arquivo {filename} abortado.", "WARNING")
                elif self.current_process.returncode == 0:
                    self.log(f"[OK] Sucesso: {filename}")
                    success_count += 1
                else:
                    self.log(f"[ERRO] Falha em {filename}: {stderr[:200]}...", "ERROR") # Show last 200 chars

            except Exception as e:
                self.log(f"Erro critico em {filename}: {e}", "ERROR")
            
            finally:
                self.current_process = None

            # Atualizar progresso UI
            if self.progress_callback:
                self.progress_callback({'current': idx + 1, 'total': total, 'status': 'processing'})

        self.is_processing = False
        self.log(f"Fim do processamento. Sucesso: {success_count}/{total}")
        return {'success': success_count, 'total': total}
