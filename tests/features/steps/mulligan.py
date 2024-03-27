from behave import *
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.agents import create_openai_tools_agent
from langchain.agents import AgentType
from langchain.agents.agent import AgentExecutor
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.tools.render import render_text_description
import re

import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
llmrootdir = os.path.dirname(currentdir + '/../../../')
sys.path.insert(0, llmrootdir)
from payload import g_payload
from prompts.mulligan import MulliganPromptPreset as MPP
from agents.agent import ChatAndThenSubmitAgentExecutor as CSAgentExecutor

from dotenv import load_dotenv
load_dotenv()

@given('the AI player is GPT from OpenAI')
def step_impl(context):
    context.llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0, max_tokens=1024)
    #context.llm = ChatOpenAI(model_name='gpt-4', temperature=0, max_tokens=1024)
    context.tools = MPP.tools
    context.chat_prompt = MPP.chat_prompt
    context.tools_prompt = MPP.tools_prompt
    context.memory = ConversationBufferMemory(memory_key="chat_history", input_key='input', return_messages=True)
    context.requests = MPP.requests
    context.agent_executor = CSAgentExecutor(
            llm=context.llm,
            chat_prompt=context.chat_prompt,
            tools_prompt=context.tools_prompt,
            tools=context.tools,
            memory=context.memory,
            requests=context.requests,
            verbose=True,
    )

@given('the AI player has a perfect hand')
def step_impl(context):
    """ Sets the context.hand with a perfect hand.
    Perfect hand: [ Plains, Plains, Plains, Ornithopter, Sigarda's Aid, Colossus Hammer, Colossus Hammer ]
    This hand enables a turn two win on the play:
    Turn 1: Plains, Ornithopter, Sigarda's Aid
    Turn 2: Plains, attack with Ornithopter, flash in two Colossal Hammers to deal 20 damage
    See https://youtu.be/AUEnIlIDDX4?t=652 for video demo by The Professor from Tolarian Community College
    """
    context.hand = [
        {
            "in_game_id": "n1#1",
            "name": "Plains", "mana_cost": None,
            "type_line": "Basic land - Plains",
            "oracle_text": "({T}: add {W}.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n1#2",
            "name": "Plains", "mana_cost": None,
            "type_line": "Basic land - Plains",
            "oracle_text": "({T}: add {W}.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n1#3",
            "name": "Plains", "mana_cost": None,
            "type_line": "Basic land - Plains",
            "oracle_text": "({T}: add {W}.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n2#1",
            "name": "Ornithopter", "mana_cost": "{0}",
            "type_line": "Artifact Creature - Thopter",
            "oracle_text": "Flying",
            "power": "0", "toughness": "2",
        },
        {
            "in_game_id": "n3#1",
            "name": "Sigarda's Aid", "mana_cost": "{W}",
            "type_line": "Enchantment",
            "oracle_text": "You may cast Aura and Equipment spells as though they had flash.\nWhenever an Equipment enters the battlefield under your control, you may attach it to target creature you control.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n4#1",
            "name": "Colossus Hammer", "mana_cost": "{1}",
            "type_line": "Artifact - Equipment",
            "oracle_text": "Equipped creature gets +10/+10 and loses flying.\nEquip {8} ({8}: Attach to target creature you control. Equip only as a sorcery.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n4#2",
            "name": "Colossus Hammer", "mana_cost": "{1}",
            "type_line": "Artifact - Equipment",
            "oracle_text": "Equipped creature gets +10/+10 and loses flying.\nEquip {8} ({8}: Attach to target creature you control. Equip only as a sorcery.)",
            "power": None, "toughness": None,
        },
    ]

@given('the AI player has a decent hand')
def step_impl(context):
    """ Sets the context.hand with a decent hand.
    Decent hand: [ Urza's Mine, Island, Island, Expedition Map, Condescend, Wurmcoil Engine, Solemn Simulacrum ]
    This hand was listed as a "keepable hand" in the Mono U Tron 99-page primer.
    https://raw.githubusercontent.com/TKOS7/Mono-U-Tron/master/Mono%20U%20Tron%20v2.0.pdf
    """
    context.hand = [
        {
            "in_game_id": "n1#1",
            "name": "Urza's Mine", "mana_cost": None,
            "type_line": "Land - Urza's Mine",
            "oracle_text": "{T}: Add {C}. If you control an Urza’s Power-Plant and an Urza’s Tower, add {C}{C} instead.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n2#1",
            "name": "Island", "mana_cost": None,
            "type_line": "Basic land - Island",
            "oracle_text": "({T}: add {U}.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n2#2",
            "name": "Island", "mana_cost": None,
            "type_line": "Basic land - Island",
            "oracle_text": "({T}: add {U}.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n3#1",
            "name": "Expedition Map", "mana_cost": "{1}",
            "type_line": "Artifact",
            "oracle_text": "{2}, {T}, Sacrifice Expedition Map: Search your library for a land card, reveal it, put it into your hand, then shuffle.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n4#1",
            "name": "Condescend", "mana_cost": "{X}{U}",
            "type_line": "Instant",
            "oracle_text": "Counter target spell unless its controller pays {X}. Scry 2. (Look at the top two cards of your library, then put any number of them on the bottom of your library and the rest on top in any order.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n5#1",
            "name": "Wurmcoil Engine", "mana_cost": "{6}",
            "type_line": "Artifact Creature - Phyrexian Wurm",
            "oracle_text": "Deathtouch, lifelink\nWhen Wurmcoil Engine dies, create a 3/3 colorless Phyrexian Wurm artifact creature token with deathtouch and a 3/3 colorless Phyrexian Wurm artifact creature token with lifelink.",
            "power": "6", "toughness": "6",
        },
        {
            "in_game_id": "n6#1",
            "name": "Solemn Simulacrum", "mana_cost": "{4}",
            "type_line": "Artifact Creature - Golem",
            "oracle_text": "When Solemn Simulacrum enters the battlefield, you may search your library for a basic land card, put that card onto the battlefield tapped, then shuffle.\nWhen Solemn Simulacrum dies, you may draw a card.",
            "power": "2", "toughness": "2",
        },
    ]

@given('the AI player has only one land in hand')
def step_impl(context):
    """ Sets the context.hand with a one-land hand.
    One-land hand (UW control): [
        Flooded Strand,
        The One Ring,
        Counterspell,
        Counterspell,
        Day's Undoing,
        Supreme Verdict,
        Teferi, Time Raveler,
    ]
    """
    context.hand = [
        {
            "in_game_id": "n1#1",
            "name": "Flooded Strand", "mana_cost": None,
            "type_line": "Land",
            "oracle_text": "{T}, Pay 1 life, Sacrifice Flooded Strand: Search your library for a Plains or Island card, put it onto the battlefield, then shuffle.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n2#1",
            "name": "The One Ring", "mana_cost": "{4}",
            "type_line": "Legendary Artifact",
            "oracle_text": "Indestructible\nWhen The One Ring enters the battlefield, if you cast it, you gain protection from everything until your next turn.\nAt the beginning of your upkeep, you lose 1 life for each burden counter on The One Ring.\n{1}, {T}: Put a burden counter on The One Ring, then draw a card for each burden counter on The One Ring.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n3#1",
            "name": "Counterspell", "mana_cost": "{U}{U}",
            "type_line": "Instant",
            "oracle_text": "Counter target spell.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n3#2",
            "name": "Counterspell", "mana_cost": "{U}{U}",
            "type_line": "Instant",
            "oracle_text": "Counter target spell.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n4#1",
            "name": "Day's Undoing", "mana_cost": "{2}{U}",
            "type_line": "Sorcery",
            "oracle_text": "Each player shuffles their hand and graveyard into their library, then draws seven cards. If it’s your turn, end the turn. (Exile all spells and abilities from the stack, including this card. Discard down to your maximum hand size. Damage wears off, and “this turn” and “until end of turn” effects end.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n5#1",
            "name": "Supreme Verdict", "mana_cost": "{1}{W}{W}{U}",
            "type_line": "Sorcery",
            "oracle_text": "This spell can’t be countered.\nDestroy all creatures.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n6#1",
            "name": "Teferi, Time Raveler", "mana_cost": "{1}{W}{U}",
            "type_line": "Legendary Planeswalker - Teferi",
            "oracle_text": "Each opponent can cast spells only any time they could cast a sorcery.\n+1: Until your next turn, you may cast sorcery spells as though they had flash.\n−3: Return up to one target artifact, creature, or enchantment to its owner’s hand. Draw a card.",
            "power": None, "toughness": None,
            "loyalty": "4",
        },
    ]

@given('the AI player has six lands in hand')
def step_impl(context):
    """ Sets the context.hand with a six-land hand.
    Six-land hand (Burn): [
        Mountain,
        Mountain,
        Inspiring Vantage,
        Arid Mesa,
        Sunbaked Canyon,
        Sunbaked Canyon,
        Monastery Swiftspear,
    ]
    """
    context.hand = [
        {
            "in_game_id": "n1#1",
            "name": "Mountain", "mana_cost": None,
            "type_line": "Basic Land - Mountain",
            "oracle_text": "({T}: Add {R}.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n1#2",
            "name": "Mountain", "mana_cost": None,
            "type_line": "Basic Land - Mountain",
            "oracle_text": "({T}: Add {R}.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n2#1",
            "name": "Inspiring Vantage", "mana_cost": None,
            "type_line": "Land",
            "oracle_text": "Inspiring Vantage enters the battlefield tapped unless you control two or fewer other lands.\n{T}: Add {R} or {W}.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n3#1",
            "name": "Arid Mesa", "mana_cost": None,
            "type_line": "Land",
            "oracle_text": "{T}, Pay 1 life, Sacrifice Arid Mesa: Search your library for a Mountain or Plains card, put it onto the battlefield, then shuffle.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n4#1",
            "name": "Sunbaked Canyon", "mana_cost": None,
            "type_line": "Land",
            "oracle_text": "{T}, Pay 1 life: Add {R} or {W}.\n{1}, {T}, Sacrifice Sunbaked Canyon: Draw a card.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n4#2",
            "name": "Sunbaked Canyon", "mana_cost": None,
            "type_line": "Land",
            "oracle_text": "{T}, Pay 1 life: Add {R} or {W}.\n{1}, {T}, Sacrifice Sunbaked Canyon: Draw a card.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n5#1",
            "name": "Monastery Swiftspear", "mana_cost": "{R}",
            "type_line": "Creature - Human Monk",
            "oracle_text": "Haste\nProwess (Whenever you cast a noncreature spell, this creature gets +1/+1 until end of turn.)",
            "power": "1", "toughness": "2",
        },
    ]

@given('the AI player has three lands and four unplayable spells')
def step_impl(context):
    """ Sets the context.hand with a three-land, four-unplayable-spell hand.
    Unplayable hand (Goryo's Vengeance): [
        Godless Shrine,
        Hallowed Fountain,
        Flooded Strand,
        Atraxa, Grand Unifier,
        Atraxa, Grand Unifier,
        Griselbrand,
        Griselbrand,
    ]
    """
    context.hand = [
        {
            "in_game_id": "n1#1",
            "name": "Godless Shrine", "mana_cost": None,
            "type_line": "Land - Plains Swamp",
            "oracle_text": "({T}: Add {W} or {B}.)\nAs Godless Shrine enters the battlefield, you may pay 2 life. If you don’t, it enters the battlefield tapped.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n2#1",
            "name": "Hallowed Fountain", "mana_cost": None,
            "type_line": "Land - Plains Island",
            "oracle_text": "({T}: Add {W} or {U}.)\nAs Hallowed Fountain enters the battlefield, you may pay 2 life. If you don’t, it enters the battlefield tapped.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n3#1",
            "name": "Flooded Strand", "mana_cost": None,
            "type_line": "Land",
            "oracle_text": "{T}, Pay 1 life, Sacrifice Flooded Strand: Search your library for a Plains or Island card, put it onto the battlefield, then shuffle.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n4#1",
            "name": "Atraxa, Grand Unifier", "mana_cost": "{3}{G}{W}{U}{B}",
            "type_line": "Legendary Creature - Phyrexian Angel",
            "oracle_text": "Flying, vigilance, deathtouch, lifelink\nWhen Atraxa, Grand Unifier enters the battlefield, reveal the top ten cards of your library. For each card type, you may put a card of that type from among the revealed cards into your hand. Put the rest on the bottom of your library in a random order. (Artifact, battle, creature, enchantment, instant, land, planeswalker, and sorcery are card types.)",
            "power": "7", "toughness": "7",
        },
        {
            "in_game_id": "n4#2",
            "name": "Atraxa, Grand Unifier", "mana_cost": "{3}{G}{W}{U}{B}",
            "type_line": "Legendary Creature - Phyrexian Angel",
            "oracle_text": "Flying, vigilance, deathtouch, lifelink\nWhen Atraxa, Grand Unifier enters the battlefield, reveal the top ten cards of your library. For each card type, you may put a card of that type from among the revealed cards into your hand. Put the rest on the bottom of your library in a random order. (Artifact, battle, creature, enchantment, instant, land, planeswalker, and sorcery are card types.)",
            "power": "7", "toughness": "7",
        },
        {
            "in_game_id": "n5#1",
            "name": "Griselbrand", "mana_cost": "{4}{B}{B}{B}{B}",
            "type_line": "Legendary Creature - Demon",
            "oracle_text": "Flying, lifelink\nPay 7 life: Draw seven cards.",
            "power": "7", "toughness": "7",
        },
        {
            "in_game_id": "n5#2",
            "name": "Griselbrand", "mana_cost": "{4}{B}{B}{B}{B}",
            "type_line": "Legendary Creature - Demon",
            "oracle_text": "Flying, lifelink\nPay 7 life: Draw seven cards.",
            "power": "7", "toughness": "7",
        },
    ]

@given('the AI player has one land, two early game cards, and four unplayable cards')
def step_impl(context):
    """ Sets the context.hand with a one land, two playable, and four unplayable hand.
    Risky hand (Murktide): [
        Steam Vents,
        Ragavan, Nimble Pilferer,
        Lightning Bolt,
        Murktide Regent,
        Murktide Regent,
        Murktide Regent,
        Brotherhood's End,
    ]
    """
    context.hand = [
        {
            "in_game_id": "n1#1",
            "name": "Steam Vents", "mana_cost": None,
            "type_line": "Land - Island Mountain",
            "oracle_text": "({T}: Add {U} or {R}.)\nAs Steam Vents enters the battlefield, you may pay 2 life. If you don’t, it enters the battlefield tapped.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n2#1",
            "name": "Ragavan, Nimble Pilferer", "mana_cost": "{R}",
            "type_line": "Legendary Creature - Monkey Pirate",
            "oracle_text": "Whenever Ragavan, Nimble Pilferer deals combat damage to a player, create a Treasure token and exile the top card of that player’s library. Until end of turn, you may cast that card.\nDash {1}{R} (You may cast this spell for its dash cost. If you do, it gains haste, and it’s returned from the battlefield to its owner’s hand at the beginning of the next end step.)",
            "power": "2", "toughness": "1",
        },
        {
            "in_game_id": "n3#1",
            "name": "Lightning Bolt", "mana_cost": "{R}",
            "type_line": "Instant",
            "oracle_text": "Lightning Bolt deals 3 damage to any target.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n4#1",
            "name": "Murktide Regent", "mana_cost": "{5}{U}{U}",
            "type_line": "Creature — Dragon",
            "oracle_text": "Delve (Each card you exile from your graveyard while casting this spell pays for {1}.)\nFlying\nMurktide Regent enters the battlefield with a +1/+1 counter on it for each instant and sorcery card exiled with it.\nWhenever an instant or sorcery card leaves your graveyard, put a +1/+1 counter on Murktide Regent.",
            "power": "3", "toughness": "3",
        },
        {
            "in_game_id": "n4#2",
            "name": "Murktide Regent", "mana_cost": "{5}{U}{U}",
            "type_line": "Creature — Dragon",
            "oracle_text": "Delve (Each card you exile from your graveyard while casting this spell pays for {1}.)\nFlying\nMurktide Regent enters the battlefield with a +1/+1 counter on it for each instant and sorcery card exiled with it.\nWhenever an instant or sorcery card leaves your graveyard, put a +1/+1 counter on Murktide Regent.",
            "power": "3", "toughness": "3",
        },
        {
            "in_game_id": "n4#3",
            "name": "Murktide Regent", "mana_cost": "{5}{U}{U}",
            "type_line": "Creature — Dragon",
            "oracle_text": "Delve (Each card you exile from your graveyard while casting this spell pays for {1}.)\nFlying\nMurktide Regent enters the battlefield with a +1/+1 counter on it for each instant and sorcery card exiled with it.\nWhenever an instant or sorcery card leaves your graveyard, put a +1/+1 counter on Murktide Regent.",
            "power": "3", "toughness": "3",
        },
        {
            "in_game_id": "n5#2",
            "name": "Brotherhood's End", "mana_cost": "{1}{R}{R}",
            "type_line": "Sorcery",
            "oracle_text": "Choose one -\n- Brotherhood’s End deals 3 damage to each creature and each planeswalker.\n- Destroy all artifacts with mana value 3 or less.",
            "power": None, "toughness": None,
        },
    ]

@given("the AI player has three Plains, two Dovin's Veto that costs a white and a blue mana, and two unplayable cards")
def step_impl(context):
    """ Sets the context.hand with a three plains, two dovin's veto, two unplayable hand.
    Color screw hand (UW Control): [
        Plains,
        Plains,
        Plains,
        Dovin's Veto,
        Dovin's Veto,
        Archmage's Charm,
        Supreme Verdit,
    ]
    """
    context.hand = [
        {
            "in_game_id": "n1#1",
            "name": "Plains", "mana_cost": None,
            "type_line": "Basic land - Plains",
            "oracle_text": "({T}: add {W}.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n1#2",
            "name": "Plains", "mana_cost": None,
            "type_line": "Basic land - Plains",
            "oracle_text": "({T}: add {W}.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n1#3",
            "name": "Plains", "mana_cost": None,
            "type_line": "Basic land - Plains",
            "oracle_text": "({T}: add {W}.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n2#1",
            "name": "Dovin's Veto", "mana_cost": "{W}{U}",
            "type_line": "Instant",
            "oracle_text": "This spell can’t be countered.\nCounter target noncreature spell.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n2#2",
            "name": "Dovin's Veto", "mana_cost": "{W}{U}",
            "type_line": "Instant",
            "oracle_text": "This spell can’t be countered.\nCounter target noncreature spell.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n3#1",
            "name": "Archmage's Charm", "mana_cost": "{U}{U}{U}",
            "type_line": "Instant",
            "oracle_text": "Choose one -\n- Counter target spell.\n- Target player draws two cards.\n- Gain control of target nonland permanent with mana value 1 or less.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n4#1",
            "name": "Supreme Verdict", "mana_cost": "{1}{W}{W}{U}",
            "type_line": "Sorcery",
            "oracle_text": "This spell can’t be countered.\nDestroy all creatures.",
            "power": None, "toughness": None,
        },
    ]
    pass

@given("the AI player has two Plains, a Flooded Strand, two Dovin's Veto that costs a white and a blue mana, and two unplayable cards")
def step_impl(context):
    """ Sets the context.hand with a two plains, one flooded strand, two dovin's veto, two unplayable hand.
    Risky hand (Murktide): [
        Plains,
        Plains,
        Flooded Strand,
        Dovin's Veto,
        Dovin's Veto,
        Archmage's Charm,
        Supreme Verdit,
    ]
    """
    context.hand = [
        {
            "in_game_id": "n1#1",
            "name": "Plains", "mana_cost": None,
            "type_line": "Basic land - Plains",
            "oracle_text": "({T}: add {W}.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n1#2",
            "name": "Plains", "mana_cost": None,
            "type_line": "Basic land - Plains",
            "oracle_text": "({T}: add {W}.)",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n2#1",
            "name": "Flooded Strand", "mana_cost": None,
            "type_line": "Land",
            "oracle_text": "{T}, Pay 1 life, Sacrifice Flooded Strand: Search your library for a Plains or Island card, put it onto the battlefield, then shuffle.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n3#1",
            "name": "Dovin's Veto", "mana_cost": "{W}{U}",
            "type_line": "Instant",
            "oracle_text": "This spell can’t be countered.\nCounter target noncreature spell.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n3#2",
            "name": "Dovin's Veto", "mana_cost": "{W}{U}",
            "type_line": "Instant",
            "oracle_text": "This spell can’t be countered.\nCounter target noncreature spell.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n4#1",
            "name": "Archmage's Charm", "mana_cost": "{U}{U}{U}",
            "type_line": "Instant",
            "oracle_text": "Choose one -\n- Counter target spell.\n- Target player draws two cards.\n- Gain control of target nonland permanent with mana value 1 or less.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n5#1",
            "name": "Supreme Verdict", "mana_cost": "{1}{W}{W}{U}",
            "type_line": "Sorcery",
            "oracle_text": "This spell can’t be countered.\nDestroy all creatures.",
            "power": None, "toughness": None,
        },
    ]
    pass

@given('the AI player has two lands, two playable cards, and three unplayable cards')
def step_impl(context):
    """ Sets the context.hand with a two land, two playable, and three unplayable hand.
    Risky hand (Murktide): [
        Fiery Islet
        Steam Vents,
        Ragavan, Nimble Pilferer,
        Lightning Bolt,
        Murktide Regent,
        Murktide Regent,
        Murktide Regent,
    ]
    """
    context.hand = [
        {
            "in_game_id": "n1#1",
            "name": "Fiery Islet", "mana_cost": None,
            "type_line": "Land",
            "oracle_text": "{T}, Pay 1 life: Add {U} or {R}.\n{1}, {T}, Sacrifice Fiery Islet: Draw a card.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n2#1",
            "name": "Steam Vents", "mana_cost": None,
            "type_line": "Land - Island Mountain",
            "oracle_text": "({T}: Add {U} or {R}.)\nAs Steam Vents enters the battlefield, you may pay 2 life. If you don’t, it enters the battlefield tapped.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n3#1",
            "name": "Ragavan, Nimble Pilferer", "mana_cost": "{R}",
            "type_line": "Legendary Creature - Monkey Pirate",
            "oracle_text": "Whenever Ragavan, Nimble Pilferer deals combat damage to a player, create a Treasure token and exile the top card of that player’s library. Until end of turn, you may cast that card.\nDash {1}{R} (You may cast this spell for its dash cost. If you do, it gains haste, and it’s returned from the battlefield to its owner’s hand at the beginning of the next end step.)",
            "power": "2", "toughness": "1",
        },
        {
            "in_game_id": "n4#1",
            "name": "Lightning Bolt", "mana_cost": "{R}",
            "type_line": "Instant",
            "oracle_text": "Lightning Bolt deals 3 damage to any target.",
            "power": None, "toughness": None,
        },
        {
            "in_game_id": "n5#1",
            "name": "Murktide Regent", "mana_cost": "{5}{U}{U}",
            "type_line": "Creature — Dragon",
            "oracle_text": "Delve (Each card you exile from your graveyard while casting this spell pays for {1}.)\nFlying\nMurktide Regent enters the battlefield with a +1/+1 counter on it for each instant and sorcery card exiled with it.\nWhenever an instant or sorcery card leaves your graveyard, put a +1/+1 counter on Murktide Regent.",
            "power": "3", "toughness": "3",
        },
        {
            "in_game_id": "n5#2",
            "name": "Murktide Regent", "mana_cost": "{5}{U}{U}",
            "type_line": "Creature — Dragon",
            "oracle_text": "Delve (Each card you exile from your graveyard while casting this spell pays for {1}.)\nFlying\nMurktide Regent enters the battlefield with a +1/+1 counter on it for each instant and sorcery card exiled with it.\nWhenever an instant or sorcery card leaves your graveyard, put a +1/+1 counter on Murktide Regent.",
            "power": "3", "toughness": "3",
        },
        {
            "in_game_id": "n5#3",
            "name": "Murktide Regent", "mana_cost": "{5}{U}{U}",
            "type_line": "Creature — Dragon",
            "oracle_text": "Delve (Each card you exile from your graveyard while casting this spell pays for {1}.)\nFlying\nMurktide Regent enters the battlefield with a +1/+1 counter on it for each instant and sorcery card exiled with it.\nWhenever an instant or sorcery card leaves your graveyard, put a +1/+1 counter on Murktide Regent.",
            "power": "3", "toughness": "3",
        },
    ]

@when('the system says hello to the AI player')
def step_impl(context):
    context.response = context.agent_executor.chatter.invoke({
        'data': "It's a good day for a Magic tournament.",
        'input': 'Hello, my opponent! High roll?',
    })

@when('the system asks the AI player for mulligan decision (bottoming 0)')
def step_impl(context):
    if not hasattr(context, 'hand'):
        return
    to_bottom_count = 0
    land_count = MPP.count_lands(context.hand)
    hand_analysis = MPP.hand_analysis.format(
            hand=context.hand,
            land_count=land_count,
            to_bottom_count=to_bottom_count,
            keep_card_count=7-to_bottom_count,
    )
    _input = MPP._input.format(
            to_bottom_count=to_bottom_count,
            keep_card_count=7-to_bottom_count,
    )
    context.response = context.agent_executor.invoke({
        'data': hand_analysis,
        'input': _input,
    })

@when('the system asks the AI player for mulligan decision (bottoming 2)')
def step_impl(context):
    if not hasattr(context, 'hand'):
        return
    to_bottom_count = 2
    land_count = MPP.count_lands(context.hand)
    hand_analysis = MPP.hand_analysis.format(
            hand=context.hand,
            land_count=land_count,
            to_bottom_count=to_bottom_count,
            keep_card_count=7-to_bottom_count,
    )
    _input = MPP._input.format(
            to_bottom_count=to_bottom_count,
            keep_card_count=7-to_bottom_count,
    )
    context.response = context.agent_executor.invoke({
        'data': hand_analysis,
        'input': _input,
    })

@then('the AI player responds with something')
def step_impl(context):
    assert context.response

@then('the AI player responds to keep')
def step_impl(context):
    if not hasattr(context, 'response'):
        return
    assert context.response.get('output', None)
    try:
        assert g_payload.get('type', '') == 'keep_hand'
    except AssertionError as e:
        improvement = context.agent_executor.chatter.invoke({
            'data': '',
            'input': MPP.improvement_prompt.format(expected_action='keep', chosen_action='mulligan'),
        })
        raise Exception('[improvement]: ' + improvement) from e


@then('the AI player responds to mulligan')
def step_impl(context):
    if not hasattr(context, 'response'):
        return
    assert context.response.get('output', None)
    try:
        assert g_payload.get('type', '') == 'mulligan'
    except AssertionError as e:
        improvement = context.agent_executor.chatter.invoke({
            'data': '',
            'input': MPP.improvement_prompt.format(expected_action='mulligan', chosen_action='keep'),
        })
        raise Exception('[improvement]: ' + improvement) from e
