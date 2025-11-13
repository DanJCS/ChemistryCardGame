#!/usr/bin/env python3
"""
Chemistry War - A simple card battle game using elements
Based on the classic card game "War" with chemistry elements
"""

import pygame
import json
import random
import sys
import asyncio
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FPS = 60

# Colors - Periodic table themed palette
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
    'purple': (168, 85, 247),
    'selected': (250, 204, 21),  # Yellow
    'metal': (148, 163, 184),
    'nonmetal': (134, 239, 172),
    'metalloid': (253, 224, 71),
    'halogen': (251, 146, 60),
    'alkali_metal': (239, 68, 68),
    'alkaline_earth': (245, 158, 11),
    'transition_metal': (168, 85, 247),
    'post_transition': (192, 132, 252),
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
    'chalcogen': (124, 58, 237),
    'pnictogen': (6, 182, 212),
    'carbon group': (16, 185, 129),
    'boron group': (236, 72, 153),
    '-': COLORS['nonmetal'],
}

# Atomic numbers for all elements
ATOMIC_NUMBERS = {
    'H': 1, 'Li': 3, 'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9,
    'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15, 'S': 16, 'Cl': 17,
    'K': 19, 'Ca': 20, 'Fe': 26, 'Cu': 29, 'Zn': 30, 'Br': 35,
    'Ag': 47, 'I': 53
}


@dataclass
class Card:
    """Represents an element card"""
    symbol: str
    name: str
    group: int
    family: str
    category: str
    atomic_number: int

    def get_color(self) -> Tuple[int, int, int]:
        """Get card color based on family/category"""
        if self.family in FAMILY_COLORS:
            return FAMILY_COLORS[self.family]
        return CATEGORY_COLORS.get(self.category, COLORS['card_bg'])

    def __repr__(self):
        return f"{self.symbol}({self.atomic_number})"


class GameState(Enum):
    """Game states"""
    READY = 1
    BATTLE = 2
    RESULT = 3
    GAME_OVER = 4


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
    def __init__(self, card: Optional[Card], x: int, y: int, width: int = 120, height: int = 160):
        self.card = card
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen: pygame.Surface, font_large: pygame.font.Font, font_small: pygame.font.Font,
             face_up: bool = True):
        """Draw the card"""
        if not self.card:
            # Draw card back
            pygame.draw.rect(screen, COLORS['ui_bg'], self.rect, border_radius=8)
            pygame.draw.rect(screen, COLORS['accent'], self.rect, 2, border_radius=8)

            # Draw "?"
            question_surf = font_large.render("?", True, COLORS['accent'])
            question_rect = question_surf.get_rect(center=self.rect.center)
            screen.blit(question_surf, question_rect)
            return

        if not face_up:
            # Draw card back
            pygame.draw.rect(screen, COLORS['ui_bg'], self.rect, border_radius=8)
            pygame.draw.rect(screen, COLORS['accent'], self.rect, 2, border_radius=8)
            return

        # Background
        bg_color = self.card.get_color()
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLORS['text_dark'], self.rect, 2, border_radius=8)

        # Atomic number (small, top left)
        atomic_num_surf = font_small.render(str(self.card.atomic_number), True, COLORS['text_dark'])
        screen.blit(atomic_num_surf, (self.rect.x + 8, self.rect.y + 8))

        # Symbol (large, centered)
        symbol_surf = font_large.render(self.card.symbol, True, COLORS['text_dark'])
        symbol_rect = symbol_surf.get_rect(center=(self.rect.centerx, self.rect.y + 60))
        screen.blit(symbol_surf, symbol_rect)

        # Name (small, below symbol)
        name_surf = font_small.render(self.card.name, True, COLORS['text_dark'])
        name_rect = name_surf.get_rect(center=(self.rect.centerx, self.rect.y + 110))
        screen.blit(name_surf, name_rect)

        # Group number (bottom)
        group_surf = font_small.render(f"Group {self.card.group}", True, COLORS['text_dark'])
        group_rect = group_surf.get_rect(center=(self.rect.centerx, self.rect.y + 135))
        screen.blit(group_surf, group_rect)


class ChemistryWarGame:
    """Main game class for Chemistry War"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chemistry War")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_title = pygame.font.Font(None, 90)
        self.font_large = pygame.font.Font(None, 60)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)
        self.card_symbol_font = pygame.font.Font(None, 48)
        self.card_text_font = pygame.font.Font(None, 18)

        # Load game data
        with open('game_info.json', 'r') as f:
            game_data = json.load(f)

        # Create deck from game data
        self.all_cards: List[Card] = []
        for elem in game_data['elements']:
            for _ in range(elem['count']):
                card = Card(
                    symbol=elem['symbol'],
                    name=elem['name'],
                    group=elem['group'],
                    family=elem['family'],
                    category=elem['category'],
                    atomic_number=ATOMIC_NUMBERS[elem['symbol']]
                )
                self.all_cards.append(card)

        # Game state
        self.state = GameState.READY
        self.player_deck: List[Card] = []
        self.ai_deck: List[Card] = []
        self.player_card: Optional[Card] = None
        self.ai_card: Optional[Card] = None
        self.prize_pile: List[Card] = []
        self.message = "Welcome to Chemistry War! Click 'Battle' to draw cards."
        self.result_message = ""
        self.game_over = False
        self.winner = None

        # Animation timer
        self.animation_timer = 0
        self.animation_duration = 2.0  # seconds

        # Buttons
        self.battle_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 100, 300, 60,
                                     "Battle!", COLORS['success'])
        self.new_game_button = Button(SCREEN_WIDTH - 220, 20, 200, 50,
                                       "New Game", COLORS['warning'])
        self.play_again_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100, 300, 60,
                                        "Play Again", COLORS['success'])

        # Card sprites
        self.player_card_sprite: Optional[CardSprite] = None
        self.ai_card_sprite: Optional[CardSprite] = None

        # Start game
        self.start_new_game()

    def start_new_game(self):
        """Initialize a new game"""
        # Shuffle deck
        deck = self.all_cards.copy()
        random.shuffle(deck)

        # Split deck in half
        mid = len(deck) // 2
        self.player_deck = deck[:mid]
        self.ai_deck = deck[mid:]

        self.player_card = None
        self.ai_card = None
        self.prize_pile = []
        self.state = GameState.READY
        self.message = "Welcome to Chemistry War! Click 'Battle' to draw cards."
        self.result_message = ""
        self.game_over = False
        self.winner = None
        self.animation_timer = 0

    def draw_cards(self):
        """Draw cards for battle"""
        if not self.player_deck or not self.ai_deck:
            self.check_game_over()
            return

        self.player_card = self.player_deck.pop(0)
        self.ai_card = self.ai_deck.pop(0)

        # Add to prize pile
        self.prize_pile.append(self.player_card)
        self.prize_pile.append(self.ai_card)

        # Create card sprites
        self.player_card_sprite = CardSprite(self.player_card, SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 80)
        self.ai_card_sprite = CardSprite(self.ai_card, SCREEN_WIDTH // 2 + 130, SCREEN_HEIGHT // 2 - 80)

        self.state = GameState.BATTLE
        self.animation_timer = self.animation_duration

    def resolve_battle(self):
        """Resolve the battle and award cards"""
        if not self.player_card or not self.ai_card:
            return

        player_power = self.player_card.atomic_number
        ai_power = self.ai_card.atomic_number

        # Bonus: Same family gives +5 atomic number
        family_bonus = ""
        if self.player_card.family == self.ai_card.family and self.player_card.family != '-':
            self.result_message = f"Both are {self.player_card.family}s! Atomic numbers: "
        else:
            self.result_message = "Atomic numbers: "

        self.result_message += f"{self.player_card.symbol}={player_power} vs {self.ai_card.symbol}={ai_power}"

        # Determine winner
        if player_power > ai_power:
            self.message = f"You win! {self.player_card.symbol} ({player_power}) beats {self.ai_card.symbol} ({ai_power})"
            self.player_deck.extend(self.prize_pile)
            random.shuffle(self.player_deck)
        elif ai_power > player_power:
            self.message = f"AI wins! {self.ai_card.symbol} ({ai_power}) beats {self.player_card.symbol} ({player_power})"
            self.ai_deck.extend(self.prize_pile)
            random.shuffle(self.ai_deck)
        else:
            # War! (tie)
            self.message = f"WAR! Both have {player_power}! Prize pile grows..."
            # In a real war, you'd draw more cards, but for simplicity, we'll just continue
            # The prize pile keeps growing and winner of next battle takes all

        self.prize_pile = []
        self.state = GameState.RESULT

        # Check for game over
        self.check_game_over()

    def check_game_over(self):
        """Check if game is over"""
        if len(self.player_deck) == 0:
            self.game_over = True
            self.winner = 'ai'
            self.message = "AI wins! You ran out of cards!"
        elif len(self.ai_deck) == 0:
            self.game_over = True
            self.winner = 'player'
            self.message = "You win! AI ran out of cards!"

    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Handle buttons
            if self.battle_button.handle_event(event):
                if self.state == GameState.READY:
                    self.draw_cards()
                elif self.state == GameState.RESULT:
                    self.state = GameState.READY
                    self.draw_cards()

            if self.new_game_button.handle_event(event):
                self.start_new_game()

            if self.play_again_button.handle_event(event):
                if self.game_over:
                    self.start_new_game()

        return True

    def update(self, dt: float):
        """Update game logic"""
        if self.state == GameState.BATTLE and self.animation_timer > 0:
            self.animation_timer -= dt
            if self.animation_timer <= 0:
                self.resolve_battle()

    def draw(self):
        """Render everything"""
        # Background
        self.screen.fill(COLORS['background'])

        # Title
        title_surf = self.font_title.render("Chemistry War", True, COLORS['text'])
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_surf, title_rect)

        # Card counts
        player_count_text = f"Your Cards: {len(self.player_deck)}"
        player_count_surf = self.font_medium.render(player_count_text, True, COLORS['success'])
        self.screen.blit(player_count_surf, (50, 150))

        ai_count_text = f"AI Cards: {len(self.ai_deck)}"
        ai_count_surf = self.font_medium.render(ai_count_text, True, COLORS['danger'])
        self.screen.blit(ai_count_surf, (SCREEN_WIDTH - 300, 150))

        # Prize pile count
        if self.prize_pile:
            prize_text = f"Prize: {len(self.prize_pile)} cards"
            prize_surf = self.font_small.render(prize_text, True, COLORS['warning'])
            prize_rect = prize_surf.get_rect(center=(SCREEN_WIDTH // 2, 450))
            self.screen.blit(prize_surf, prize_rect)

        # Draw battle cards
        if self.state in [GameState.BATTLE, GameState.RESULT]:
            if self.player_card_sprite:
                self.player_card_sprite.draw(self.screen, self.card_symbol_font,
                                            self.card_text_font, face_up=True)
                # Label
                label_surf = self.font_medium.render("YOU", True, COLORS['success'])
                label_rect = label_surf.get_rect(center=(self.player_card_sprite.rect.centerx,
                                                         self.player_card_sprite.rect.y - 30))
                self.screen.blit(label_surf, label_rect)

            if self.ai_card_sprite:
                self.ai_card_sprite.draw(self.screen, self.card_symbol_font,
                                        self.card_text_font, face_up=True)
                # Label
                label_surf = self.font_medium.render("AI", True, COLORS['danger'])
                label_rect = label_surf.get_rect(center=(self.ai_card_sprite.rect.centerx,
                                                         self.ai_card_sprite.rect.y - 30))
                self.screen.blit(label_surf, label_rect)

            # VS text
            vs_surf = self.font_large.render("VS", True, COLORS['warning'])
            vs_rect = vs_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(vs_surf, vs_rect)

        # Message box
        msg_bg = pygame.Rect(50, SCREEN_HEIGHT - 220, SCREEN_WIDTH - 100, 100)
        pygame.draw.rect(self.screen, COLORS['ui_bg'], msg_bg, border_radius=8)
        pygame.draw.rect(self.screen, COLORS['accent'], msg_bg, 2, border_radius=8)

        # Message text (word wrap)
        words = self.message.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if self.font_small.size(test_line)[0] < msg_bg.width - 40:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines[:3]):  # Max 3 lines
            msg_surf = self.font_small.render(line.strip(), True, COLORS['text'])
            self.screen.blit(msg_surf, (msg_bg.x + 20, msg_bg.y + 15 + i * 30))

        # Rules box
        rules_box = pygame.Rect(SCREEN_WIDTH - 380, 220, 360, 180)
        pygame.draw.rect(self.screen, COLORS['ui_bg'], rules_box, border_radius=8)
        pygame.draw.rect(self.screen, COLORS['purple'], rules_box, 2, border_radius=8)

        rules_title = self.font_medium.render("Rules:", True, COLORS['text'])
        self.screen.blit(rules_title, (rules_box.x + 15, rules_box.y + 15))

        rules = [
            "• Higher atomic number wins",
            "• Winner takes both cards",
            "• First to collect all cards wins!",
            "• Ties create a 'War' bonus pile"
        ]

        for i, rule in enumerate(rules):
            rule_surf = self.font_small.render(rule, True, COLORS['text'])
            self.screen.blit(rule_surf, (rules_box.x + 15, rules_box.y + 60 + i * 30))

        # Draw buttons
        if not self.game_over:
            if self.state == GameState.READY or self.state == GameState.RESULT:
                self.battle_button.draw(self.screen, self.font_medium)
            self.new_game_button.draw(self.screen, self.font_medium)

        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(COLORS['background'])
            self.screen.blit(overlay, (0, 0))

            result_text = self.message
            result_color = COLORS['success'] if self.winner == 'player' else COLORS['danger']
            result_surf = self.font_large.render(result_text, True, result_color)
            result_rect = result_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(result_surf, result_rect)

            # Final scores
            score_text = f"Final: You {len(self.player_deck)} - AI {len(self.ai_deck)}"
            score_surf = self.font_medium.render(score_text, True, COLORS['text'])
            score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(score_surf, score_rect)

            self.play_again_button.draw(self.screen, self.font_medium)

        # Credit
        credit_text = "Based on Chemistry Card Game | Design by N.Siwatkittisuk"
        credit_surf = self.font_small.render(credit_text, True, COLORS['text'])
        credit_rect = credit_surf.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 10))
        self.screen.blit(credit_surf, credit_rect)

        pygame.display.flip()

    async def run(self):
        """Main game loop"""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            running = self.handle_events()
            self.update(dt)
            self.draw()

            # Yield to browser
            await asyncio.sleep(0)

        pygame.quit()


async def main():
    """Entry point"""
    game = ChemistryWarGame()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
