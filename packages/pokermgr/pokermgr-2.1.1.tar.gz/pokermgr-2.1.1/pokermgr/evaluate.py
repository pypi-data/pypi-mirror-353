"""Poker Hand Evaluation Module

This module provides functionality to evaluate poker hands and determine the winner(s)
among multiple players. It handles the core logic for comparing hand strengths
based on standard poker hand rankings.

Functions:
    get_winners: Determines the winning player(s) based on their best 5-card hand
                evaluated against the community cards.
"""
from itertools import combinations
from typing import List, Tuple
from cardspy.card import extract_cards, cards_mask
from pokermgr.player import TablePlayer
from pokermgr.funcs import get_hand_type_weight


def get_winners(board_cards_key: int, players: List[TablePlayer]) -> List[TablePlayer]:
    """Determine the winning player(s) based on their best 5-card hand.

    This function evaluates each player's best possible 5-card hand using their
    hole cards and the community cards. It then compares all players' hands to
    determine the winner(s) based on standard poker hand rankings.

    Args:
        board_cards: Bitmask integer representing the community cards on the board
        players: List of TablePlayer objects to evaluate

    Returns:
        List[TablePlayer]: List of winning players (may contain multiple players in case of a tie)

    Example:
        >>> from pokermgr.player import TablePlayer
        >>> from pokermgr.funcs import cards_to_mask
        >>>
        >>> # Setup players and board
        >>> player1 = TablePlayer(1, "Alice")
        >>> player2 = TablePlayer(2, "Bob")
        >>> player1.set_hole_cards(cards_to_mask(["Ah", "Kh"]))
        >>> player2.set_hole_cards(cards_to_mask(["Ad", "Kd"]))
        >>> board = cards_to_mask(["Qh", "Jh", "Th", "9h", "8h"])  # Royal flush board
        >>>
        >>> # Determine winner(s)
        >>> winners = get_winners(board, [player1, player2])
        >>> [winner.name for winner in winners]
        ['Alice']  # Alice wins with royal flush
    """
    if board_cards_key == 0:
        return []
    player_weights = []

    # Calculate best weight for each player
    for player in players:
        best_weight = _get_player_best_weight(player, board_cards_key)
        player_weights.append((player, best_weight))

    # Find winners based on best weights
    return _determine_winners_from_weights(player_weights)


def _get_player_best_weight(player: TablePlayer, board_cards_key: int) -> int:
    """Calculate the best possible hand weight for a player."""
    player_cards_count = player.hole_cards.key.bit_count()

    if player_cards_count == 2:
        return _get_holdem_best_weight(player, board_cards_key)
    elif player_cards_count >= 4:
        return _get_omaha_best_weight(player, board_cards_key)

    return 0


def _get_holdem_best_weight(player: TablePlayer, board_cards_key: int) -> int:
    """Calculate best weight for Hold'em game (2 hole cards)."""
    all_cards_key = player.hole_cards.key | board_cards_key
    all_cards = extract_cards(all_cards_key)

    best_weight = 0
    for combo in combinations(all_cards, 5):
        combo_key = cards_mask(list(combo))
        weight, _, _ = get_hand_type_weight(combo_key)
        best_weight = max(best_weight, weight)

    return best_weight


def _get_omaha_best_weight(player: TablePlayer, board_cards_key: int) -> int:
    """Calculate best weight for Omaha game (4+ hole cards)."""
    player_cards = extract_cards(player.hole_cards.key)
    board_cards = extract_cards(board_cards_key)

    best_weight = 0
    for player_cards_combo in combinations(player_cards, 2):
        for board_cards_combo in combinations(board_cards, 3):
            combo = player_cards_combo + board_cards_combo
            combo_key = cards_mask(list(combo))
            weight, _, _ = get_hand_type_weight(combo_key)
            best_weight = max(best_weight, weight)

    return best_weight


def _determine_winners_from_weights(
    player_weights: List[Tuple[TablePlayer, int]]
) -> List[TablePlayer]:
    """Determine winners from list of (player, weight) tuples."""
    if not player_weights:
        return []

    # Find the maximum weight
    max_weight = max(weight for _, weight in player_weights)

    # Return all players with the maximum weight
    return [player for player, weight in player_weights if weight == max_weight]
