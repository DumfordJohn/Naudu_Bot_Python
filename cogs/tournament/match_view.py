import discord
from discord.ui import View, Button

class MatchView(View):
    def __init__(self, tournament_name, match_index, player1, player2):
        super().__init__(timeout=None)
        self.tournament_name = tournament_name
        self.match_index = match_index
        self.player1 = player1
        self.player2 = player2

        self.add_item(Button(label=f"{player1} Wins", style=discord.ButtonStyle.success,custom_id=f"{tournament_name}|{match_index}|1"))
        self.add_item(Button(lable=f"{player2} Wins", style=discord.ButtonStyle.success,custom_id=f"{tournament_name}|{match_index}|2"))
