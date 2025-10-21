#!/usr/bin/env python3
"""
Chemistry Card Game - An educational chemistry card game using Pygame
Based on periodic table elements and chemical reactions
"""

import pygame
import json
import random
import sys
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
FPS = 60

# Colors - Professional periodic table themed palette
COLORS = {
    'background': (15, 23, 42),  # Dark blue-gray
    'ui_bg': (30, 41, 59),
    'card_bg': (248, 250, 252),
    'text': (241, 245, 249),
    'text_dark': (15, 23, 42),
    'accent': (59, 130, 246),  # Blue
    'accent_hover': (96, 165, 250),
    'success': (34, 197, 94),  # Green
    'warning': (251, 146, 60),  # Orange
    'danger': (239, 68, 68),  # Red
    'floor': (168, 85, 247),  # Purple
    'selected': (250, 204, 21),  # Yellow
    'metal': (148, 163, 184),  # Blue-gray
    'nonmetal': (134, 239, 172),  # Light green
    'metalloid': (253, 224, 71),  # Yellow
    'halogen': (251, 146, 60),  # Orange
    'alkali_metal': (239, 68, 68),  # Red
    'alkaline_earth': (245, 158, 11),  # Amber
    'transition_metal': (168, 85, 247),  # Purple
    'post_transition': (192, 132, 252),  # Light purple
    'noble_gas': (59, 130, 246),  # Blue
}

# Element category colors
CATEGORY_COLORS = {
    'metal': COLORS['metal'],
    'nonmetal': COLORS['nonmetal'],
    'metalloid': COLORS['metalloid'],
    'post-transition metal': COLORS['post_transition'],
}

FAMILY_COLORS = {
    'alkali metal': COLORS['alkali_metal'],
    'alkaline earth metal': COLORS['alkaline_earth'],
    'transition metal': COLORS['transition_metal'],
    'halogen': COLORS['halogen'],
    'chalcogen': (124, 58, 237),  # Violet
    'pnictogen': (6, 182, 212),  # Cyan
    'carbon group': (16, 185, 129),  # Emerald
    'boron group': (236, 72, 153),  # Pink
    '-': COLORS['nonmetal'],
}

# Atomic numbers for all elements in the game
ATOMIC_NUMBERS = {
    'H': 1, 'Li': 3, 'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9,
    'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15, 'S': 16, 'Cl': 17,
    'K': 19, 'Ca': 20, 'Fe': 26, 'Cu': 29, 'Zn': 30, 'Br': 35,
    'Ag': 47, 'I': 53
}


class AnimationType(Enum):
    """Animation types for visual effects"""
    SLIDE = 1
    FADE = 2
    SCALE = 3
    GLOW = 4


@dataclass
class Animation:
    """Animation data"""
    target: any
    anim_type: AnimationType
    start_val: float
    end_val: float
    current_val: float
    duration: float
    elapsed: float = 0.0

    def update(self, dt: float) -> bool:
        """Update animation, return True if complete"""
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.current_val = self.end_val
            return True

        # Ease out quad
        t = self.elapsed / self.duration
        t = 1 - (1 - t) * (1 - t)
        self.current_val = self.start_val + (self.end_val - self.start_val) * t
        return False


@dataclass
class Card:
    """Represents an element card"""
    symbol: str
    name: str
    group: int
    family: str
    category: str
    binary_partners: List[str]
    atomic_number: int

    def get_color(self) -> Tuple[int, int, int]:
        """Get card color based on family/category"""
        if self.family in FAMILY_COLORS:
            return FAMILY_COLORS[self.family]
        return CATEGORY_COLORS.get(self.category, COLORS['card_bg'])

    def __hash__(self):
        return hash(self.symbol)

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.symbol == other.symbol
        return False

    def __repr__(self):
        return f"Card({self.symbol})"


class Deck:
    """Manages the deck of cards"""

    def __init__(self, game_data: dict):
        self.all_cards: List[Card] = []
        self.draw_pile: List[Card] = []
        self.discard_pile: List[Card] = []

        # Load cards from game data
        for elem in game_data['elements']:
            for _ in range(elem['count']):
                card = Card(
                    symbol=elem['symbol'],
                    name=elem['name'],
                    group=elem['group'],
                    family=elem['family'],
                    category=elem['category'],
                    binary_partners=elem['binary_partners'],
                    atomic_number=ATOMIC_NUMBERS[elem['symbol']]
                )
                self.all_cards.append(card)

    def shuffle(self):
        """Shuffle the draw pile"""
        random.shuffle(self.draw_pile)

    def reset(self):
        """Reset deck for new game"""
        self.draw_pile = self.all_cards.copy()
        self.discard_pile = []
        self.shuffle()

    def draw(self) -> Optional[Card]:
        """Draw a card from the deck"""
        if not self.draw_pile:
            # Reshuffle discard pile (keeping floor card out)
            if self.discard_pile:
                self.draw_pile = self.discard_pile.copy()
                self.discard_pile = []
                self.shuffle()

        if self.draw_pile:
            return self.draw_pile.pop()
        return None

    def discard(self, card: Card):
        """Add card to discard pile"""
        self.discard_pile.append(card)


class ReactionValidator:
    """Validates card plays and reactions"""

    def __init__(self, game_data: dict):
        # Build reaction sets for fast lookup
        self.binary_reactions: Set[frozenset] = set()
        self.ternary_reactions: Set[frozenset] = set()
        self.quaternary_reactions: Set[frozenset] = set()

        for combo in game_data['combos']['binary']:
            self.binary_reactions.add(frozenset(combo['elements']))

        for combo in game_data['combos']['ternary']:
            self.ternary_reactions.add(frozenset(combo['elements']))

        for combo in game_data['combos']['quaternary']:
            self.quaternary_reactions.add(frozenset(combo['elements']))

    def is_group_match(self, card: Card, floor_card: Card) -> bool:
        """Check if card matches floor's group"""
        return card.group == floor_card.group

    def is_valid_reaction(self, cards: List[Card], floor_card: Card) -> Tuple[bool, str]:
        """
        Check if cards + floor form a valid reaction
        Returns (valid, combo_type)
        """
        all_elements = [floor_card] + cards

        # Check for duplicates
        symbols = [c.symbol for c in all_elements]
        if len(symbols) != len(set(symbols)):
            return False, ""

        # Create element set
        element_set = frozenset(symbols)

        # Check against reaction lists
        if len(element_set) == 2 and element_set in self.binary_reactions:
            return True, "Binary"
        elif len(element_set) == 3 and element_set in self.ternary_reactions:
            return True, "Ternary"
        elif len(element_set) == 4 and element_set in self.quaternary_reactions:
            return True, "Quaternary"

        return False, ""

    def get_reaction_example(self, cards: List[Card], floor_card: Card, game_data: dict) -> str:
        """Get example compound name for a reaction"""
        all_elements = sorted([c.symbol for c in cards] + [floor_card.symbol])
        element_set = frozenset(all_elements)

        # Search for example in combos
        for category in ['binary', 'ternary', 'quaternary']:
            for combo in game_data['combos'][category]:
                if frozenset(combo['elements']) == element_set:
                    return combo['example']

        return ""


class AIPlayer:
    """AI opponent logic"""

    def __init__(self, validator: ReactionValidator):
        self.validator = validator

    def choose_play(self, hand: List[Card], floor_card: Card) -> Tuple[str, List[Card]]:
        """
        Choose best play for AI
        Returns (play_type, cards_to_play)
        play_type: 'reaction', 'group', or 'draw'
        """
        # Try to find best reaction (prioritize larger reactions)
        best_reaction = None
        best_reaction_size = 0

        # Try all combinations of 1-3 cards
        for size in range(1, 4):
            for i in range(len(hand)):
                if size == 1:
                    combo = [hand[i]]
                    is_valid, combo_type = self.validator.is_valid_reaction(combo, floor_card)
                    if is_valid and size > best_reaction_size:
                        best_reaction = combo
                        best_reaction_size = size
                elif size == 2:
                    for j in range(i + 1, len(hand)):
                        combo = [hand[i], hand[j]]
                        is_valid, combo_type = self.validator.is_valid_reaction(combo, floor_card)
                        if is_valid and size > best_reaction_size:
                            best_reaction = combo
                            best_reaction_size = size
                elif size == 3:
                    for j in range(i + 1, len(hand)):
                        for k in range(j + 1, len(hand)):
                            combo = [hand[i], hand[j], hand[k]]
                            is_valid, combo_type = self.validator.is_valid_reaction(combo, floor_card)
                            if is_valid and size > best_reaction_size:
                                best_reaction = combo
                                best_reaction_size = size

        if best_reaction:
            return ('reaction', best_reaction)

        # Try group match - prefer high-connectivity cards
        connectivity_scores = []
        for card in hand:
            if self.validator.is_group_match(card, floor_card):
                # Score based on number of binary partners
                score = len(card.binary_partners)
                connectivity_scores.append((card, score))

        if connectivity_scores:
            # Play card with highest connectivity
            connectivity_scores.sort(key=lambda x: x[1], reverse=True)
            return ('group', [connectivity_scores[0][0]])

        # Must draw
        return ('draw', [])


class GameState:
    """Main game state manager"""

    def __init__(self, game_data: dict):
        self.game_data = game_data
        self.deck = Deck(game_data)
        self.validator = ReactionValidator(game_data)
        self.ai = AIPlayer(self.validator)

        self.player_hand: List[Card] = []
        self.ai_hand: List[Card] = []
        self.floor_card: Optional[Card] = None
        self.current_player = 'player'  # 'player' or 'ai'
        self.selected_cards: List[Card] = []
        self.game_over = False
        self.winner = None
        self.message = "Welcome! Select cards to play a reaction or match the group."
        self.waiting_for_floor_choice = False
        self.played_cards_for_floor: List[Card] = []

    def start_new_game(self):
        """Initialize a new game"""
        self.deck.reset()

        # Deal hands
        self.player_hand = [self.deck.draw() for _ in range(5)]
        self.ai_hand = [self.deck.draw() for _ in range(5)]

        # Set floor card
        self.floor_card = self.deck.draw()

        # Random starting player
        self.current_player = random.choice(['player', 'ai'])

        self.selected_cards = []
        self.game_over = False
        self.winner = None
        self.waiting_for_floor_choice = False
        self.played_cards_for_floor = []
        self.message = f"{self.current_player.title()}'s turn!"

        # If AI starts, let it play
        if self.current_player == 'ai':
            return True  # Signal to process AI turn
        return False

    def select_card(self, card: Card):
        """Toggle card selection"""
        if card in self.selected_cards:
            self.selected_cards.remove(card)
        else:
            if len(self.selected_cards) < 3:  # Max 3 cards for reaction
                self.selected_cards.append(card)

    def try_play(self) -> bool:
        """
        Attempt to play selected cards
        Returns True if play was successful
        """
        if not self.selected_cards:
            self.message = "No cards selected!"
            return False

        # Try reaction first
        is_valid, combo_type = self.validator.is_valid_reaction(
            self.selected_cards, self.floor_card
        )

        if is_valid:
            example = self.validator.get_reaction_example(
                self.selected_cards, self.floor_card, self.game_data
            )
            self.message = f"{combo_type} reaction! {example}"

            # Remove cards from hand
            for card in self.selected_cards:
                self.player_hand.remove(card)

            # Discard old floor
            self.deck.discard(self.floor_card)

            # Need to choose new floor from played cards
            if len(self.selected_cards) == 1:
                self.floor_card = self.selected_cards[0]
                self.selected_cards = []
                self.check_win()
                self.end_turn()
            else:
                # Multiple cards - need to choose
                self.waiting_for_floor_choice = True
                self.played_cards_for_floor = self.selected_cards.copy()
                self.selected_cards = []
                self.message += " - Choose new floor card!"

            return True

        # Try single group match
        if len(self.selected_cards) == 1:
            card = self.selected_cards[0]
            if self.validator.is_group_match(card, self.floor_card):
                self.message = f"Group {card.group} match!"

                # Remove from hand
                self.player_hand.remove(card)

                # Old floor to discard
                self.deck.discard(self.floor_card)

                # Played card becomes new floor
                self.floor_card = card
                self.selected_cards = []

                self.check_win()
                self.end_turn()
                return True

        self.message = "Invalid play! Try a reaction or group match."
        return False

    def choose_floor_card(self, card: Card):
        """Choose new floor card after reaction"""
        if card in self.played_cards_for_floor:
            self.floor_card = card
            # Discard other played cards
            for c in self.played_cards_for_floor:
                if c != card:
                    self.deck.discard(c)

            self.waiting_for_floor_choice = False
            self.played_cards_for_floor = []
            self.check_win()
            self.end_turn()

    def player_draw(self):
        """Player draws a card"""
        card = self.deck.draw()
        if card:
            self.player_hand.append(card)
            self.message = f"Drew {card.symbol} ({card.name})"
            self.end_turn()
        else:
            self.message = "Deck is empty!"
            self.check_stalemate()

    def end_turn(self):
        """Switch to next player"""
        self.current_player = 'ai' if self.current_player == 'player' else 'player'

    def check_win(self):
        """Check if someone won"""
        # Win by emptying hand
        if len(self.player_hand) == 0:
            self.game_over = True
            self.winner = 'player'
            self.message = "You win! Hand emptied!"
        elif len(self.ai_hand) == 0:
            self.game_over = True
            self.winner = 'ai'
            self.message = "AI wins! Hand emptied!"
        # Lose by having 10+ cards
        elif len(self.player_hand) >= 10:
            self.game_over = True
            self.winner = 'ai'
            self.message = "You lose! Too many cards (10+)!"
        elif len(self.ai_hand) >= 10:
            self.game_over = True
            self.winner = 'player'
            self.message = "You win! AI has too many cards (10+)!"

    def check_stalemate(self):
        """Check for stalemate"""
        if not self.deck.draw_pile and not self.deck.discard_pile:
            self.game_over = True
            if len(self.player_hand) < len(self.ai_hand):
                self.winner = 'player'
                self.message = "Stalemate! You win with fewer cards!"
            elif len(self.ai_hand) < len(self.player_hand):
                self.winner = 'ai'
                self.message = "Stalemate! AI wins with fewer cards!"
            else:
                self.winner = None
                self.message = "Stalemate! It's a draw!"

    def process_ai_turn(self) -> bool:
        """
        Process AI's turn
        Returns True if AI needs more time (animations)
        """
        if self.game_over:
            return False

        # AI chooses play
        play_type, cards = self.ai.choose_play(self.ai_hand, self.floor_card)

        if play_type == 'reaction':
            is_valid, combo_type = self.validator.is_valid_reaction(cards, self.floor_card)
            example = self.validator.get_reaction_example(cards, self.floor_card, self.game_data)

            card_names = ', '.join([c.symbol for c in cards])
            self.message = f"AI played {combo_type} reaction: {card_names} ({example})"

            # Remove from AI hand
            for card in cards:
                self.ai_hand.remove(card)

            # Discard old floor
            self.deck.discard(self.floor_card)

            # Choose new floor (AI picks last card)
            self.floor_card = cards[-1]

            # Discard other played cards
            for card in cards[:-1]:
                self.deck.discard(card)

        elif play_type == 'group':
            card = cards[0]
            self.message = f"AI matched Group {card.group} with {card.symbol}"

            # Remove from hand
            self.ai_hand.remove(card)

            # Old floor to discard
            self.deck.discard(self.floor_card)

            # New floor
            self.floor_card = card

        else:  # draw
            card = self.deck.draw()
            if card:
                self.ai_hand.append(card)
                self.message = f"AI drew a card"
            else:
                self.message = "Deck is empty!"
                self.check_stalemate()

        self.check_win()

        if not self.game_over:
            self.end_turn()

        return True


class Button:
    """UI Button"""

    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = COLORS['accent_hover']
        self.is_hovered = False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """Draw button"""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLORS['text'], self.rect, 2, border_radius=8)

        text_surf = font.render(self.text, True, COLORS['text'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events, return True if clicked"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False


class CardSprite:
    """Visual representation of a card"""

    def __init__(self, card: Card, x: int, y: int, width: int = 100, height: int = 140):
        self.card = card
        self.rect = pygame.Rect(x, y, width, height)
        self.base_y = y
        self.is_hovered = False
        self.is_selected = False
        self.hover_offset = -10

    def draw(self, screen: pygame.Surface, font_large: pygame.font.Font, font_small: pygame.font.Font):
        """Draw the card"""
        # Adjust position for hover
        y_pos = self.rect.y
        if self.is_hovered and not self.is_selected:
            y_pos += self.hover_offset

        draw_rect = pygame.Rect(self.rect.x, y_pos, self.rect.width, self.rect.height)

        # Background
        bg_color = self.card.get_color()
        pygame.draw.rect(screen, bg_color, draw_rect, border_radius=8)

        # Border
        border_color = COLORS['selected'] if self.is_selected else COLORS['text_dark']
        border_width = 4 if self.is_selected else 2
        pygame.draw.rect(screen, border_color, draw_rect, border_width, border_radius=8)

        # Atomic number (small, top left corner)
        atomic_num_surf = font_small.render(str(self.card.atomic_number), True, COLORS['text_dark'])
        screen.blit(atomic_num_surf, (draw_rect.x + 5, draw_rect.y + 5))

        # Symbol (large)
        symbol_surf = font_large.render(self.card.symbol, True, COLORS['text_dark'])
        symbol_rect = symbol_surf.get_rect(center=(draw_rect.centerx, draw_rect.y + 45))
        screen.blit(symbol_surf, symbol_rect)

        # Name (small)
        name_surf = font_small.render(self.card.name, True, COLORS['text_dark'])
        name_rect = name_surf.get_rect(center=(draw_rect.centerx, draw_rect.y + 90))
        screen.blit(name_surf, name_rect)

        # Group number
        group_surf = font_small.render(f"Grp {self.card.group}", True, COLORS['text_dark'])
        group_rect = group_surf.get_rect(center=(draw_rect.centerx, draw_rect.y + 115))
        screen.blit(group_surf, group_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events, return True if clicked"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False


class ChemistryCardGame:
    """Main game class"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chemistry Card Game")
        self.clock = pygame.time.Clock()

        # UI Fonts (larger for readability, 20% smaller than 3x)
        self.font_large = pygame.font.Font(None, 115)
        self.font_medium = pygame.font.Font(None, 77)
        self.font_small = pygame.font.Font(None, 48)
        self.font_tiny = pygame.font.Font(None, 38)

        # Card-specific fonts (kept small)
        self.card_symbol_font = pygame.font.Font(None, 48)
        self.card_text_font = pygame.font.Font(None, 16)

        # Load game data
        with open('game_info.json', 'r') as f:
            self.game_data = json.load(f)

        # Game state
        self.state = GameState(self.game_data)

        # UI Elements
        self.card_sprites: List[CardSprite] = []
        self.floor_sprite: Optional[CardSprite] = None
        self.ai_card_backs: List[pygame.Rect] = []

        # Buttons - repositioned for better separation
        # Action buttons at bottom, well-separated from hand and each other
        button_y = SCREEN_HEIGHT - 60
        self.clear_button = Button(50, button_y, 180, 50,
                                    "Clear", COLORS['danger'])
        self.draw_button = Button(280, button_y, 180, 50,
                                   "Draw", COLORS['accent'])
        self.play_button = Button(510, button_y, 250, 50,
                                   "Play Cards", COLORS['success'])
        # New game button in top right corner
        self.new_game_button = Button(SCREEN_WIDTH - 220, 20, 200, 50,
                                       "New Game", COLORS['warning'])

        # Start game
        self.ai_turn_timer = 0
        self.ai_turn_delay = 1.5  # Seconds before AI plays

        needs_ai_turn = self.state.start_new_game()
        self.update_sprites()

        if needs_ai_turn:
            self.ai_turn_timer = self.ai_turn_delay

    def update_sprites(self):
        """Update card sprite positions"""
        # Player hand
        self.card_sprites = []
        hand_width = len(self.state.player_hand) * 110
        start_x = (SCREEN_WIDTH - hand_width) // 2

        for i, card in enumerate(self.state.player_hand):
            sprite = CardSprite(card, start_x + i * 110, SCREEN_HEIGHT - 300)
            sprite.is_selected = card in self.state.selected_cards
            self.card_sprites.append(sprite)

        # Floor card
        if self.state.floor_card:
            self.floor_sprite = CardSprite(self.state.floor_card,
                                          SCREEN_WIDTH // 2 - 50,
                                          SCREEN_HEIGHT // 2 - 70,
                                          100, 140)

        # AI card backs
        self.ai_card_backs = []
        ai_hand_width = len(self.state.ai_hand) * 110
        ai_start_x = (SCREEN_WIDTH - ai_hand_width) // 2

        for i in range(len(self.state.ai_hand)):
            rect = pygame.Rect(ai_start_x + i * 110, 200, 100, 140)
            self.ai_card_backs.append(rect)

        # Update floor choice sprites if waiting
        if self.state.waiting_for_floor_choice:
            self.card_sprites = []
            choice_width = len(self.state.played_cards_for_floor) * 110
            choice_x = (SCREEN_WIDTH - choice_width) // 2

            for i, card in enumerate(self.state.played_cards_for_floor):
                sprite = CardSprite(card, choice_x + i * 110, SCREEN_HEIGHT // 2 + 100)
                self.card_sprites.append(sprite)

    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Skip input if AI's turn
            if self.state.current_player == 'ai' and not self.state.game_over:
                continue

            # Handle floor choice
            if self.state.waiting_for_floor_choice:
                for sprite in self.card_sprites:
                    if sprite.handle_event(event):
                        self.state.choose_floor_card(sprite.card)
                        self.update_sprites()
                continue

            # Handle card selection
            for sprite in self.card_sprites:
                if sprite.handle_event(event):
                    self.state.select_card(sprite.card)
                    self.update_sprites()

            # Handle buttons
            if self.play_button.handle_event(event):
                if self.state.current_player == 'player' and not self.state.game_over:
                    if self.state.try_play():
                        self.update_sprites()
                        # Check if AI's turn now
                        if self.state.current_player == 'ai' and not self.state.game_over:
                            self.ai_turn_timer = self.ai_turn_delay

            if self.draw_button.handle_event(event):
                if self.state.current_player == 'player' and not self.state.game_over:
                    self.state.player_draw()
                    self.update_sprites()
                    # Check if AI's turn now
                    if self.state.current_player == 'ai' and not self.state.game_over:
                        self.ai_turn_timer = self.ai_turn_delay

            if self.clear_button.handle_event(event):
                if self.state.current_player == 'player':
                    self.state.selected_cards = []
                    self.update_sprites()

            if self.new_game_button.handle_event(event):
                needs_ai_turn = self.state.start_new_game()
                self.update_sprites()
                if needs_ai_turn:
                    self.ai_turn_timer = self.ai_turn_delay
                else:
                    self.ai_turn_timer = 0

        return True

    def update(self, dt: float):
        """Update game logic"""
        # Handle AI turn with delay
        if self.state.current_player == 'ai' and not self.state.game_over:
            if self.ai_turn_timer > 0:
                self.ai_turn_timer -= dt
                if self.ai_turn_timer <= 0:
                    self.state.process_ai_turn()
                    self.update_sprites()

    def draw(self):
        """Render everything"""
        # Background
        self.screen.fill(COLORS['background'])

        # Title
        title_text = "Chemistry Card Game"
        title_surf = self.font_large.render(title_text, True, COLORS['text'])
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(title_surf, title_rect)

        # Game info panel
        info_y = 80

        # Deck count
        deck_text = f"Deck: {len(self.state.deck.draw_pile)}"
        deck_surf = self.font_tiny.render(deck_text, True, COLORS['text'])
        self.screen.blit(deck_surf, (50, info_y))

        # Discard count
        discard_text = f"Discard: {len(self.state.deck.discard_pile)}"
        discard_surf = self.font_tiny.render(discard_text, True, COLORS['text'])
        self.screen.blit(discard_surf, (50, info_y + 60))

        # Player hand count
        player_count = f"Your cards: {len(self.state.player_hand)}"
        player_surf = self.font_tiny.render(player_count, True, COLORS['success'])
        self.screen.blit(player_surf, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 360))

        # AI hand count
        ai_count = f"AI cards: {len(self.state.ai_hand)}"
        ai_surf = self.font_tiny.render(ai_count, True, COLORS['danger'])
        self.screen.blit(ai_surf, (SCREEN_WIDTH - 300, 360))

        # Draw AI card backs
        for rect in self.ai_card_backs:
            pygame.draw.rect(self.screen, COLORS['ui_bg'], rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS['accent'], rect, 2, border_radius=8)

            # Draw "?" on back
            question_surf = self.font_large.render("?", True, COLORS['accent'])
            question_rect = question_surf.get_rect(center=rect.center)
            self.screen.blit(question_surf, question_rect)

        # Draw floor card
        if self.floor_sprite:
            # Glow effect for floor
            glow_rect = self.floor_sprite.rect.inflate(20, 20)
            pygame.draw.rect(self.screen, COLORS['floor'], glow_rect, 3, border_radius=10)

            self.floor_sprite.draw(self.screen, self.card_symbol_font, self.card_text_font)

        # Draw player cards or floor choice
        if self.state.waiting_for_floor_choice:
            # Floor choice prompt
            prompt = "Choose which card becomes the new floor:"
            prompt_surf = self.font_medium.render(prompt, True, COLORS['warning'])
            prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(prompt_surf, prompt_rect)

        for sprite in self.card_sprites:
            sprite.draw(self.screen, self.card_symbol_font, self.card_text_font)

        # Message box - positioned above buttons with larger fonts
        msg_bg = pygame.Rect(50, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 100, 80)
        pygame.draw.rect(self.screen, COLORS['ui_bg'], msg_bg, border_radius=8)
        pygame.draw.rect(self.screen, COLORS['accent'], msg_bg, 2, border_radius=8)

        # Word wrap message
        words = self.state.message.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if self.font_tiny.size(test_line)[0] < msg_bg.width - 40:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines[:2]):  # Max 2 lines
            msg_surf = self.font_tiny.render(line.strip(), True, COLORS['text'])
            self.screen.blit(msg_surf, (msg_bg.x + 20, msg_bg.y + 15 + i * 50))

        # Draw buttons
        if not self.state.waiting_for_floor_choice:
            self.play_button.draw(self.screen, self.font_small)
            self.draw_button.draw(self.screen, self.font_small)
            self.clear_button.draw(self.screen, self.font_small)

        self.new_game_button.draw(self.screen, self.font_small)

        # Turn indicator - beneath title
        turn_text = f"Current Turn: {self.state.current_player.upper()}"
        turn_color = COLORS['success'] if self.state.current_player == 'player' else COLORS['danger']
        turn_surf = self.font_medium.render(turn_text, True, turn_color)
        turn_rect = turn_surf.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.screen.blit(turn_surf, turn_rect)

        # Game over overlay
        if self.state.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(COLORS['background'])
            self.screen.blit(overlay, (0, 0))

            result_text = self.state.message
            result_surf = self.font_large.render(result_text, True,
                                                  COLORS['success'] if self.state.winner == 'player'
                                                  else COLORS['danger'] if self.state.winner == 'ai'
                                                  else COLORS['warning'])
            result_rect = result_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(result_surf, result_rect)

            instruction_surf = self.font_small.render("Click 'New Game' to play again",
                                                      True, COLORS['text'])
            instruction_rect = instruction_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                                  SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(instruction_surf, instruction_rect)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds

            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()


def main():
    """Entry point"""
    game = ChemistryCardGame()
    game.run()


if __name__ == "__main__":
    main()
