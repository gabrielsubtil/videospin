# VideoSpin CUDA - Plano de Implementação

## 1. Visão Geral
Utilitário desktop de alta performance para rotação de vídeos em lote, utilizando aceleração de hardware (NVIDIA CUDA) e interface moderna via PyWebView.
**Objetivo:** Permitir que editores e produtores processem grandes volumes de arquivos rapidamente, mantendo qualidade e faixas de áudio.

## 2. Arquitetura Técnica

### Frontend (Interface)
- **Tecnologia:** PyWebView (WebView2 no Windows).
- **Stack Web:** HTML5, CSS3 (Vanilla + Variáveis CSS), JavaScript (Vanilla ES6+).
- **Design System:** "Premium Dark" - Fundo escuro profundo, acentos em gradiente sutil ou neon (evitando roxo cliché), cards flutuantes, tipografia Inter/Roboto.
- **UX:** Drag & Drop zone, Feedback visual de progresso real, Logs roláveis.

### Backend (Core)
- **Linguagem:** Python 3.12.
- **Processamento:** `subprocess` invocando FFmpeg.
- **Hardware:** Detecção obrigatória de `h264_nvenc`.
- **API Bridge:** Classe `Api` exposta ao PyWebView para comunicação bidirecional.

## 3. Fases de Implementação

### Fase 1: Setup e Validação 🛠️
- [ ] Inicializar estrutura de diretórios (`/src`, `/assets`, `/logs`).
- [ ] Criar `requirements.txt` (`pywebview`, `requests` - se necessário).
- [ ] Implementar `check_diagnostics.py`:
    - Validar instalação do Python 3.12.
    - Validar presença do FFmpeg no PATH.
    - Validar suporte a `h264_nvenc` (`ffmpeg -encoders`).
    - Exibir alertas visuais no console caso falhe.

### Fase 2: Backend Core Logic ⚙️
- [ ] Classe `VideoProcessor`:
    - Método `scan_folder(path)`: Listar vídeos suportados (`.mp4`, `.mov`, `.mkv`).
    - Método `validate_paths(source, dest)`: Impedir `source == dest`.
    - Método `build_command(...)`: Gerar linha de comando FFmpeg com `-hwaccel cuda`.
        - Mapping de Bitrates: 8M, 10M, 12M, 18M.
        - Preservação de áudio: `-map 0:v -map 0:a -c:a copy`.
        - Rotação: Metadata vs Transpose (Definir Transpose forçado para compatibilidade total).
- [ ] Sistema de Logs:
    - Buffer em memória para enviar à UI.
    - Gravação em arquivo (`process.log`).

### Fase 3: Frontend "Visual Excellence" 🎨
- [ ] `index.html`: Estrutura semântica.
- [ ] `style.css`:
    - Paleta Dark Mode (Cinza Escuro #1a1a1a, Acentos em Verde/Azul Ciano ou Laranja "Produtividade").
    - Animações CSS para hover, loading e progresso.
- [ ] `app.js`:
    - Gerenciamento de estado (arquivos selecionados, config).
    - Comunicação com Python (`pywebview.api`).
    - Atualização da barra de progresso em tempo real.

### Fase 4: Integração 🔗
- [ ] Conectar Botão "Processar" -> `api.start_processing()`.
- [ ] Conectar "Selecionar Pasta" -> `api.open_folder_dialog()`.
- [ ] Implementar callback de progresso (Python -> JS).
- [ ] Teste de fluxo completo (E2E Manual).

### Fase 5: Entrega e Polimento 🚀
- [ ] Verificação de Erros (Caminhos com espaços, arquivos corrompidos).
- [ ] Limpeza de código (Linting).
- [ ] Documentação básica (`README.md`).

## 4. Estrutura de Arquivos Proposta
```
/VideoSpin
├── assets/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── src/
│   ├── __init__.py
│   ├── app.py          # Entry point + PyWebView config
│   ├── core.py         # Lógica FFmpeg
│   └── utils.py        # Helpers (Logs, Checks)
├── requirements.txt
├── task-videospin.md
└── README.md
```

## 5. Regras de Negócio (Revisão)
- [ ] **Segurança:** Não sobrescrever arquivos originais.
- [ ] **Integridade:** Bloquear se pasta Origem == Destino.
- [ ] **Performance:** Usar NVENC mandatório.
- [ ] **Qualidade:** Manter resolução original.
