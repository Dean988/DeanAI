import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import time
import json
import os

class CoinFlipGame:
    def __init__(self):
        self.leaderboard = self.load_leaderboard()
        self.last_played = {}

    def load_leaderboard(self):
        if os.path.exists("leaderboard.json"):
            with open("leaderboard.json", "r") as f:
                return json.load(f)
        return {}

    def save_leaderboard(self):
        with open("leaderboard.json", "w") as f:
            json.dump(self.leaderboard, f)

    def flip_coin(self, choice, user_id, server_id):
        # Creiamo una chiave unica per ogni utente su ogni server
        unique_key = f"{server_id}:{user_id}"

        # Controlla il cooldown di 10 minuti
        if user_id in self.last_played:
            time_since_last_play = time.time() - self.last_played[user_id]
            remaining_time = 600 - int(time_since_last_play)
            if time_since_last_play < 600:
                return False, f"Riprova tra {remaining_time // 60} minuti e {remaining_time % 60} secondi."

        self.last_played[user_id] = time.time()
        result = random.choice(["Testa", "Croce"])
        won = choice == result

        # Aggiorna la classifica
        if unique_key in self.leaderboard:
            self.leaderboard[unique_key]["games"] += 1
            if won:
                self.leaderboard[unique_key]["wins"] += 1
        else:
            self.leaderboard[unique_key] = {"games": 1, "wins": 1 if won else 0}

        # Salva la classifica aggiornata
        self.save_leaderboard()

        # Crea il messaggio di risultato
        if won:
            message = f"Hai vinto! La moneta ha mostrato **{result}**."
        else:
            message = f"Hai perso. La moneta ha mostrato **{result}**."

        # Ordina la classifica per il server corrente
        sorted_leaderboard = sorted(
            [
                (key, data) for key, data in self.leaderboard.items()
                if key.startswith(f"{server_id}:")
            ],
            key=lambda x: x[1]["wins"],
            reverse=True
        )[:4]
        leaderboard_message = "\n".join(
            [
                f"{idx + 1}. <@{key.split(':')[1]}> - Vittorie: {data['wins']}, Partite giocate: {data['games']}"
                for idx, (key, data) in enumerate(sorted_leaderboard)
            ]
        )

        message += f"\n\n**Classifica:**\n{leaderboard_message}"
        return True, message


class CoinFlipButton(Button):
    def __init__(self, label, choice, game):
        super().__init__(label=label, style=discord.ButtonStyle.primary if choice == "Testa" else discord.ButtonStyle.secondary)
        self.choice = choice
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        result, message = self.game.flip_coin(self.choice, interaction.user.id, interaction.guild.id)
        await interaction.followup.send(content=message)


class CoinFlipView(View):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.add_item(CoinFlipButton("Testa", "Testa", game))
        self.add_item(CoinFlipButton("Croce", "Croce", game))


async def start_coin_flip_game(message):
    game = CoinFlipGame()
    view = CoinFlipView(game)
    await message.channel.send(
        "Inizia la partita a Testa o Croce! Scegli Testa o Croce premendo il pulsante qui sotto:",
        view=view
    )
