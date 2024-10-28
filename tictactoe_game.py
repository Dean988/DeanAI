import discord
from discord.ui import View, Button
import random

class TicTacToeGame:
    def __init__(self):
        self.board = [" " for _ in range(9)]
        self.current_player = "X"
        self.game_over = False

    def make_move(self, index, player):
        if self.board[index] == " ":
            self.board[index] = player
            if self.check_winner(player):
                self.game_over = True
                return f"{player} ha vinto!"
            elif " " not in self.board:
                self.game_over = True
                return "Pareggio!"
            return None
        else:
            return "Mossa non valida, riprova!"

    def ai_move(self):
        available_moves = [i for i in range(9) if self.board[i] == " "]
        if available_moves:
            ai_move = random.choice(available_moves)
            return self.make_move(ai_move, "O")

    def check_winner(self, player):
        winning_positions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # righe
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # colonne
            [0, 4, 8], [2, 4, 6]              # diagonali
        ]
        for pos in winning_positions:
            if all(self.board[i] == player for i in pos):
                return True
        return False

    def get_board_text(self):
        board_text = ""
        for i in range(9):
            board_text += self.board[i] if self.board[i] != " " else str(i + 1)
            if (i + 1) % 3 == 0:
                board_text += "\n"
            else:
                board_text += " | "
        return f"```\n{board_text}\n```"


class TicTacToeView(View):
    def __init__(self, game):
        super().__init__(timeout=None)
        self.game = game
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        for i in range(9):
            button = TicTacToeButton(i, self.game)
            self.add_item(button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.game.game_over:
            await interaction.response.send_message("La partita è terminata! Avvia una nuova partita per giocare di nuovo.", ephemeral=True)
            return False
        return True


class TicTacToeButton(Button):
    def __init__(self, index, game):
        super().__init__(label=str(index + 1), style=discord.ButtonStyle.primary)
        self.index = index
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        # Mossa del giocatore
        result = self.game.make_move(self.index, "X")
        self.view.update_buttons()  # Aggiorna i bottoni per mostrare la mossa
        board_text = self.game.get_board_text()

        if result:
            await interaction.response.edit_message(content=f"{board_text}\n{result}", view=None)
            return

        # Mossa dell'IA
        ai_result = self.game.ai_move()
        self.view.update_buttons()  # Aggiorna i bottoni per la mossa dell'IA
        board_text = self.game.get_board_text()

        if ai_result:
            await interaction.response.edit_message(content=f"{board_text}\n{ai_result}", view=None)
        else:
            await interaction.response.edit_message(content=f"{board_text}", view=self.view)


# Funzione per avviare una nuova partita a Tris
async def start_tictactoe_game(message):
    game = TicTacToeGame()
    view = TicTacToeView(game)
    await message.channel.send(
        "Inizia la partita a Tris! Sei 'X' e l'IA è 'O'. Scegli una cella per fare la tua mossa:",
        view=view
    )
    await message.channel.send(f"Stato iniziale del tabellone:\n{game.get_board_text()}")
