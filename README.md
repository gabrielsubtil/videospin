# VideoSpin

> **Processador de Vídeo Profissional com Aceleração de GPU e Detecção Automática de Hardware.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Enabled-green?style=for-the-badge&logo=ffmpeg)
![NVIDIA](https://img.shields.io/badge/NVIDIA-NVENC%20Ready-76B900?style=for-the-badge&logo=nvidia)
![Platform](https://img.shields.io/badge/Platform-Windows-00a4ef?style=for-the-badge&logo=windows)

---

## Sobre o Projeto: Para Videomakers e Criadores de Conteúdo

*"Prezados amigos donos de câmeras da Canon ou outras câmeras que, mesmo filmando na posição vertical, infelizmente entregam os arquivos de vídeo ainda na posição horizontal..."*

Sabemos a dificuldade que é trabalhar com redes sociais quando a câmera grava na vertical mas o arquivo sai "deitado" no computador. Isso quebra o fluxo de trabalho, exige configurações chatas no editor e consome tempo precioso.

**Criei este aplicativo para resolver exatamente isso.**

O **VideoSpin** facilita a vida de quem grava conteúdo bruto (especialmente usuários de Canon que já filmam com o Perfil de Cor/Picture Style correto). A proposta é simples:

1. Arraste seus arquivos brutos.
2. Gere novos arquivos **já na orientação correta** (Vertical Real).
3. Entregue ou poste direto nas redes sociais (Reels, TikTok, Shorts).

Para garantir a qualidade sem arquivos gigantes, defini arbitrariamente os melhores padrões de bitrate para o mercado atual:

* **8 Mbps** para Full HD (1080p) - Equilíbrio perfeito.
* **18 Mbps** para 4K - Máxima nitidez.

---

## Funcionalidades Principais

* **Rotação Física**: Converte vídeos deitados (Landscape) para verticais reais (Portrait) - 90° Horário ou Anti-horário.
* **Motor Híbrido Inteligente**:
  * **NVIDIA NVENC**: Se detectar uma GPU NVIDIA, usa aceleração de hardware para conversão ultra-rápida.
  * **CPU Fallback**: Se não houver GPU compatível, alterna automaticamente para processamento via CPU, garantindo que o app funcione em qualquer PC.
* **Presets de Qualidade**: Opções de bitrate (8, 10, 12, 18 Mbps) focadas em redes sociais.
* **Processamento em Lote**: Converta pastas inteiras ou múltiplos arquivos de uma vez.
* **Interface Limpa**: Design moderno, Drag & Drop e Logs em tempo real.

---

## Requisitos do Sistema

1. **Python 3.10+** instalado.
2. **FFmpeg** instalado e adicionado ao PATH do sistema (Essencial para o processamento).
3. **Drivers NVIDIA** atualizados (Opcional, apenas para aceleração de hardware).

---

## Instalação e Uso

O VideoSpin foi projetado para ser leve. Você não precisa instalar nada complexo além do Python e FFmpeg.

### Para Usuários (Executando o Código Fonte)

1. **Pré-requisitos**:
    * **Python 3.12+** (Recomendado) ou versão mais recente compatível com `pywebview`. ([Baixar aqui](https://www.python.org/downloads/))
    * **FFmpeg** ([Baixar aqui](https://ffmpeg.org/download.html)) - *Importante: Adicione ao PATH do sistema.*

2. **Instalação**:
    Abra o terminal na pasta do projeto e digite:

    ```bash
    pip install -r requirements.txt
    ```

3. **Executar**:

    ```bash
    python src/app.py
    ```

---

## Compilação Futura (PyInstaller)

O projeto já está configurado para gerar um executável único (`.exe`).
Quando desejar compilar, apenas instale o `pyinstaller` e execute:

```bash
pyinstaller videospin.spec
```

Isso gerará o arquivo `dist/VideoSpin-v10.exe` autônomo.

---

## Agradecimentos e Créditos

Este projeto foi desenvolvido através de uma sessão intensiva de **Vibe Code**, cuidadosamente testado e arquitetado com foco em Clean Code e Segurança.

Um agradecimento especial ao ecossistema **Google Antigravity**, cuja inteligência e capacidades avançadas de agente possibilitaram a criação desta ferramenta profissional em tempo recorde.

---

**VideoSpin** - Potência máxima para seus vídeos verticais.

---

## Licença e Uso

**PolyForm Shield License 1.0.0**

> [!IMPORTANT]
> **Este software é gratuito para uso, inclusive comercial (prestação de serviços). No entanto, é estritamente proibido vender, licenciar ou comercializar este software ou versões modificadas dele como um produto autônomo.**

**Desenvolvedor:**
Gabriel Subtil - [GitHub](https://github.com/gabrielsubtil)
Contato: <gabrielsubtil@hotmail.com>
