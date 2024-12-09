import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

from models.base import Error


class Suit(Enum):
    '''撲克牌花色'''
    CLUB = {'symbol': '♣', 'value': 0}
    DIAMOND = {'symbol': '♦', 'value': 1}
    HEART = {'symbol': '♥', 'value': 2}
    SPADE = {'symbol': '♠', 'value': 3}


class Rank(Enum):
    '''撲克牌點數'''
    TWO = {'symbol': '2', 'value': 0}
    THREE = {'symbol': '3', 'value': 1}
    FOUR = {'symbol': '4', 'value': 2}
    FIVE = {'symbol': '5', 'value': 3}
    SIX = {'symbol': '6', 'value': 4}
    SEVEN = {'symbol': '7', 'value': 5}
    EIGHT = {'symbol': '8', 'value': 6}
    NIGHT = {'symbol': '9', 'value': 7}
    TEN = {'symbol': '10', 'value': 8}
    JACK = {'symbol': 'J', 'value': 9}
    QUEEN = {'symbol': 'Q', 'value': 10}
    KING = {'symbol': 'K', 'value': 11}
    ACE = {'symbol': 'A', 'value': 12}


class Card:
    '''撲克牌'''

    def __init__(self, rank: Rank, suit: Suit):
        self.__rank = rank
        self.__suit = suit

    @property
    def rank(self):
        return self.__rank

    @property
    def suit(self):
        return self.__suit

    def __repr__(self):
        return f"{self.__suit.value['symbol']} {self.__rank.value['value']}"


class Deck:
    '''撲克牌牌堆'''

    def __init__(self):
        self.__card_list: List[Card] = []
        for suit in Suit:
            for rank in Rank:
                card = Card(rank, suit)
                self.__card_list.append(card)

    @property
    def cards(self):
        return tuple(self.__card_list)

    @property
    def card_count(self):
        return len(self.__card_list)

    def shuffle(self):
        '''洗牌'''
        random.shuffle(self.__card_list)

    def draw(self) -> Card:
        '''抽牌'''
        return self.__card_list.pop()


class Player(ABC):
    '''玩家'''

    def __init__(self):
        self.__scroe: int = 0
        self.__hand_card_list: List[Card] = []
        self.__name: Optional[str] = None

    @property
    def point(self):
        return self.__scroe

    def add_point(self, score: int):
        '''增加分數'''
        self.__scroe += score

    @property
    def hands(self):
        return tuple(self.__hand_card_list)

    @property
    def hands_count(self):
        return len(self.__hand_card_list)

    def add_hand_card(self, card: Card):
        '''增加手牌'''
        if len(self.hands) >= 13:
            raise ValueError("手牌數量不能超過13張")
        self.__hand_card_list.append(card)

    def drop_hands(self, card: Card):
        self.__hand_card_list.remove(card)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

    @abstractmethod
    def make_decision(self):
        '''玩家做選擇'''
        ...

    @abstractmethod
    def name_self(self):
        '''玩家取名'''
        ...


class HumanPlayer(Player):
    '''人類玩家'''

    def __init__(self):
        super().__init__()

    def make_decision(self) -> Card:
        '''使用指令介面輸入 (Command Line Interface) 來做選擇'''
        try:
            num = eval(input("請輸入你想出第幾張牌的數字: "))
            if num < 0 or num >= self.hands_count:
                raise ValueError(f"Invalid number `{num}`")
        except Exception as e:
            err = Error.from_exc("ValueError", e)
            print(err.title, err.message)
            return self.make_decision()
        choice_card = self.hands[num]
        self.drop_hands(choice_card)
        return choice_card

    def name_self(self):
        '''使用指令介面輸入 (Command Line Interface) 來取名'''
        name = input("請輸入你的名字: ")
        self.name = name


class AIPlayer(Player):
    '''AI玩家'''

    def __init__(self):
        super().__init__()

    def make_decision(self):
        '''AI玩家隨機做選擇'''
        choice_card = random.choice(self.hands)
        self.drop_hands(choice_card)
        return choice_card

    def name_self(self):
        '''AI玩家取名'''
        self.name = "AI Player"


class Showdown:
    '''撲克牌比大小遊戲 (Showdown)'''

    def __init__(self, deck: Deck):
        self.__round: int = 0
        self.__human_num: int = 0
        self.__ai_num: int = 0
        self.player_list: List[Player] = []  # P1 ~ P4
        self.max_support_players: int = 4
        self.deck = deck

    @property
    def round_count(self):
        return self.__round

    @property
    def human_num(self):
        return self.__human_num

    @human_num.setter
    def human_num(self, num: int):
        if num < 0:
            raise ValueError("人數不能為負數")
        if num > self.max_support_players:
            raise ValueError(f"遊戲最多支援{self.max_support_players}人")
        self.__human_num = num
        for _ in range(num):
            player = HumanPlayer()
            self.player_list.append(player)

    @property
    def ai_num(self):
        return self.__ai_num

    @ai_num.setter
    def ai_num(self, num: int):
        if num < 0:
            raise ValueError("人數不能為負數")
        if num > self.max_support_players:
            raise ValueError(f"遊戲最多支援{self.max_support_players}人")
        self.__ai_num = num
        for _ in range(num):
            player = AIPlayer()
            self.player_list.append(player)

    @property
    def total_players(self):
        return self.human_num + self.ai_num

    def input_human_player_number(self):
        human_num = eval(input("輸入人類玩家數量: "))
        try:
            self.human_num = human_num
        except Exception as e:
            err = Error.from_exc("ValueError", e)
            print(err.title, err.message)
            return self.input_human_player_number()

    def input_ai_player_number(self):
        if self.total_players == self.max_support_players:
            return
        # ai_num = eval(input("輸入AI玩家數量: "))
        ai_num = self.max_support_players - self.human_num
        try:
            self.ai_num = ai_num
        except Exception as e:
            err = Error.from_exc("ValueError", e)
            print(err.title, err.message)
            return self.input_ai_player_number()

    def name_players(self):
        for pidx, player in enumerate(self.player_list):
            print(f"輸入 P{pidx+1} 玩家名稱:")
            player.name_self()
            print(f"P{pidx+1} 玩家 {player.name} 加入遊戲")

    def start(self):
        # 設定玩家人數
        self.input_human_player_number()
        self.input_ai_player_number()
        # 請玩家取名
        self.name_players()
        # 洗牌階段
        print("開始洗牌")
        self.deck.shuffle()
        # 抽牌階段
        cards_per_player = 52 // self.total_players
        while sum([p.hands_count for p in self.player_list]) < cards_per_player * self.total_players:
            for player in self.player_list:
                card = self.deck.draw()
                player.add_hand_card(card)
                if self.deck.card_count == 0:
                    print("牌堆已經抽完")
                    break
        # 遊戲回合開始, 直到回合數等於玩家手牌數 或 所有玩家手牌數為0
        while self.round_count <= cards_per_player and sum([p.hands_count for p in self.player_list]) > 0:
            # 開始新的一輪
            self.rount_start()
            # 玩家輪流出牌
            card_list: List[Card] = []
            for player in self.player_list:
                # 是否使用特權
                #
                # 出牌
                card = player.make_decision()
                card_list.append(card)

            print(f'第{self.round_count}局出牌結果: {card_list}')
            # 比牌
            winner_idx = self.compare_cards(card_list)
            print(f'第{self.round_count}局由 P{winner_idx+1} 玩家獲勝')
            self.player_list[winner_idx].add_point(1)

            # 顯示牌
            self.show_cards(card_list)

        # 遊戲結束
        self.stop()

    def rount_start(self):
        '''新的一輪開始'''
        self.__round += 1

    def compare_cards(self, card_list: List[Card]) -> int:
        '''比較出牌
        先比較牌的階級，此時階級較大者勝，如果階級相同則比較花色，此時花色較大者勝。

        Args:
            card_list: 出牌列表

        Return:
            int: 勝利者的索引
        '''
        max_card = card_list[0]
        max_idx = 0
        for idx, card in enumerate(card_list[1:]):
            if card.rank.value['value'] > max_card.rank.value['value']:
                # 階級較大者勝
                max_card = card
                max_idx = idx
            elif card.rank.value['value'] == max_card.rank.value['value']:
                # 階級相同比較花色
                if card.suit.value['value'] > max_card.suit.value['value']:
                    max_card = card
                    max_idx = idx
        return max_idx

    def show_cards(self, card_list: List[Card]):
        print(f'第{self.round_count}局出牌結果: {card_list}')

    def stop(self):
        '''遊戲結束'''
        print('遊戲結束')
        print(f'玩家得分: ', [f'{p.name}: {p.point}' for p in self.player_list])
        max_score = self.player_list[0].point
        max_score_idx = 0
        for idx, player in enumerate(self.player_list[1:]):
            if player.point > max_score:
                max_score = player.point
                max_score_idx = idx + 1
        print(
            f'勝者: P{max_score_idx + 1} {self.player_list[max_score_idx].name}')


if __name__ == '__main__':
    deck = Deck()
    showdown = Showdown(deck)
    showdown.start()
