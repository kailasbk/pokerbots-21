from nodes import Node
from player import Player
from tree import create_game_tree, branches_from_dealer
from cards import *

class Game:
    """
    Facilitates a game of poker
    """
    def __init__(self, tree: Node):
        names = ['SB', 'BB']
        cards = draw_random_cards(all_cards_excluding(), 9)
        hands = [cards[0:2], cards[2:4]]
        self.players = [Player(names[i], tree, hands[i]) for i in range(2)]
        self.shared_cards = cards[4:9]
        self.round = 1
        self.history = ['R1']
        self.last_turn = self.players[1]

    def is_finished(self) -> bool:
        assert self.players[0].at_terminal() == self.players[1].at_terminal()
        return self.players[0].at_terminal()

    def move_up(self):
        for player in self.players:
            player.move_up()
        
        self.history.pop()

    def move_down(self, branch):
        for player in self.players:
            player.move_down(branch)
        
        self.history.append(branch)
        if ',' in branch:
            self.round += 1

    def get_players(self) -> list:
        return self.players

    def get_history(self) -> list:
        return self.history

    def cards_on_table(self, round) -> list:
        if round == 1:
            return []
        elif round == 2:
            return self.shared_cards[0:3]
        elif round == 3:
            return self.shared_cards[0:4]
        else:
            return self.shared_cards[0:5]

    def take_turn(self):
        branch = ''
        for player in self.players:
            if player.is_owner():
                self.last_turn = player
                branch = player.choose_branch()
                #print(str(player) + ' chooses ' + branch)
                break

        if branch != '':
            self.move_down(branch)

        else:
            self.history.append('D')
            for player in self.players:
                mc = monte_carlo_prob(player.get_hand(), self.cards_on_table(self.round))
                for range in branches_from_dealer:
                    if mc <= float(range):
                        player.move_down(range)
                        break

    def play(self) -> str:
        while not self.is_finished():
            self.take_turn()
        
        total = 2
        raise_amount = 0

        if len(self.history) == 3:
            return 'SB -3'
        else:
            for event in self.history:
                if 'RR' in event:
                    total += 2 * raise_amount
                    raise_amount = int(event[2:])
                elif 'R' in event:
                    raise_amount = int(event[1:])
                elif 'C' in event:
                    total += 2 * raise_amount
                    raise_amount = 0

            if 'F' in self.history[-1]:
                return f'{self.last_turn} -{total}'
            else:
                sb_cards = self.players[0].get_hand() + self.shared_cards
                bb_cards = self.players[1].get_hand() + self.shared_cards
                sb = eval7.evaluate([eval7.Card(card) for card in sb_cards])
                bb = eval7.evaluate([eval7.Card(card) for card in bb_cards])
                if sb > bb:
                    return f'SB {total}'
                elif sb < bb:
                    return f'BB {total}'
                else:
                    return 'SP 0'