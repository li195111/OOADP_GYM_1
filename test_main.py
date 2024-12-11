import pytest

from main import AIPlayer, Deck, ExchangeHandsPrivilege, Showdown


def test_main():
    privilege_1 = ExchangeHandsPrivilege()
    player_1 = AIPlayer(player_id=1, privilege=privilege_1)
    privilege_2 = ExchangeHandsPrivilege()
    player_2 = AIPlayer(player_id=2, privilege=privilege_2)
    privilege_3 = ExchangeHandsPrivilege()
    player_3 = AIPlayer(player_id=3, privilege=privilege_3)
    privilege_4 = ExchangeHandsPrivilege()
    player_4 = AIPlayer(player_id=4, privilege=privilege_4)

    # 測試牌堆牌的初始數量為52
    deck = Deck()
    assert deck.card_count == 52

    showdown = Showdown(deck)
    showdown.add_player(player_1)
    showdown.add_player(player_2)
    showdown.add_player(player_3)
    showdown.add_player(player_4)

    assert showdown.total_players == 4

    with pytest.raises(ValueError):
        # 測試玩家數量超過4人時會拋出錯誤
        showdown.add_player(player_1)

    showdown.start()
    # 測試遊戲結束時玩家的手牌數量為0
    for player_id, player in showdown.player_map.items():
        assert player.hands_count == 0
