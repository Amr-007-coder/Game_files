import webbrowser
from game_scripts.nll.scripts.Game import Game

def main():
    game = Game()

    while not game.button_actions["Quit"]:
        game.run()
        
    game.menu.save_settings()

    webbrowser.open("https://sites.google.com/view/nll-forum/home")