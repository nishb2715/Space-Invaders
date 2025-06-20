# Space Invaders Game - Enhanced Edition

A classic Space Invaders-style game built with Python and Pygame, featuring modern enhancements.

## Features

### Core Gameplay
- **Player-controlled spaceship**: Move with arrow keys, shoot with spacebar
- **Enemy invaders**: Grid of enemies that move horizontally and drop down when hitting screen edges
- **Collision detection**: Bullets destroy enemies, enemy bullets can hit the player
- **Score system**: Earn 10 points for each enemy destroyed
- **Sound effects**: Shooting, hit, and game over sounds (requires numpy)
- **Game over conditions**: Win by destroying all enemies, lose if enemies reach you or you're hit
- **Restart functionality**: Press R to restart after game over

### New Enhanced Features
- **Scrolling starfield background**: Dynamic animated star field for immersive space atmosphere
- **Power-up system**: Three different power-ups with visual effects and timed duration
  - **Triple Shot** (Cyan): Fires three bullets at once in a spread pattern
  - **Rapid Fire** (Orange): Increases firing rate significantly
  - **Shield** (Purple): Blocks enemy bullets and provides visual protection
- **Power-up mechanics**: 30% chance to drop when destroying enemies, lasts 10 seconds
- **Enhanced visuals**: Player ship changes color based on active power-up
- **Power-up status display**: Shows active power-up and remaining time
