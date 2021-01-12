import eval7
import itertools
import pandas as pd
from cards import monte_carlo_prob
import time

if __name__ == '__main__':
    start = time.time()
    _MONTE_CARLO_ITERS = 5000
    _RANKS = 'AKQJT98765432' 

    off_rank_holes = list(itertools.combinations(_RANKS, 2)) #all holes we can have EXCEPT pocket pairs (e.g. [(A, K), (A, Q), (A, J)...])
    pocket_pair_holes = list(zip(_RANKS, _RANKS)) #all pocket pairs [(A, A), (K, K), (Q, Q)...]

    suited_strengths = [monte_carlo_prob([hole[0] + 'c', hole[1] + 'c'], [], [], _MONTE_CARLO_ITERS) 
        for hole in off_rank_holes] #all holes with the same suit
    off_suit_strengths = [monte_carlo_prob([hole[0] + 'c', hole[1] + 'd'], [], [], _MONTE_CARLO_ITERS) 
        for hole in off_rank_holes] #all holes with off suits
    pocket_pair_strengths = [monte_carlo_prob([hole[0] + 'c', hole[1] + 'd'], [], [], _MONTE_CARLO_ITERS) 
        for hole in pocket_pair_holes] #pocket pairs must be off suit

    suited_holes = [hole[0] + hole[1] + 's' for hole in off_rank_holes] #s == suited
    off_suited_holes = [hole[0] + hole[1] + 'o' for hole in off_rank_holes] #o == off-suit
    pocket_pairs = [hole[0] + hole[1] + 'o' for hole in pocket_pair_holes] #pocket pairs are always off suit

    all_strengths = suited_strengths + off_suit_strengths + pocket_pair_strengths #aggregate them all
    all_holes = suited_holes + off_suited_holes + pocket_pairs

    hole_df = pd.DataFrame() #make our spreadsheet with a pandas data frame!
    hole_df['Holes'] = all_holes
    hole_df['Strengths'] = all_strengths

    hole_df.to_csv('hole_strengths.csv', index=False) #save it for later use, trade space for time!
    end = time.time()
    print(f"{end-start}")