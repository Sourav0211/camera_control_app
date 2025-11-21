let connectedCameras = new Set();

async function detectCameras() {
  try {
    const response = await fetch("/api/cameras");
    const data = await response.json();

    const container = document.getElementById("availableCameras");
    container.innerHTML = "";

    if (data.available.length === 0) {
      container.innerHTML = '<p style="color: #777;">No cameras detected</p>';
      return;
    }

    data.available.forEach((cameraId) => {
      const button = document.createElement("button");
      button.className = "camera-button";
      button.textContent = `Camera ${cameraId}`;
      button.onclick = () => connectCamera(cameraId);

      if (data.connected.includes(cameraId)) {
        button.disabled = true;
        button.textContent = `Camera ${cameraId} (Connected)`;
      }

      container.appendChild(button);
    });
  } catch (error) {
    console.error("Error detecting cameras:", error);
  }
}

async function connectCamera(cameraId) {
  try {
    const response = await fetch(`/api/camera/${cameraId}/connect`, {
      method: "POST",
    });

    if (response.ok) {
      connectedCameras.add(cameraId);
      await createCameraCard(cameraId);
      await detectCameras();
    }
  } catch (error) {
    console.error("Error connecting camera:", error);
  }
}

async function disconnectCamera(cameraId) {
  try {
    const response = await fetch(`/api/camera/${cameraId}/disconnect`, {
      method: "POST",
    });

    if (response.ok) {
      connectedCameras.delete(cameraId);
      const card = document.getElementById(`camera-${cameraId}`);
      if (card) card.remove();
      await detectCameras();
    }
  } catch (error) {
    console.error("Error disconnecting camera:", error);
  }
}

async function createCameraCard(cameraId) {
  const container = document.getElementById("connectedCameras");

  // Get camera settings
  const settingsResponse = await fetch(`/api/camera/${cameraId}/settings`);
  const settings = await settingsResponse.json();

  const card = document.createElement("div");
  card.className = "camera-card";
  card.id = `camera-${cameraId}`;

  card.innerHTML = `
                <div class="camera-header">
                    <h3>Camera ${cameraId}</h3>
                    <button class="disconnect-btn" onclick="disconnectCamera(${cameraId})">Disconnect</button>
                </div>
                
                <div class="video-container">
                    <img src="/api/camera/${cameraId}/stream" alt="Camera ${cameraId} Stream">
                </div>
                
                <div class="settings-grid" id="settings-${cameraId}">
                    ${createSettingsHTML(cameraId, settings)}
                </div>
            `;

  container.appendChild(card);
}

function createSettingsHTML(cameraId, settings) {
  const settingsToShow = [
    "brightness",
    "contrast",
    "saturation",
    "exposure",
    "gain",
  ];
  let html = "";

  settingsToShow.forEach((setting) => {
    if (settings[setting] !== undefined && settings[setting] !== -1) {
      html += `
                        <div class="setting-control">
                            <label>${
                              setting.charAt(0).toUpperCase() + setting.slice(1)
                            }</label>
                            <input type="range" 
                                   min="-100" 
                                   max="100" 
                                   value="${settings[setting]}" 
                                   id="${cameraId}-${setting}"
                                   onchange="updateSetting(${cameraId}, '${setting}', this.value)">
                            <span class="setting-value" id="${cameraId}-${setting}-value">${
        settings[setting]
      }</span>
                        </div>
                    `;
    }
  });

  return html || '<p style="color: #777;">No adjustable settings available</p>';
}

async function updateSetting(cameraId, setting, value) {
  try {
    const response = await fetch(`/api/camera/${cameraId}/settings`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        setting: setting,
        value: parseFloat(value),
      }),
    });

    if (response.ok) {
      document.getElementById(`${cameraId}-${setting}-value`).textContent =
        value;
    }
  } catch (error) {
    console.error("Error updating setting:", error);
  }
}

// Initialize on page load
detectCameras();
