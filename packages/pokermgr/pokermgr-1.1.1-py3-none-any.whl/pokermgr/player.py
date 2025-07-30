"""Player module for poker game.

This module defines the core player-related classes for a poker game, including:
- PlayerStatus: Enum for different player states
- ActionType: Enum for different types of player actions
- Action: Class representing a player's action
- Player: Base player class with bankroll management
- TablePlayer: Extended player class for table gameplay
"""
from itertools import combinations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TypeVar
from cardspy.card import cards_mask, extract_cards
from pokermgr.hand import Hand
from pokermgr.hole_cards import HoleCards
from pokermgr.funcs import get_hand_type_weight

# Type variable for generic return type in class methods
T = TypeVar('T', bound='Player')


class PlayerStatus(Enum):
    """Enum representing the possible statuses of a poker player.

    Attributes:
        INGAME: Player is actively playing the current hand
        SITOUT: Player is sitting out the current hand
        FOLDED: Player has folded their hand
        ALLIN: Player is all-in and cannot make further bets
    """
    INGAME = 0x1
    SITOUT = 0x2
    FOLDED = 0x4
    ALLIN = 0x8


class ActionType(Enum):
    """Enum representing the types of actions a player can take.

    Attributes:
        FOLD: Player folds their hand
        CHECK: Player checks (passes action to next player)
        CALL: Player matches the current bet
        RAISE: Player increases the current bet
        ALL_IN: Player bets all their remaining chips
    """
    FOLD = 0x1
    CHECK = 0x2
    CALL = 0x4
    RAISE = 0x8
    ALL_IN = 0x10


@dataclass
class Action:
    """Represents a player's action in a poker game.

    Attributes:
        type: The type of action (fold, check, call, raise, all-in)
        amount: The amount associated with the action (for call/raise/all-in)
    """

    type: ActionType
    amount: float = field(default=0.0)

    def __str__(self) -> str:
        if self.type == ActionType.FOLD:
            return "folds"
        if self.type == ActionType.CHECK:
            return "checks"
        if self.type == ActionType.CALL:
            return f"calls {self.amount}"
        if self.type == ActionType.RAISE:
            return f"raises to {self.amount}"
        if self.type == ActionType.ALL_IN:
            return f"goes all-in with {self.amount}"
        return ""


@dataclass
class Player:
    """Base class representing a poker player.

    Attributes:
        code: Unique identifier for the player
        bank_roll: Current amount of money the player has (default: 3000)
    """
    code: str
    bank_roll: float = field(default=3000.0)

    def add_balance(self, amount: float) -> None:
        """Add funds to the player's bank roll.

        Args:
            amount: The amount to add to the bank roll
    
        Note:
            No validation is performed on the amount. It can be negative.
        """
        self.bank_roll += amount

    def remove_balance(self, amount: float) -> None:
        """Remove funds from the player's bank roll.

        Args:
            amount: The amount to remove from the bank roll

        Note:
            No validation is performed on the amount. It can be negative.
        """
        self.bank_roll -= amount

    def __str__(self) -> str:
        """Return the player's code as string representation.

        Returns:
            str: The player's unique code
        """
        return self.code

    def __repr__(self) -> str:
        """Return the player's code as the official string representation.

        Returns:
            str: The player's unique code
        """
        return self.code

    def __eq__(self, other: object) -> bool:
        """Compare two Player instances for equality.

        Args:
            other: The object to compare with

        Returns:
            bool: True if other is a Player with the same code, False otherwise
        """
        if not isinstance(other, Player):
            return False
        return self.code == other.code


@dataclass
class TablePlayer(Player):
    """Extended Player class for table gameplay with hand and betting management.

    Attributes:
        status: Current status of the player in the game
        hole_cards: Bitmask representing the player's hole cards
        best_hand: The best possible hand the player can make with their hole cards and community cards
        equity: The player's current equity in the hand (0.0 to 1.0)
        current_bet: The amount the player has bet in the current betting round
        stack: The player's current chip stack
        last_action: The player's last action in the current hand
    """
    status: PlayerStatus = field(default=PlayerStatus.INGAME, init=False)
    hole_cards: HoleCards = field(init=False, default=HoleCards(0))
    best_hand: Hand = field(init=False)
    equity: float = field(init=False, default=0.0)
    current_bet: float = field(init=False, default=0.0)
    stack: float = field(init=False, default=150.0)  # Default starting stack
    last_action: Optional[Action] = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Initialize TablePlayer instance with default values."""
        self.status = PlayerStatus.INGAME
        self.best_hand = Hand(self.hole_cards.key)
        self.equity = 0.0
        self.current_bet = 0.0
        self.stack = 150.0
        self.last_action = None

    def set_hole_cards(self, cards: int) -> None:
        """Set the player's hole cards and update the best hand.
        
        This method creates a new HoleCards instance with the given card mask
        and updates the player's best hand to use these new hole cards.
        
        Args:
            cards: Integer bitmask representing the hole cards
            
        Example:
            >>> from cardspy.deck import cards_to_mask
            >>> player = TablePlayer("p1")
            >>> player.set_hole_cards(cards_to_mask(['As', 'Ks']))
            >>> print(player.hole_cards.ranges)
            ['AKs']
        """
        self.hole_cards = HoleCards(cards)
        self.best_hand = Hand(cards)  # Update best hand with new hole cards

    def add_stack(self, amount: float) -> None:
        """Add chips to the player's stack from their bank roll.

        This method transfers the specified amount from the player's bank roll
        to their current stack. The amount must be non-negative and cannot exceed
        the player's available bank roll.

        Args:
            amount: The number of chips to add to the stack (must be >= 0)

        Raises:
            ValueError: If amount is negative or exceeds bank roll
            
        Example:
            >>> player = TablePlayer("p1")
            >>> player.bank_roll = 1000.0
            >>> player.stack = 100.0
            >>> player.add_stack(200.0)
            >>> player.stack
            300.0
            >>> player.bank_roll
            800.0
        """
        if amount < 0:
            raise ValueError("Cannot add negative amount to stack")
        if self.bank_roll < amount:
            raise ValueError("Not enough bank roll")
        self.stack += amount
        self.bank_roll -= amount

    def remove_stack(self, amount: float) -> None:
        """Remove chips from the player's stack and return to bank roll.

        This method transfers the specified amount from the player's current stack
        back to their bank roll. The amount must be non-negative and cannot exceed
        the player's current stack.

        Args:
            amount: The number of chips to remove from the stack (must be >= 0)

        Raises:
            ValueError: If amount is negative or exceeds current stack
            
        Example:
            >>> player = TablePlayer("p1")
            >>> player.stack = 500.0
            >>> player.bank_roll = 1000.0
            >>> player.remove_stack(200.0)
            >>> player.stack
            300.0
            >>> player.bank_roll
            1200.0
        """
        if amount < 0:
            raise ValueError("Cannot remove negative amount from stack")
        if self.stack < amount:
            raise ValueError("Not enough stack")
        self.stack -= amount
        self.bank_roll += amount

    def fold(self) -> Action:
        """Execute a fold action.

        Returns:
            Action: The fold action that was taken

        Note:
            Sets the player's status to FOLDED and records the action
        """
        self.status = PlayerStatus.FOLDED
        self.last_action = Action(ActionType.FOLD)
        return self.last_action

    def check(self) -> Action:
        """Execute a check action.

        Returns:
            Action: The check action that was taken

        Note:
            Records the check action. Does not change the player's status.
        """
        self.last_action = Action(ActionType.CHECK)
        return self.last_action

    def set_best_hand(self, board_cards_key: int) -> None:

        """
        Calculates and sets the player's best possible 5-card poker hand using their hole cards and community cards.

        This method examines all valid 5-card combinations formed by the player's hole cards and the provided board cards. 
        For a standard Texas Hold'em scenario (exactly two hole cards), it combines those two cards with every possible three-card selection from the board. 
        For games like Omaha where the player has four hole cards, it evaluates every two-card combination from the hole cards combined with every three-card combination from the board.

        The hand ranking is determined by the `get_hand_type_weight` function, which returns a weight used to compare hands. 
        After evaluating all combinations, `self.best_hand` is updated to the highest-ranking hand found.

        Args:
            board_cards_key (int): A bitmask integer representing the community (board) cards.

        Returns:
            None: Updates the `self.best_hand` attribute with an instance of `Hand` representing the best hand.

        Examples:
            # Assume `player` is an instance of TablePlayer and has already been dealt hole cards.
            # For Texas Hold'em (2 hole cards):
            player.set_hole_cards(cards_mask([AH, KH]))  # Ace of hearts, King of hearts
            board_key = cards_mask([QH, JH, TH, 2C, 5D])  # Board: Q♥, J♥, T♥, 2♣, 5♦
            player.set_best_hand(board_key)
            # Now player.best_hand represents the royal flush (A♥, K♥, Q♥, J♥, T♥).

            # For Omaha (4 hole cards):
            player.set_hole_cards(cards_mask([AS, KS, QS, JS]))
            board_key = cards_mask([TS, 9S, 2D, 3C, 4H])
            player.set_best_hand(board_key)
            # Now player.best_hand represents the straight flush (9♠, 10♠, J♠, Q♠, K♠).

            # Accessing the best hand weight:
            best_weight = player.best_hand.weight

        """

        board_cards = extract_cards(board_cards_key)
        best_hand = Hand(0)
        hole_cards_count = self.hole_cards.key.bit_count()
        if hole_cards_count == 2:
            all_cards_key = self.hole_cards.key | board_cards_key
            all_cards = extract_cards(all_cards_key)
            for comb in combinations(all_cards, 5):
                comb_key = cards_mask(comb)
                weight, type_key, type_name = get_hand_type_weight(comb_key)
                if weight > best_hand.weight:
                    best_hand = Hand(comb_key)
                    best_hand.weight = weight
                    best_hand.type_key = type_key
                    best_hand.type_name = type_name
        elif hole_cards_count >= 4:
            hole_cards = extract_cards(self.hole_cards.key)
            board_cards = extract_cards(board_cards_key)
            for comb_hole_cards in combinations(hole_cards, 2):
                for comb_board_cards in combinations(board_cards, 3):
                    comb_key = cards_mask(comb_hole_cards + comb_board_cards)
                    weight, type_key, type_name = get_hand_type_weight(comb_key)
                    if weight > best_hand.weight:
                        best_hand = Hand(comb_key)
                        best_hand.weight = weight
                        best_hand.type_key = type_key
                        best_hand.type_name = type_name
        self.best_hand = best_hand

    # def call(self, current_bet: float) -> Action:
    #     """Player calls the current bet"""
    #     call_amount = min(current_bet - self.current_bet, self.stack)
    #     self.stack -= call_amount
    #     self.current_bet += call_amount

    #     if self.stack <= 0:
    #         self.status = PlayerStatus.ALLIN
    #         action = Action(ActionType.ALL_IN, self.current_bet)
    #     else:
    #         action = Action(ActionType.CALL, call_amount)

    #     self.last_action = action
    #     return action

    # def raise_bet(self, current_bet: float, min_raise: float) -> Action:
    #     """Player raises the bet"""
    #     if self.stack <= (current_bet - self.current_bet):
    #         return self.call(current_bet)

    #     # Calculate raise amount based on player style and randomness
    #     base_raise = max(min_raise, current_bet * 1.5)
    #     if self.style == PlayerStyle.TIGHT:
    #         # Tighter players tend to make smaller raises
    #         raise_amount = min(base_raise * random.uniform(1.0, 1.5), self.stack)
    #     elif self.style == PlayerStyle.BALANCED:
    #         # Balanced players make moderate raises
    #         raise_amount = min(base_raise * random.uniform(1.5, 2.0), self.stack)
    #     else:  # AGGRESSIVE or OVERAGGRESSIVE
    #         # Aggressive players make bigger raises
    #         multiplier = 2.0 if self.style == PlayerStyle.AGGRESSIVE else 2.5
    #         raise_amount = min(base_raise * random.uniform(2.0, multiplier), self.stack)

    #     # Round to nearest 0.5 for cleaner betting
    #     raise_amount = round(raise_amount * 2) / 2
    #     total_bet = self.current_bet + raise_amount

    #     if total_bet >= self.stack:
    #         return self.go_all_in()

    #     self.stack -= raise_amount
    #     self.current_bet = total_bet
    #     self.last_action = Action(ActionType.RAISE, total_bet)
    #     return self.last_action

    # def go_all_in(self) -> Action:
    #     """Player goes all-in"""
    #     total_bet = self.current_bet + self.stack
    #     self.current_bet = total_bet
    #     self.stack = 0
    #     self.status = PlayerStatus.ALLIN
    #     self.last_action = Action(ActionType.ALL_IN, total_bet)
    #     return self.last_action

    def __str__(self) -> str:
        """Return a string representation of the player."""
        return self.code

    def __repr__(self) -> str:
        """Return a string representation of the player."""
        return self.code

    def __eq__(self, other: object) -> bool:
        """Return True if the players are equal."""
        if not isinstance(other, Player):
            return False
        return self.code == other.code
