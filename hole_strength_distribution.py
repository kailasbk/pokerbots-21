from cards import all_cards_excluding, draw_random_cards, sort_cards, hole_strengths

deck = all_cards_excluding()
sample_hole_strengths = []
for _ in range(10000):
    hole_cards = draw_random_cards(deck, 2)
    sorted = sort_cards(hole_cards)

    if hole_cards[0][1] == hole_cards[1][1]:
        prob = float(hole_strengths[str(sorted[1][0] + sorted[0][0] + 's')])
    else:
        prob = float(hole_strengths[str(sorted[1][0] + sorted[0][0] + 'o')])

    sample_hole_strengths.append(prob)


    
