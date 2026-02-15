// Debug Logger
function debugLog(msg) {
    // console.log(`[JS Debug] ${msg}`);
    try {
        if (window.pywebview && window.pywebview.api) {
            window.pywebview.api.log_js(msg);
        }
    } catch (e) {
        console.error("Failed to log", e);
    }
}

// UI Elements (Updated for New Layout)
const ui = {
    btnStart: document.getElementById('btn-start'),
    btnStop: document.getElementById('btn-stop'),

    // Inputs
    inputSource: document.getElementById('input-source'),
    inputDest: document.getElementById('input-dest'),
    containerSource: document.getElementById('container-source'),
    containerDest: document.getElementById('container-dest'),
    btnSource: document.getElementById('btn-source'),
    btnDest: document.getElementById('btn-dest'),

    // Areas
    dropZone: document.getElementById('drop-zone'),
    dropZoneContent: document.getElementById('drop-zone-content'),
    fileListContainer: document.getElementById('file-list-container'),
    fileListItems: document.getElementById('file-list-items'),
    fileCount: document.getElementById('file-count'),

    // Console
    consoleOutput: document.getElementById('console-output'),

    // Footer
    progressBar: document.getElementById('progress-bar'),
    progressText: document.getElementById('progress-text'),
    statusText: document.getElementById('status-text'),
    statusDot: document.getElementById('status-dot')
};

// Application State
const state = {
    sourcePath: null,
    destPath: null,
    files: [],
    config: {
        rotation: '90_ccw',
        bitrate: '10'
    },
    isProcessing: false
};

// Main Initialization
async function initApp() {
    debugLog("initApp() v2.5 STARTED");

    if (!window.pywebview || !window.pywebview.api) {
        alert("Erro: API Python não detectada.");
        return;
    }

    // ---- Event Listeners ----

    // 1. Config Radio Buttons (Rotation & Bitrate)
    document.querySelectorAll('input[type=radio]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.checked) {
                const group = e.target.name; // 'rotation' or 'bitrate'
                state.config[group] = e.target.value;
                log(`Configuração alterada: ${group} = ${e.target.value}`, "info");
            }
        });
    });

    // 2. Source Button
    const handleSource = async () => {
        if (state.isProcessing) return;
        try {
            const path = await window.pywebview.api.pick_source_folder();
            if (path) {
                state.sourcePath = path;
                ui.inputSource.value = path;
                ui.containerSource.classList.remove('border-red-500', 'border-border-dark');
                ui.containerSource.classList.add('border-primary'); // Highlight success

                // Scan
                const files = await window.pywebview.api.scan_directory(path);
                state.files = files;
                updateFileList(files);
                log(`Pasta de origem: ${path}`, "success");
            }
        } catch (e) {
            log(`Erro ao selecionar: ${e}`, "error");
        }
    };

    ui.btnSource.addEventListener('click', handleSource);
    ui.dropZone.addEventListener('click', (e) => {
        // Only trigger if clicking the empty zone, not the file list
        if (state.files.length === 0 || e.target.closest('#drop-zone-content')) {
            handleSource();
        }
    });

    // 3. Destination Button
    ui.btnDest.addEventListener('click', async () => {
        if (state.isProcessing) return;
        try {
            const path = await window.pywebview.api.pick_output_folder();
            if (path) {
                state.destPath = path;
                ui.inputDest.value = path;
                ui.containerDest.classList.remove('border-red-500', 'border-border-dark');
                ui.containerDest.classList.add('border-primary'); // Highlight success
                log(`Pasta de destino: ${path}`, "success");
            }
        } catch (e) {
            log(`Erro: ${e}`, "error");
        }
    });

    // 4. Start Button
    ui.btnStart.addEventListener('click', async () => {
        if (state.isProcessing) return;

        // Validation
        let isValid = true;
        if (!state.sourcePath) {
            ui.containerSource.classList.add('border-red-500');
            isValid = false;
        }
        if (!state.destPath) {
            ui.containerDest.classList.add('border-red-500');
            isValid = false;
        }

        if (!isValid) return log("ERRO: Selecione as pastas de origem e destino.", "error");

        if (state.files.length === 0) return log("ERRO: Nenhum arquivo encontrado.", "error");
        if (state.sourcePath === state.destPath) return log("ERRO: Pastas iguais.", "error");

        state.isProcessing = true;
        ui.btnStart.disabled = true;
        ui.btnStart.innerHTML = '<span class="material-symbols-outlined animate-spin">sync</span> PROCESSANDO...';

        // Show Stop Button
        ui.btnStop.classList.remove('hidden');

        try {
            await window.pywebview.api.start_job(state.sourcePath, state.destPath, state.config);
        } catch (e) {
            log(`Erro Fatal: ${e}`, "error");
            resetUiState(); // Reset only on start fail
        }
    });

    // 5. Stop Button
    ui.btnStop.addEventListener('click', async () => {
        if (!state.isProcessing) return;

        const confirmStop = confirm("Deseja realmente parar o processamento? A ação será concluída após o arquivo atual.");
        if (confirmStop) {
            log("Solicitando parada... Aguarde encerrar arquivo atual.", "warning");
            try {
                ui.btnStop.disabled = true;
                ui.btnStop.innerHTML = '<span class="material-symbols-outlined animate-spin">sync</span> PARANDO...';
                await window.pywebview.api.stop_job();
            } catch (e) {
                log(`Erro ao parar: ${e}`, "error");
                ui.btnStop.disabled = false;
                ui.btnStop.innerHTML = "PARAR CONVERSÃO";
            }
        }
    });

    // ... (rest of listeners) ...
    // 6. Get Version
    try {
        if (window.pywebview.api.get_version) {
            const ver = await window.pywebview.api.get_version();
            const footerLink = document.getElementById('app-version-link');
            if (footerLink) footerLink.textContent = `VideoSpin ${ver}`;
            document.title = `VideoSpin ${ver}`;
            log(`Sistema Pronto (${ver}) - Aceleracao Ativa`, "success");
        }
    } catch (e) {
        console.error("Failed to get version", e);
    }
}

function resetUiState() {
    state.isProcessing = false;
    ui.btnStart.disabled = false;
    ui.btnStart.innerHTML = '<span class="material-symbols-outlined">play_arrow</span> INICIAR';

    // Hide Stop Button
    ui.btnStop.classList.add('hidden');
    ui.btnStop.disabled = false;
    ui.btnStop.innerHTML = '<span class="material-symbols-outlined">stop_circle</span> PARAR CONVERSÃO';

    // Reset Progress
    ui.statusDot.classList.add('bg-primary');
    ui.statusDot.classList.remove('bg-green-500');
}

// Helpers
// ... (updateFileList existing) ...

// ... (log existing) ...

// Python Callbacks
window.onJobComplete = function (result) {
    resetUiState();
    if (result && result.success !== undefined) {
        log(`Processamento concluído! Sucesso: ${result.success}/${result.total}`, "success");
        ui.statusText.textContent = "Concluído";
        alert(`Processamento Finalizado!\nSucesso: ${result.success}\nTotal: ${result.total}`);
    } else {
        log("Processamento finalizado.", "info");
    }
}

window.pythonError = function (msg) {
    log(msg, "error");
    resetUiState();
}



// Helpers
function updateFileList(files) {
    if (files.length > 0) {
        ui.dropZoneContent.classList.add('hidden');
        ui.fileListContainer.classList.remove('hidden');
        ui.fileListItems.innerHTML = '';
        ui.fileCount.textContent = files.length;

        files.forEach(f => {
            const div = document.createElement('div');
            div.className = 'flex justify-between items-center p-3 bg-panel-dark/50 rounded border border-white/5 hover:border-primary/30 transition-colors cursor-default text-xs';
            div.innerHTML = `
                <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-sm text-primary">movie</span>
                    <span class="text-slate-300 font-medium">${f.name}</span>
                </div>
                <span class="text-slate-500 font-mono">${f.size}</span>
            `;
            ui.fileListItems.appendChild(div);
        });
    } else {
        ui.dropZoneContent.classList.remove('hidden');
        ui.fileListContainer.classList.add('hidden');
    }
}

function log(msg, type = 'info') {
    const p = document.createElement('p');
    const time = new Date().toLocaleTimeString();
    const colorClass = type === 'error' ? 'text-red-500' : (type === 'success' ? 'text-green-500' : 'text-slate-400');

    // Secure DOM creation (prevents XSS from filenames)
    const spanTime = document.createElement('span');
    spanTime.className = "text-slate-600";
    spanTime.textContent = `[${time}] `;

    const spanMsg = document.createElement('span');
    spanMsg.className = colorClass;
    spanMsg.textContent = msg;

    p.appendChild(spanTime);
    p.appendChild(spanMsg);

    ui.consoleOutput.appendChild(p);
    ui.consoleOutput.scrollTop = ui.consoleOutput.scrollHeight;
}

// Python Callbacks
window.updateProgress = function (current, total, status) {
    const percent = Math.round((Math.min(current, total) / total) * 100);
    ui.progressBar.style.width = `${percent}%`;
    ui.progressText.textContent = `${percent}%`;
    ui.statusText.textContent = `Processando: ${current}/${total}`;

    if (percent === 100) {
        ui.statusDot.classList.remove('bg-primary');
        ui.statusDot.classList.add('bg-green-500');
    } else {
        ui.statusDot.classList.add('bg-primary');
        ui.statusDot.classList.remove('bg-green-500');
    }
}

window.pythonLog = function (level, msg) {
    log(msg, level === 'ERROR' ? 'error' : (level === 'SUCCESS' ? 'success' : 'info'));
}

// Boot
// Boot
if (window.pywebview) {
    initApp();
} else {
    window.addEventListener('pywebviewready', initApp);
}
