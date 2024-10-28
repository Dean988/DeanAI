import discord
from discord.ui import View, Button
import chess
import chess.engine

class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.start_square = None
        self.move_history = []

    def describe_move(self, move):
        piece_moved = self.board.piece_at(move.from_square)
        piece_type = piece_moved.symbol().upper() if piece_moved else ""
        from_square = chess.square_name(move.from_square)
        to_square = chess.square_name(move.to_square)
        captured_piece = self.board.piece_at(move.to_square)

        if captured_piece:
            return f"{piece_type} in {from_square} cattura {captured_piece.symbol().upper()} in {to_square}"
        else:
            return f"{piece_type} si muove da {from_square} a {to_square}"

    def make_move(self, start_square, end_square):
        move = f"{start_square}{end_square}"
        print(f"Tentativo di eseguire la mossa: {move}")

        try:
            chess_move = chess.Move.from_uci(move)
            if chess_move in self.board.legal_moves:
                move_description = self.describe_move(chess_move)
                self.move_history.append(f"Giocatore: {move_description}")
                self.board.push(chess_move)
                return True, self.get_board_text()
            else:
                return False, "Mossa non valida."
        except ValueError:
            return False, "Formato mossa non valido."

    def ai_move(self):
        with chess.engine.SimpleEngine.popen_uci(r".\stockfish\stockfish-windows-x86-64-sse41-popcnt.exe") as engine:
            result = engine.play(self.board, chess.engine.Limit(time=0.1))
            move_description = self.describe_move(result.move)
            self.move_history.append(f"AI: {move_description}")
            self.board.push(result.move)
            return self.get_board_text()

    def suggest_best_moves(self):
        with chess.engine.SimpleEngine.popen_uci(r".\stockfish\stockfish-windows-x86-64-sse41-popcnt.exe") as engine:
            analysis = engine.analyse(self.board, chess.engine.Limit(time=0.1))
            best_moves = analysis['pv'][:2]  # Prendi le prime due mosse migliori
            move_suggestions = [self.board.san(move) for move in best_moves]
            return move_suggestions

    def get_move_history(self):
        return "\n".join(self.move_history)

    def get_board_text(self):
        board_str = "   a b c d e f g h\n"
        board_str += "  ----------------\n"
        for rank in range(7, -1, -1):
            line = f"{rank + 1} |"
            for file in range(8):
                square = chess.square(file, rank)
                piece = self.board.piece_at(square)
                if self.start_square and chess.square_name(square) == self.start_square:
                    line += "🔴 "
                elif piece:
                    line += piece.symbol() + " "
                else:
                    line += ". "
            board_str += line + f"| {rank + 1}\n"
        board_str += "  ----------------\n"
        board_str += "   a b c d e f g h\n"
        return f"```\n{board_str}\n```"

class ColumnSelectionView(View):
    def __init__(self, game, select_end_square=False):
        super().__init__()
        self.game = game
        self.select_end_square = select_end_square
        for col in 'abcdefgh':
            button = ColumnButton(col, self.select_end_square)
            self.add_item(button)
        suggest_button = SuggestionButton(self.game)
        self.add_item(suggest_button)

class RowSelectionView(View):
    def __init__(self, game, column, select_end_square=False):
        super().__init__()
        self.game = game
        self.column = column
        self.select_end_square = select_end_square
        for row in '12345678':
            button = RowButton(row, column, select_end_square)
            self.add_item(button)

class ColumnButton(Button):
    def __init__(self, label, select_end_square):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.select_end_square = select_end_square

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        view = RowSelectionView(self.view.game, column=self.label, select_end_square=self.select_end_square)
        await interaction.followup.send("Seleziona la **riga**:", view=view, ephemeral=True)

class RowButton(Button):
    def __init__(self, row, column, select_end_square):
        super().__init__(label=row, style=discord.ButtonStyle.primary)
        self.column = column
        self.select_end_square = select_end_square

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        square = f"{self.column}{self.label}"

        if not self.select_end_square:
            self.view.game.start_square = square
            view = ColumnSelectionView(self.view.game, select_end_square=True)
            await interaction.followup.send("Seleziona la **colonna di arrivo**:", view=view, ephemeral=True)
        else:
            start_square = self.view.game.start_square
            end_square = square
            success, result = self.view.game.make_move(start_square, end_square)
            if success:
                self.view.game.start_square = None
                await interaction.channel.send(f"**Mossa effettuata!**\n{result}")

                ai_board_text = self.view.game.ai_move()
                await interaction.channel.send(f"**Mossa dell'IA effettuata!**\n{ai_board_text}")

                await interaction.channel.send(f"**Cronologia delle mosse:**\n{self.view.game.get_move_history()}")

                new_view = ColumnSelectionView(self.view.game, select_end_square=False)
                await interaction.followup.send("Seleziona la **colonna di partenza** della tua prossima mossa (da 'a' a 'h'):", view=new_view, ephemeral=True)
            else:
                await interaction.followup.send(
                    f"Errore: {result}. Riprova selezionando nuovamente la colonna di partenza.",
                    view=ColumnSelectionView(self.view.game, select_end_square=False),
                    ephemeral=True)

class SuggestionButton(Button):
    def __init__(self, game):
        super().__init__(label="Suggerimento", style=discord.ButtonStyle.secondary)
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        suggestions = self.game.suggest_best_moves()
        if suggestions:
            await interaction.followup.send(f"Le due mosse migliori sono: {suggestions[0]} e {suggestions[1]}", ephemeral=True)
        else:
            await interaction.followup.send("Non è possibile suggerire mosse in questo momento.", ephemeral=True)

# Funzione per avviare una nuova partita
async def start_chess_game(message):
    game = ChessGame()
    view = ColumnSelectionView(game)
    await message.channel.send("Seleziona la **colonna di partenza** della tua mossa (da 'a' a 'h'):", view=view)
    await message.channel.send(f"**Stato iniziale della scacchiera:**\n{game.get_board_text()}")




















