# Chemistry Card Game

An educational card game based on chemical elements and reactions, built with Pygame.

## Features

- **34-card deck** with 22 element types from the periodic table
- **Smart AI opponent** that prioritizes reactions and strategic plays
- **Beautiful periodic table-themed visuals** with color-coded element families
- **Cards display:** element symbol, name, atomic number, and periodic group
- **Two types of plays:**
  - **Group Match:** Play a card matching the floor card's periodic group
  - **Reaction:** Combine 2-4 elements to form real chemical compounds (binary, ternary, or quaternary)
- **Educational gameplay** teaches chemical families and compound formation
- **Smooth animations** and intuitive UI
- **Strategic race** to empty your hand while avoiding the 10-card penalty

## How to Play

### Objective
Be the first player to play all cards from your hand!

### Game Setup
- Each player starts with 5 cards
- One card is placed face-up as the "floor card"
- A random player goes first

### On Your Turn
You can either:

1. **Play Cards (Group Match):**
   - Play ONE card that shares the same periodic group number as the floor card
   - The played card becomes the new floor
   - No penalty to opponent

2. **Play Cards (Reaction):**
   - Select 1-3 cards from your hand that, together with the floor card, form a valid chemical compound
   - Valid reactions include:
     - **Binary:** 2 elements (e.g., Na + Cl = NaCl)
     - **Ternary:** 3 elements (e.g., Na + H + O = NaOH)
     - **Quaternary:** 4 elements (e.g., Ca + H + O + P = calcium phosphate)
   - After a reaction, choose which played card becomes the new floor
   - Reactions allow you to play multiple cards at once, reducing your hand faster

3. **Draw a Card:**
   - If you can't or don't want to play, draw one card
   - Your turn ends

### Controls

- **Click cards** in your hand to select them (yellow border = selected)
- **Play Cards button:** Attempt to play your selection
- **Draw button:** Draw a card from the deck
- **Clear button:** Deselect all cards
- **New Game button:** Start a fresh game

### Winning

- **Win:** First player to reach 0 cards wins immediately
- **Loss:** If your hand reaches 10 or more cards, you lose immediately
- **Stalemate:** If deck runs out and no one can play:
  - Player with fewer cards wins
  - Tie = Draw

### Valid Reactions

The game includes real chemical compounds:
- **Binary compounds:** NaCl, H2O, CO2, Fe2O3, etc.
- **Ternary compounds:** NaOH (hydroxides), NaNO3 (nitrates), H2SO4 (acids), etc.
- **Quaternary compounds:** CH3COOH derivatives, complex salts, etc.

All reactions are validated against real chemistry!

## Installation

### Requirements
- Python 3.7+
- Pygame

### Install Dependencies
```bash
pip install pygame
```

### Run the Game
```bash
python3 chemistry_card_game.py
```

## Game Elements

The deck includes elements from various periodic table families:

- **Alkali Metals** (Red): Li, Na, K
- **Alkaline Earth Metals** (Orange): Mg, Ca
- **Transition Metals** (Purple): Fe, Cu, Zn, Ag
- **Halogens** (Orange): F, Cl, Br, I
- **Chalcogens** (Violet): O, S
- **Other Nonmetals** (Green): H, C, N, P, B, Si

High-connectivity elements (H, O, Cl, C, N, S, Na, K, Ca, Fe, Cu, Zn) appear twice in the deck for better gameplay balance.

## Strategy Tips

1. **Watch your hand size** - reaching 10 cards means instant loss! Use reactions strategically to reduce your hand
2. **Save high-connectivity cards** (O, H, Cl) - they can form many reactions
3. **Reactions are powerful** - they let you play multiple cards at once, helping you empty your hand faster
4. **Plan your floor card** - after a reaction, choose a floor that limits opponent's options
5. **Monitor both card counts** - race to empty your hand while avoiding the 10-card penalty
6. **Know your groups:**
   - Group 1: H, Li, Na, K
   - Group 2: Mg, Ca
   - Group 13: B, Al
   - Group 14: C, Si
   - Group 15: N, P
   - Group 16: O, S
   - Group 17: F, Cl, Br, I

## Educational Value

This game teaches:
- Periodic table groups and families
- Element properties and categories
- Common chemical compounds
- Binary, ternary, and quaternary compound formation
- Strategic thinking and planning

## Credits

Game design based on `game_info.json` specification.
Built with Python and Pygame.
