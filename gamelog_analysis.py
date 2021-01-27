def desirable(line, board):
    # return ('Round' in line) or (('B' in line) and ('board 1') in line)
    return ('shows' in line) and ('B' in line) and (('board ' + str(board)) in line)

open('board1','w').writelines(line for line in open('../engine-2021/gamelog.txt') if desirable(line, 1))
open('board2','w').writelines(line for line in open('../engine-2021/gamelog.txt') if desirable(line, 2))
open('board3','w').writelines(line for line in open('../engine-2021/gamelog.txt') if desirable(line, 3))    