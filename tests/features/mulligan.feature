Feature: AI player acts in the mulligan phase of an Magic: the Gathering game

    Background: the AI player is connected via OpneAI's API
        Given the AI player is GPT from OpenAI

    Scenario: Say hello to the AI player
        When the system says hello to the AI player
        Then the AI player responds with something

    Scenario: AI player keeps a perfect hand
        Given the AI player has a perfect hand
        When the system asks the AI player for mulligan decision (bottoming 0)
        Then the AI player responds to keep

    Scenario: AI player keeps a decent hand
        Given the AI player has a decent hand
        When the system asks the AI player for mulligan decision (bottoming 0)
        Then the AI player responds to keep

    Scenario: AI player mulligans a hand with too few lands
        Given the AI player has only one land in hand
        When the system asks the AI player for mulligan decision (bottoming 0)
        Then the AI player responds to mulligan

    Scenario: AI player mulligans a hand with too many lands
        Given the AI player has six lands in hand
        When the system asks the AI player for mulligan decision (bottoming 0)
        Then the AI player responds to mulligan

    Scenario: AI player mulligans an unplayable hand
        Given the AI player has three lands and four unplayable spells
        When the system asks the AI player for mulligan decision (bottoming 0)
        Then the AI player responds to mulligan

    Scenario: AI player mulligans a risky hand
        Given the AI player has one land, two early game cards, and four unplayable cards
        When the system asks the AI player for mulligan decision (bottoming 0)
        Then the AI player responds to mulligan

    Scenario: AI player mulligans a potential color screw
        Given the AI player has three Plains, two Dovin's Veto that costs a white and a blue mana, and two unplayable cards
        When the system asks the AI player for mulligan decision (bottoming 0)
        Then the AI player responds to mulligan

    Scenario: AI player knows fetch land can save color screw
        Given the AI player has two Plains, a Flooded Strand, two Dovin's Veto that costs a white and a blue mana, and two unplayable cards
        When the system asks the AI player for mulligan decision (bottoming 0)
        Then the AI player responds to keep

    Scenario: AI player reluctantly keeps a mediocre five card hand
        Given the AI player has two lands, two playable cards, and three unplayable cards
        When the system asks the AI player for mulligan decision (bottoming 2)
        Then the AI player responds to keep
