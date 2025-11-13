# Chemistry War

A simple card battle game spin-off of Chemistry Uno! Battle against an AI opponent using the power of atomic numbers.

## About

Chemistry War is a simplified chemistry-themed card game based on the classic "War" card game. Instead of traditional card values, elements battle using their atomic numbers!

## How to Play

### Setup
- The 35-card deck is shuffled and split evenly between you and the AI
- Each player gets approximately 17-18 cards face-down

### Gameplay
1. Click the **"Battle!"** button to draw cards
2. Both you and the AI flip the top card from your decks
3. The element with the **higher atomic number wins**!
4. The winner takes both cards and adds them to the bottom of their deck
5. Continue battling until one player collects all the cards

### Special Rules
- **Tie (War)**: When both cards have the same atomic number, it's a WAR! The prize pile grows and the next battle winner takes all
- **Same Family Bonus**: When both elements are from the same chemical family, it creates an exciting match-up!

### Victory Conditions
- **Win**: Collect all 35 cards
- **Lose**: Run out of cards

## Running the Game

### Option 1: Play in Browser (Recommended)
```bash
# Install pygbag
pip install pygbag

# Run the game in browser
pygbag chemistry_war.py
```

Then open your browser to `http://localhost:8000`

### Option 2: Run Locally (Desktop)
```bash
# Install pygame
pip install pygame

# Run the game
python3 chemistry_war.py
```

## Educational Value

Chemistry War teaches:
- **Atomic numbers** of common elements
- **Element families** and their relationships
- **Periodic table organization**
- Quick element recognition by symbol and name
- Probability and strategic thinking

## Element Examples

The game includes elements from across the periodic table:
- **Low atomic numbers**: H (1), Li (3), C (6), O (8)
- **Medium atomic numbers**: Na (11), Mg (12), Ca (20), Fe (26)
- **High atomic numbers**: Cu (29), Zn (30), Br (35), Ag (47), I (53)

## Strategy Tips

1. **Know your numbers**: Memorizing atomic numbers helps you predict battle outcomes
2. **Count cards**: Keep track of approximately how many cards each player has
3. **Element families matter**: Recognizing families helps you understand which elements are likely to appear together

## Comparison with Chemistry Uno

| Feature | Chemistry Uno | Chemistry War |
|---------|--------------|---------------|
| Complexity | Complex | Simple |
| Game Duration | 10-15 minutes | 5-10 minutes |
| Learning Curve | Moderate | Easy |
| Focus | Reactions & Groups | Atomic Numbers |
| Strategic Depth | High | Low |
| Educational Value | Compound Formation | Atomic Structure |

## Credits

Spin-off of the Chemistry Card Game
Based on `game_info.json` element data
Built with Python and Pygame
