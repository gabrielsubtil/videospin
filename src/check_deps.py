import shutil
import subprocess
import sys
import os

# Forçar UTF-8 no Windows para exibir emojis corretamente
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

def check_requirements():
    print("🔍 Iniciando diagnóstico do ambiente VideoSpin CUDA...\n")

    # 1. Python Version
    v = sys.version_info
    print(f"✅ Python: {v.major}.{v.minor}.{v.micro}")
    if v < (3, 12):
        print("⚠️  Aviso: O projeto foi desenhado para Python 3.12+.")

    # 2. FFmpeg no PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print(f"✅ FFmpeg encontrado: {ffmpeg_path}")
    else:
        print("❌ Erro CRÍTICO: FFmpeg não encontrado no PATH do sistema.")
        print("   Por favor, instale o FFmpeg e adicione ao PATH.")
        return False

    # 3. Check NVENC support
    print("🔍 Verificando suporte a NVIDIA NVENC...")
    try:
        # Executa ffmpeg -encoders para listar
        result = subprocess.run(
            ["ffmpeg", "-encoders"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        output = result.stdout
        if "h264_nvenc" in output or "hevc_nvenc" in output:
            print("✅ Suporte a NVENC detectado!")
            if "h264_nvenc" in output:
                print("   - h264_nvenc: Disponível")
            if "hevc_nvenc" in output:
                print("   - hevc_nvenc: Disponível")
        else:
            print("⚠️  ALERTA: Encoder 'h264_nvenc' NÃO encontrado.")
            print("   O processamento via hardware (CUDA) falhará.")
            print("   Verifique se seus drivers NVIDIA estão atualizados.")
            return False

    except Exception as e:
        print(f"❌ Erro ao executar FFmpeg: {e}")
        return False

    print("\n✅ Diagnóstico concluído. O ambiente parece pronto.")
    return True

if __name__ == "__main__":
    success = check_requirements()
    if not success:
        sys.exit(1)
