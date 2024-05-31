const video = document.getElementById('video');
const websocket = new WebSocket("ws://localhost:8000/ws");

websocket.onopen = function(event) {
    console.log("WebSocket connection opened.");
};

websocket.onmessage = function(event) {
    const imageUrl = URL.createObjectURL(new Blob([event.data], { type: 'image/jpeg' }));
    video.src = imageUrl;
};

websocket.onerror = function(event) {
    console.log("WebSocket error: ", event);
};

websocket.onclose = function(event) {
    console.log("WebSocket connection closed: ", event);
};

async function setSide(side) {
    console.log(`Setting side to: ${side}`);
    const response = await fetch(`/set_side/${side}`, { method: 'POST' });
    const data = await response.json();
    console.log(`Server response: ${JSON.stringify(data)}`);
}

