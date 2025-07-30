"""Poker Hand Evaluation Module

This module provides functionality to evaluate poker hands and determine the winner(s)
among multiple players. It handles the core logic for comparing hand strengths
based on standard poker hand rankings.

Functions:
    get_winners: Determines the winning player(s) based on their best 5-card hand
                evaluated against the community cards.
"""
from typing import List
from pokermgr.player import TablePlayer


def get_winners(board_cards: int, players: List[TablePlayer]) -> List[TablePlayer]:
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
    winners: List[TablePlayer] = []
    best_weight = 0
    
    # Evaluate each player's best hand
    for player in players:
        # Calculate the best possible hand for the player using their hole cards and the board
        player.set_best_hand(board_cards)
        
        # Compare with current best hand
        if player.best_hand.weight > best_weight:
            # New best hand found, update winners list
            best_weight = player.best_hand.weight
            winners = [player]
        elif player.best_hand.weight == best_weight:
            # Tie with current best hand, add to winners
            winners.append(player)
    
    return winners
