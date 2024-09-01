function startAIBot(tournament_id) {
    const url = (window.location.protocol == "https:" ? "wss://" : "ws://") +
        window.location.host +
        "/ws/pong/" +
        tournament_id +
        "/" +
        "?is_bot=True";

    console.log("Starting AI Bot WebSocket on URL: ", url);
    const socket = new WebSocket(url);

    const FIELD_HEIGHT = 500;
    const PADDLE_HEIGHT = 100;

    socket.onopen = function(e) {
        console.log("AI Bot WebSocket connection opened");
    };

    socket.onclose = function(e) {
        console.log("AI Bot WebSocket connection closed");
    };

    function sendGameData(key, keyAction) {
        socket.send(JSON.stringify({
            message: {
                key: key,
                keyAction: keyAction,
            },
            type: "game",
        }));
    }

    function aiMove(ballY, paddleY) {
        const paddleCenter = paddleY;
        if (ballY < paddleCenter - 10) {
            sendGameData("ArrowUp", "keydown");
            setTimeout(() => sendGameData("ArrowUp", "keyup"), 100);
        } else if (ballY > paddleCenter + 10) {
            sendGameData("ArrowDown", "keydown");
            setTimeout(() => sendGameData("ArrowDown", "keyup"), 100);
        }
    }

    socket.onmessage = function(e) {
        const gameData = JSON.parse(e.data);
        console.log("AI Bot received game state:", gameData);

        if (gameData.state === "finished") {
            console.log("Game finished. Winner:", gameData.winner);
            socket.close();
            return;
        }

        // AI logic
        const ballY = gameData.ball.y;
        const paddleY = gameData.player2.y; // Assuming AI is player2

        aiMove(ballY, paddleY);
    };
}

export { startAIBot };
