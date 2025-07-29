"""
This module provides the Pot class which represents a poker pot.

A Pot tracks the amount of chips in play during a poker hand, the players
eligible to win the pot, and the eventual winners of the pot.
"""
from dataclasses import dataclass, field
from typing import List, Dict
from pokermgr.player import TablePlayer


@dataclass
class Pot:
    """
    A class representing a poker pot in a poker game.

    The Pot class tracks the chips in play, the players who have contributed to the pot,
    and the eventual winners per board. For multi-board games, the pot is typically
    split equally between boards (e.g., $500 pot = $250 per board).

    Attributes:
        key: A unique identifier for the pot.
        stack: The total amount of chips in the pot.
        players: List of players who have contributed to this pot and are eligible to win it.
        board_count: Number of boards this pot will be split across (default 1).
        winners_by_board: Dict mapping board_id to list of winners for that board.

    Note:
        The `winners_by_board` dict is initialized as an empty dict in `__post_init__`
        since we can't use a mutable default argument in the field definition.
    """
    key: int
    stack: float
    players: List[TablePlayer]
    board_count: int = 1
    winners_by_board: Dict[int, List[TablePlayer]] = field(init=False)

    def __post_init__(self) -> None:
        """
        Initialize the winners_by_board dict after the dataclass is instantiated.

        This is necessary because we can't use a mutable default argument
        in the field definition.
        """
        self.winners_by_board = {}

    def get_board_share(self) -> float:
        """Get the amount each board is worth (total pot divided by board count)."""
        return self.stack / self.board_count

    def set_board_winners(self, board_id: int, winners: List[TablePlayer]) -> None:
        """Set the winners for a specific board."""
        if board_id < 1 or board_id > self.board_count:
            raise ValueError(f"Board ID {board_id} out of range (1-{self.board_count})")
        self.winners_by_board[board_id] = winners

    def get_board_winners(self, board_id: int) -> List[TablePlayer]:
        """Get the winners for a specific board."""
        return self.winners_by_board.get(board_id, [])

    def get_player_winnings(self, player: TablePlayer) -> float:
        """Calculate total winnings for a player across all boards."""
        total_winnings = 0.0
        board_share = self.get_board_share()
        
        for board_id in range(1, self.board_count + 1):
            board_winners = self.get_board_winners(board_id)
            if player in board_winners and board_winners:
                # Split the board's share among its winners
                total_winnings += board_share / len(board_winners)
        
        return total_winnings

    def add_board(self) -> None:
        """
        Add an additional board to the game.
        
        This method increases the board count by 1, which automatically
        redistributes the pot value across more boards when get_board_share() is called.
        
        Raises:
            RuntimeError: If any boards already have winners assigned.
        """
        if self.winners_by_board:
            raise RuntimeError("Cannot add boards after winners have been assigned")
        self.board_count += 1

    def remove_board(self) -> None:
        """
        Remove a board from the game.
        
        This method decreases the board count by 1, but only if no winners
        have been assigned and the board count is greater than 1.
        
        Raises:
            RuntimeError: If any boards already have winners assigned.
            ValueError: If trying to reduce board count below 1.
        """
        if self.winners_by_board:
            raise RuntimeError("Cannot remove boards after winners have been assigned")
        if self.board_count <= 1:
            raise ValueError("Cannot reduce board count below 1")
        self.board_count -= 1

    def set_board_count(self, new_count: int) -> None:
        """
        Set the board count to a specific value.
        
        Args:
            new_count: The new number of boards (must be >= 1)
            
        Raises:
            RuntimeError: If any boards already have winners assigned.
            ValueError: If new_count is less than 1.
        """
        if new_count < 1:
            raise ValueError("Board count must be at least 1")
        if self.winners_by_board:
            raise RuntimeError("Cannot change board count after winners have been assigned")
        self.board_count = new_count

    def is_fully_resolved(self) -> bool:
        """Check if all boards have winners assigned."""
        return len(self.winners_by_board) == self.board_count

    def is_multi_board(self) -> bool:
        """Check if this is a multi-board pot."""
        return self.board_count > 1

    @property
    def all_winners(self) -> List[TablePlayer]:
        """Get all unique winners across all boards."""
        all_winners = set()
        for winners in self.winners_by_board.values():
            all_winners.update(winners)
        return list(all_winners)

    def __repr__(self) -> str:
        """Custom representation showing pot details."""
        if self.board_count > 1:
            return (f"Pot(key={self.key}, stack=${self.stack}, "
                   f"boards={self.board_count}, share=${self.get_board_share():.2f})")
        else:
            return f"Pot(key={self.key}, stack=${self.stack})"
