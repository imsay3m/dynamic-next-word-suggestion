document.addEventListener("DOMContentLoaded", () => {
    const datasetSelect = document.getElementById("dataset-select");
    const uploadForm = document.getElementById("upload-form");
    const fileInput = document.getElementById("file-input");
    const uploadStatus = document.getElementById("upload-status");
    const trainBtn = document.getElementById("train-btn");
    const modelStatus = document.getElementById("model-status");
    const dataDisplayArea = document.getElementById("data-display-area");
    const predictionInput = document.getElementById("prediction-input");
    const suggestionsDiv = document.getElementById("suggestions");
    const logsDiv = document.getElementById("logs");
    const downloadModelBtn = document.getElementById("download-model-btn");
    const loadingSpinner = document.getElementById("loading-spinner");
    
    
    const previewTemplate = document.getElementById("template-data-preview");
    const customDataTemplate = document.getElementById("template-custom-data");

    let socket;
    let currentDataset = "";
    

    async function populateDatasetDropdown() {
        try {
            const response = await fetch("/get_datasets");
            const datasets = await response.json();
            datasetSelect.innerHTML = ""; 

            if (datasets.length === 0) {
                datasetSelect.innerHTML = "<option value=''>No datasets found. Please upload one.</option>";
                return;
            }

            datasets.forEach(name => {
                const option = document.createElement("option");
                option.value = name;
                option.textContent = name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                datasetSelect.appendChild(option);
            });
            
            const customOption = document.createElement("option");
            customOption.value = "custom";
            customOption.textContent = "Custom (Manual Input)";
            datasetSelect.appendChild(customOption);
            
            datasetSelect.dispatchEvent(new Event('change'));

        } catch (error) {
            console.error("Failed to load datasets:", error);
            datasetSelect.innerHTML = "<option>Error loading datasets</option>";
        }
    }

    function connectWebSocket() {
        socket = new WebSocket(`ws://${window.location.host}/ws`);
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.status === "training") {
                logsDiv.innerHTML += `<p>${data.log}</p>`;
                logsDiv.scrollTop = logsDiv.scrollHeight;
            } else if (data.status === "trained") {
                logsDiv.innerHTML += `<p><strong>${data.log}</strong></p>`;
                updateModelStatusUI(true);
            }
        };
        socket.onclose = () => { setTimeout(connectWebSocket, 1000); };
    }

    function updateModelStatusUI(isTrained) {
        if (isTrained) {
            modelStatus.innerHTML = `<i class="fas fa-check-circle"></i> Model Trained`;
            modelStatus.className = 'status-indicator trained';
            predictionInput.disabled = false;
            predictionInput.placeholder = "Start typing...";
            downloadModelBtn.classList.remove("hidden");
        } else {
            modelStatus.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Needs Training`;
            modelStatus.className = 'status-indicator untrained';
            predictionInput.disabled = true;
            predictionInput.placeholder = "Train a model to start typing...";
            downloadModelBtn.classList.add("hidden");
        }
        trainBtn.disabled = false;
        trainBtn.textContent = "Train Model";
        trainBtn.insertAdjacentHTML('afterbegin', '<i class="fas fa-brain"></i>');
    }
    
    async function checkAndSetInitialStatus() {
        if (!currentDataset || currentDataset === "custom") {
             updateModelStatusUI(false);
             trainBtn.disabled = (currentDataset === "");
             return;
        }
        const response = await fetch(`/check_model_status?dataset=${currentDataset}`);
        const data = await response.json();
        updateModelStatusUI(data.is_trained);
    }
    
    async function displayDataContent(dataset) {
        dataDisplayArea.innerHTML = ''; 
        if (dataset === "custom") {
            const customNode = customDataTemplate.content.cloneNode(true);
            dataDisplayArea.appendChild(customNode);
        } else if (dataset) {
            const previewNode = previewTemplate.content.cloneNode(true);
            dataDisplayArea.appendChild(previewNode);
            const dataPreviewEl = dataDisplayArea.querySelector("#data-preview");
            
            const response = await fetch(`/get_dataset_preview?dataset=${dataset}`);
            const data = await response.json();
            dataPreviewEl.textContent = data.preview;
        }
    }

    datasetSelect.addEventListener("change", () => {
        currentDataset = datasetSelect.value;
        displayDataContent(currentDataset);
        checkAndSetInitialStatus();
        predictionInput.value = "";
        suggestionsDiv.innerHTML = "";
    });

    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        uploadStatus.textContent = "Uploading...";
        uploadStatus.className = 'status-message';
        
        try {
            const response = await fetch("/upload_dataset", {
                method: "POST",
                body: formData,
            });
            const result = await response.json();

            if (response.ok) {
                uploadStatus.textContent = result.message;
                uploadStatus.classList.add("success");
                await populateDatasetDropdown();
                datasetSelect.value = result.new_dataset_key;
                datasetSelect.dispatchEvent(new Event('change'));
            } else {
                uploadStatus.textContent = `Error: ${result.message}`;
                uploadStatus.classList.add("error");
            }
        } catch (error) {
            uploadStatus.textContent = "An error occurred during upload.";
            uploadStatus.classList.add("error");
            console.error(error);
        }
        uploadForm.reset();
    });

    let predictionController = null;
    predictionInput.addEventListener("input", async (e) => {
        const text = e.target.value;
        if (predictionController) {
            predictionController.abort();
        }
        if (text.trim() === "") {
            suggestionsDiv.innerHTML = "";
            loadingSpinner.classList.add("hidden");
            return;
        }
        predictionController = new AbortController();
        const signal = predictionController.signal;
        loadingSpinner.classList.remove("hidden");
        suggestionsDiv.innerHTML = "";
        try {
            const response = await fetch("/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ dataset: currentDataset, text: text }),
                signal: signal,
            });
            const data = await response.json();
            
            if (signal.aborted) return;

            loadingSpinner.classList.add("hidden");

            if (data.predictions && data.predictions.length > 0) {
                data.predictions.forEach(word => {
                    if (!word) return;
                    const suggestionEl = document.createElement("div");
                    suggestionEl.className = "suggestion";
                    suggestionEl.textContent = word;
                    suggestionEl.onclick = () => {
                        predictionInput.value = word;
                        suggestionsDiv.innerHTML = "";
                        predictionInput.focus();
                    };
                    suggestionsDiv.appendChild(suggestionEl);
                });
            }
        } catch (error) {
            if (error.name !== 'AbortError') { console.error("Prediction error:", error); }
            loadingSpinner.classList.add("hidden");
        }
    });

    trainBtn.addEventListener("click", () => {
        const customTextArea = document.getElementById("custom-text");
        const customText = customTextArea ? customTextArea.value : "";
        if (socket.readyState === WebSocket.OPEN) {
            logsDiv.innerHTML = "";
            trainBtn.disabled = true;
            trainBtn.textContent = "Training...";
            socket.send(JSON.stringify({
                action: "train",
                dataset: currentDataset,
                custom_text: customText,
            }));
        }
    });

    downloadModelBtn.addEventListener("click", () => {
        window.open(`/models/${currentDataset}_model.keras`, '_blank');
    });

    connectWebSocket();
    populateDatasetDropdown();
});