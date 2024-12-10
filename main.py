from __future__ import annotations

import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional

from models.base import Error


class ExchangeHandsPrivilege:

    def __init__(self):
        self.__use_count = 0
        self.__use_round = None
        self.__source_player = None
        self.__target_player = None
        self.__is_expired = False

    @property
    def use_count(self):
        return self.__use_count

    @property
    def source_player(self):
        return self.__source_player

    @property
    def target_player(self):
        return self.__target_player

    @property
    def exchange_round(self):
        return self.__use_round

    @property
    def is_expired(self):
        return self.__is_expired

    @is_expired.setter
    def is_expired(self, is_expired: bool):
        self.__is_expired = is_expired

    def use(self, round: int, src_player: Player, tgt_player: Player):
        if self.use_count == 1:
            raise ValueError("特權已經使用過了")
        print(f"P{src_player.id} 對 P{tgt_player.id}使用特權")
        self.__use_round = round
        self.__source_player = src_player
        self.__target_player = tgt_player
        self.__use_count += 1
        # 交換手牌
        self.source_player.hands, self.target_player.hands = self.target_player.hands, self.source_player.hands

    def restore(self):
        if not self.target_player or not self.use_count:
            raise ValueError("尚未使用特權，無法回復手牌")
        # 交換手牌回復
        self.source_player.hands, self.target_player.hands = self.target_player.hands, self.source_player.hands
        self.is_expired = True


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
        return f"{self.__suit.value['symbol']} {self.__rank.value['symbol']}"


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

    def __init__(self, player_id: int, privilege: ExchangeHandsPrivilege):
        self.__id = player_id
        self.__scroe: int = 0
        self.__hand_card_list: List[Card] = []
        self.__name: Optional[str] = None
        self.privilege = privilege

    @property
    def id(self):
        return self.__id

    @property
    def point(self):
        return self.__scroe

    def add_point(self, score: int):
        '''增加分數'''
        self.__scroe += score

    @property
    def hands(self):
        return self.__hand_card_list

    @hands.setter
    def hands(self, cards: List[Card]):
        self.__hand_card_list = cards

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

    @abstractmethod
    def use_privilege(self, round: int, player_map: Dict[int, Player]):
        '''使用特權'''
        ...


class HumanPlayer(Player):
    '''人類玩家'''

    def __init__(self, player_id: int, privilege: ExchangeHandsPrivilege):
        super().__init__(player_id=player_id, privilege=privilege)

    def make_decision(self) -> Card:
        '''使用指令介面輸入 (Command Line Interface) 來做選擇'''
        if self.hands_count == 0:
            # 手牌已經出完
            return
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
        name = input(f"P{self.id} 請輸入你的名字: ")
        self.name = name
        print(f"P{self.id} 玩家 {name} 加入遊戲")

    def use_privilege(self, round: int, player_map: Dict[int, Player]):
        '''使用特權'''
        if self.privilege.use_count == 0:
            is_use_privilege = input("是否使用特權? (Y/n): ")
            if is_use_privilege.lower() == 'y':
                print(f"{self.name} 使用特權")
                player_names = [f'P{player_id} {p.name}' for player_id,
                                p in player_map.items() if p != self]
                player_id_list = list(player_map.keys())
                min_id = min(player_id_list)
                max_id = max(player_id_list)
                num = eval(
                    input(f"玩家列表:\n{player_names}\n請輸入{min_id}~{max_id}來指定交換手牌的玩家: "))
                if not num in player_map:
                    raise ValueError(f"Invalid number `{num}`")
                player = player_map[num]
                self.privilege.use(round, self, player)
        else:
            # 檢查是否要回復手牌
            if not self.privilege.is_expired and round - self.privilege.exchange_round > 3:
                print(f"P{self.id} 特權失效，回復手牌")
                self.privilege.restore()


class AIPlayer(Player):
    '''AI玩家'''

    def __init__(self, player_id: int, privilege: ExchangeHandsPrivilege):
        super().__init__(player_id=player_id, privilege=privilege)

    def make_decision(self):
        '''AI玩家隨機做選擇'''
        if self.hands_count == 0:
            # 手牌已經出完
            return
        choice_card = random.choice(self.hands)
        self.drop_hands(choice_card)
        return choice_card

    def name_self(self):
        '''AI玩家取名'''
        self.name = f"AI Player-{self.id}"
        print(f"P{self.id} 玩家 {self.name} 加入遊戲")

    def use_privilege(self, round: int, player_map: Dict[int, Player]):
        '''使用特權，AI玩家隨機做選擇'''
        if self.privilege.use_count == 0:
            is_use_privilege = random.random() > 0.5
            if is_use_privilege:
                # 隨機選擇除了自己以外的一位玩家
                player = random.choice(
                    [p for p in player_map.values() if p != self])
                self.privilege.use(round, self, player)
        else:
            # 檢查是否要回復手牌
            if not self.privilege.is_expired and round - self.privilege.exchange_round > 3:
                print(f"P{self.id} 特權失效，回復手牌")
                self.privilege.restore()


class Showdown:
    '''撲克牌比大小遊戲 (Showdown)'''

    def __init__(self, deck: Deck):
        self.__round: int = 0
        self.__human_num: int = 0
        self.__ai_num: int = 0
        self.player_map: Dict[int, Player] = {}  # P1 ~ P4
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
            privilege = ExchangeHandsPrivilege()
            player_id = len(self.player_map) + 1
            player = HumanPlayer(player_id=player_id, privilege=privilege)
            self.player_map[player_id] = player

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
            privilege = ExchangeHandsPrivilege()
            player_id = len(self.player_map) + 1
            player = AIPlayer(player_id=player_id, privilege=privilege)
            self.player_map[player_id] = player

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
        for player in self.player_map.values():
            player.name_self()

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
        hands_count_limit = 13
        while sum([p.hands_count == hands_count_limit for _, p in self.player_map.items()]) != self.total_players:
            for player_id, player in self.player_map.items():

                card = self.deck.draw()

                player.add_hand_card(card)

                if self.deck.card_count == 0:
                    print("牌堆已經抽完")
                    break

        # 遊戲回合開始, 直到回合數等於玩家手牌數 或 所有玩家手牌數為0
        # 13回合後 且 玩家手牌數=0 時結束
        while self.round_count < hands_count_limit or \
                sum([p.hands_count for _, p in self.player_map.items()]) > 0:

            # 顯示玩家剩餘手牌
            for player_id, player in self.player_map.items():
                print(f'P{player_id} 剩餘手牌: ', player.hands_count)

            # 開始新的一輪
            self.rount_start()

            # 玩家輪流出牌
            card_map: Dict[int, Card] = {}
            for player_id, player in self.player_map.items():

                # 是否使用特權 or 是否三回合後回復手牌
                player.use_privilege(self.round_count, self.player_map)

                # 出牌
                card = player.make_decision()
                if not card:
                    # 手牌已經出完, 不參與比牌
                    continue
                card_map[player_id] = card

            # 比牌
            winner_id = self.compare_cards(card_map)
            print(f'第{self.round_count}局由 P{winner_id} 玩家獲勝')
            self.player_map[winner_id].add_point(1)

            # 顯示牌
            self.show_cards(card_map)

        # 遊戲結束
        self.stop()

    def rount_start(self):
        '''新的一輪開始'''
        self.__round += 1

    def compare_cards(self, card_map: Dict[int, Card]) -> int:
        '''比較出牌
        先比較牌的階級，此時階級較大者勝，如果階級相同則比較花色，此時花色較大者勝。

        Args:
            card_list: 出牌列表

        Return:
            int: 勝利者的索引
        '''
        player_ids = list(card_map.keys())
        max_id = player_ids[0]
        max_card = card_map[max_id]
        for player_id in player_ids[1:]:
            card = card_map[player_id]
            if card.rank.value['value'] > max_card.rank.value['value']:
                # 階級較大者勝
                max_card = card
                max_id = player_id
            elif card.rank.value['value'] == max_card.rank.value['value']:
                # 階級相同比較花色
                if card.suit.value['value'] > max_card.suit.value['value']:
                    max_card = card
                    max_id = player_id
        return max_id

    def show_cards(self, card_map: Dict[int, Card]):
        print(f'第{self.round_count}局出牌結果: {card_map}')

    def stop(self):
        '''遊戲結束'''
        print('遊戲結束')
        print(f'玩家得分: ', [
              f'{p.name}: {p.point}' for _, p in self.player_map.items()])
        player_ids = list(self.player_map.keys())
        max_score_idx = player_ids[0]
        max_score = self.player_map[max_score_idx].point
        for player_id in player_ids[1:]:
            player = self.player_map[player_id]
            if player.point > max_score:
                max_score = player.point
                max_score_idx = player_id
        print(
            f'勝者: P{max_score_idx} {self.player_map[max_score_idx].name}')


if __name__ == '__main__':
    deck = Deck()
    showdown = Showdown(deck)
    showdown.start()
