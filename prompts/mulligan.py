from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.tools.render import render_text_description

import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
llmrootdir = os.path.dirname(currentdir + '/../')
sys.path.insert(0, llmrootdir)
from tools.mulligan import submit_mulligan_decision
from prompts.whoami import AI_ROLE
from prompts.react import REACT_GUIDE

class MulliganPromptPreset():
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(AI_ROLE),
        SystemMessagePromptTemplate.from_template('{data}'),
        SystemMessagePromptTemplate.from_template('Ned Decker (AI) is currently in the mulligan step.'),
        MessagesPlaceholder("chat_history"),
        HumanMessagePromptTemplate.from_template('{input}'),
    ])

    tools = [ submit_mulligan_decision() ]

    tools_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(REACT_GUIDE.format(
            tools=render_text_description(tools),
            tool_names=", ".join([ t.name for t in tools ]),
        )),
        SystemMessagePromptTemplate.from_template(AI_ROLE),
        MessagesPlaceholder("chat_history"),
        HumanMessagePromptTemplate.from_template('{input}'),
    ])

    requests = [
        "1. How many mana sources are there in Ned Decker's hand? (only integer)\n"
        "1a. Classify Ned Decker's hand as one of "
        "["
            "\"mana screw\" (too few mana sources, e.g. one land or less), "
            "\"balanced\", "
            "\"mana flood\" (too many mana sources, e.g. five lands or more) "
        "] "
        "(don't say anything else).\n"
        "1b. State the colors that Ned Decker's lands in hand can produce (use {W}{U}{B}{R}{G}, no duplicates).\n"
        "1c. State the colors that Ned Decker's spells in hand require (use {W}{U}{B}{R}{G}, no duplicates).\n"
        "(If lands cannot provide enough mana or enough color, consider taking a mulligan.)\n"
        "(If there are too many lands and not enough spells, consider taking a mulligan.)\n"
        "2. Are there 2 spells or more that costs more than 3 CMC (Yes/No)?\n"
        "2a. If yes, at what turn can Ned Decker use those spells (only integer)?\n"
        "3. How many cards would be put to the bottom of Ned Decker's library (only integer)?\n"
        "3a. How many cards would be in Ned Decker's hand after bottoming (only integer)?\n"
        "3b. What unwanted, worst card(s) would Ned Decker send to the bottom of the library (give name and ID)?\n"
        "3c. Compile a hand after sending those cards to the bottom of the library (with only name and ID).\n"
        "3d. After bottoming the unwanted cards, is the rest of the hand good enough for keeping?\n"
        "(If there are too many unplayable cards and can't bottom them, consider taking a mulligan.)\n"
        "(IMPORTANT: From now on, analysis should be exclusively based on the compiled hand created in 3c.)\n"
        "4. Please summarize the hand's early game plays for each of [ turn 1, turn 2, turn 3 ] "
        "("
            "reply with format: <format>"
                "turn X => "
                "Land Play (turn X): name of land for turn or \"Missed land drop\" "
                "(and then list all the played lands since turn 1) => "
                "Spell Cast (turn X): cast what spell or \"No spell played (reason)\" "
                "(and then mention the mana cost of each casted spell) "
                "(this step may repeat N times in the same turn) "
                "=> "
                "Pay Cost (turn X, spell=spell_name) (optional): "
                "if one or more spells that costs mana were casted, "
                "tap what land to produce what mana (color, amount) for the cost "
                "(note that one land usually produces one mana);"
            "</format>"
        "), "
        "(please be concise and terse).\n"
        "4a. Has Ned Decker missed any land drop for the turn and lost tempo (Yes/No, and explain why)?\n"
        "4b. Has Ned Decker passed a turn without casting a spell and lost tempo (Yes/No, and explain why)?\n"
        "4c. Did Ned Decker make board pressure or meaningfully interact in the first three turns?\n"
        "(If the early game feels slow and without tempo, strongly consider taking a mulligan.)\n"
        "4d. A Burn deck could deal 21 damage to Ned Decker within four turns; "
        "could Ned Decker race the opponent or survive the first three turns?\n"
        "4e. If the opponent removes some of the early game plays, could Ned Decker keep up without topdecking?\n"
        "4f. Was color an issue or would be an issue (Yes/No only)?\n"
        "(If the early game was not resilient enough, consider taking a mulligan.)\n"
        "5. Analyze why Ned Decker should keep or mulligan (only 1 reason, be super short & terse).\n"
        "5a. Is it worth it to have one less card in hand to see the next seven cards? \n"
        "(If should mulligan but mulligan is not worth having one less card, "
        "then Ned Decker should reluctantly keep instead.)"
        "6. Final Verdict: keep or mulligan (Keep/Mulligan)?\n",
    ]

    def count_lands(hand):
        assert hand and hand[0].get('type_line', None)
        return sum([ 1 if 'land' in card['type_line'].lower() else 0 for card in hand ])

    hand_analysis = "Ned Decker's hand is: <hand>{hand}</hand>. There are {land_count} land(s) in your hand. You will bottom {to_bottom_count} card(s) and have {keep_card_count} cards in hand if you keep."

    _input = "AI may choose to mulligan or to keep the {keep_card_count}-card(s) hand and bottom {to_bottom_count} card(s). Please submit your choice; if you choose to keep, remember to specify what card(s) to bottom using only ID(s)."

    improvement_prompt = (
        "The previous Chain of Thought was intended to make AI Ned Decker to {expected_action} this hand. "
        "However, you chose to {chosen_action}. "
        "The most important question is (answer to best of your knowledge and explain step-by-step): "
        "What guidances in the deduction step made you think that you should {chosen_action}? "
        "And these are some less-important questions: "
        "What {expected_action}-able aspects about this hand did the deduction step miss? "
        "What should be asked instead to make AI Ned Decker {expected_action} this hand?"
    )

if __name__ == '__main__':
    print(MulliganPromptPreset.chat_prompt)
    print(MulliganPromptPreset.tools)
    print(MulliganPromptPreset.tools_prompt)
    print(MulliganPromptPreset.requests)
    print(MulliganPromptPreset.count_lands)
    print(MulliganPromptPreset.hand_analysis)
    print(MulliganPromptPreset._input)
    print(MulliganPromptPreset.improvement_prompt)
