# Quick Start Guide

## Play in Browser (Easiest!)

### 1. Install Pygbag
```bash
pip install pygbag
```

### 2. Run the Game
```bash
pygbag chemistry_card_game.py
```

### 3. Open Browser
Navigate to: `http://localhost:8000`

**That's it!** The game will load in your browser.

---

## Play on Desktop

### 1. Install Pygame
```bash
pip install pygame
```

### 2. Run the Game
```bash
python3 chemistry_card_game.py
```

---

## Game Controls

- **Click cards** to select them (yellow border = selected)
- **Play Cards** button - Play your selected cards
- **Draw** button - Draw a card from the deck
- **Clear** button - Deselect all cards
- **New Game** button - Start a fresh game

---

## Quick Rules

### Objective
Empty your hand before the AI does!

### How to Play
Each turn you can either:

1. **Group Match**: Play 1 card matching the floor's periodic group
2. **Reaction**: Play 1-3 cards that form a chemical compound with the floor
3. **Draw**: Draw 1 card if you can't play

### Win Conditions
- ✅ **Win**: Empty your hand (0 cards)
- ❌ **Lose**: Reach 10+ cards
- 🤝 **Stalemate**: Fewer cards wins when deck runs out

---

## Example Reactions

- **Binary**: Na + Cl → NaCl (table salt)
- **Ternary**: Na + O + H → NaOH (sodium hydroxide)
- **Quaternary**: Ca + H + O + P → Ca(H₂PO₄)₂ (calcium phosphate)

All reactions are real chemistry validated!

---

## Tips

1. **Oxygen (O)** appears 5× in the deck - save it for powerful reactions!
2. **Hydrogen (H)** appears 3× - combines with many elements
3. Watch your hand size - 10 cards = instant loss!
4. Use reactions to play multiple cards at once

---

## Need Help?

- Full rules: See `README.md`
- Web deployment: See `WEB_DEPLOYMENT.md`
- Game configuration: See `game_info.json`

Enjoy learning chemistry! 🧪
