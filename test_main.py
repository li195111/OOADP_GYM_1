import pytest
from main import Deck, Showdown


def test_main(monkeypatch):
    inputs = iter(["0"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    # 測試牌堆牌的初始數量為52
    deck = Deck()
    assert deck.card_count == 52

    showdown = Showdown(deck)
    showdown.start()
    # 測試遊戲結束時玩家的手牌數量為0
    for player_id, player in showdown.player_map.items():
        assert player.hands_count == 0
