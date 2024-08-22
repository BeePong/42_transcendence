# AI-Algo

**Purpose**: To handle movements and decisions made by AI opponent playing BeePong

## Interactions with the game

### AI view of game state

- **Constraints:** game state monitoring can be done only once per second.
- **AI requires inteactions with server's API via asynchronous updates to get:**
    - ball's current:
        - position 
        - direction
    - AI's current paddle position

### AI movements to hit the ball

- **Constraints:** AI must replicate human behaviour, it's movements simulate keyboard input.
- **AI's movements requires:**
    - Estimation of ball location when passing AI's side line
    - Movement to estimated impact position
        - May require to artificially produce artifacts in behavior to not be overwhemingly good.
        - Requires to simulate up and down key presses

.. to be continued
