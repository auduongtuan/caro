import { cloneDeep, range } from "lodash";
export const COMP = +1;
export const HUMAN = -1;
export const BOARD_SIZE = 10;
// Large board size -> need to limit the depth
export const DEPTH_LIMIT = 3;
export const WIN_STREAK = 5;
export const TIME_LIMIT = 7000;
export type Player = typeof COMP | typeof HUMAN;
export type CellValue = Player | 0;
export type State = CellValue[][];
export type CellCoord = [number, number];
const b = BOARD_SIZE-WIN_STREAK+1;
export const winPaths: CellCoord[][] = getWinPaths();

const patterns = {
  '11111': 30000000,
  '22222': -30000000,
  '011110': 20000000,
  '022220': -20000000,
  '011112': 50000,
  '211110': 50000,
  '022221': -50000,
  '122220': -50000,
  '01110': 30000,
  '02220': -30000,
  '011010': 15000,
  '010110': 15000,
  '022020': -15000,
  '020220': -15000,
  '001112': 2000,
  '211100': 2000,
  '002221': -2000,
  '122200': -2000,
  '211010': 2000,
  '210110': 2000,
  '010112': 2000,
  '011012': 2000,
  '122020': -2000,
  '120220': -2000,
  '020221': -2000,
  '022021': -2000,
  '01100': 500,
  '00110': 500,
  '02200': -500,
  '00220': -500
}
function getWinPaths() {
  return range(BOARD_SIZE).reduce((acc, i) => {
    // x=b
    const xb = range(BOARD_SIZE).map(k => [i, k]);
    // y=b
    const yb = range(BOARD_SIZE).map(k => [k, i]);
    acc.push(xb); 
    acc.push(yb);
    return acc;
  },[])
  .concat(range(-b+1, b).reduce((acc, k) => {
        // y = x + k
        let yxk = range(BOARD_SIZE).reduce((yxkAcc, x) => {
          const y = x+k;
          if(y >= 0 && y < BOARD_SIZE) {
            yxkAcc.push([x, y]);
          }
          return yxkAcc;
        }, []);
        // y = BOARD_SIZE - 1 - x + k
        let y_sxk = range(BOARD_SIZE).reduce((y_sxkAcc, x) => {
          const y = BOARD_SIZE - 1 - x + k

          if(y >= 0 && y < BOARD_SIZE) {
            y_sxkAcc.push([x, y]);
          }
          return y_sxkAcc;
        }, []);
        acc.push(yxk);
        acc.push(y_sxk);
       return acc;
  }, []));
}

function generateCheckmate(player: Player):CellValue[][] {
  return range(1, WIN_STREAK+1).map(i =>
    [...Array(WIN_STREAK-i).fill(player), 0, ...Array(i-1).fill(player)]
  )
}

function generateHalfCheckmate(player: Player):CellValue[][] {
  return range(1, WIN_STREAK).map(i => {
      let template = [0, ...Array(WIN_STREAK-1).fill(player), 0]
      template[i] = 0
      return template;
    }
  )
}
function isValidSubsequence(array: number[], sequence: number[]) {
  // let index = -1;
  // for (const value of sequence) {
  //   index = array.indexOf(value, index + 1); // find the next sequence value
  //   if (index === -1) {
  //     return false; // not found, return false immediately
  //   }
  // }
  return array.join(',').includes(sequence.join(','));
  // return true;
}
export function gameOver(state: State) {
  return wins(state, HUMAN) || wins(state, COMP);
} 
export function wins(state: State, player: Player) {
  return getWinCases(state).some(winCase => 
    isValidSubsequence(winCase, Array(WIN_STREAK).fill(player))
  );
}
export function getWinCases(state: State): CellValue[][] {
  return winPaths.map(winPath => winPath.map((cell: CellCoord) => state[cell[0]][cell[1]]));
}
export function isSameMove(move1: CellCoord, move2: CellCoord) {
  return move1[0] == move2[0] && move1[1] == move2[1];
}
export function emptyCells(state: State) {
  return state.reduce<CellCoord[]>((acc, row, x) => {
    row.forEach((cell, y) => {
      if(cell == 0) acc.push([x, y]);
    });
    return acc;
  }, []);
}
let human_checkmate_list = generateCheckmate(HUMAN)
let comp_checkmate_list = generateCheckmate(COMP)
let human_half_checkmate_list = generateHalfCheckmate(HUMAN)
let comp_half_checkmate_list = generateHalfCheckmate(COMP)
export function calculateCheckmateScore(state: State, player: Player) {
  return getWinCases(state).reduce((point, path) => {
    if(player == HUMAN) {
      const checkMatePoint = human_checkmate_list.reduce((acc, checkmate) => {
        if (isValidSubsequence(path, checkmate)) {
          acc = acc + 1;
        }
        return acc;
      }, 0);
      const halfCheckmatePoint = human_half_checkmate_list.reduce((acc, half_checkmate) => {        
        if (isValidSubsequence(path, half_checkmate)) {
          acc = acc + 1;
        }
        return acc;
      }, 0);
      point += checkMatePoint*300 + halfCheckmatePoint*200;
      return point;
    }
    else {
      const checkMatePoint = comp_checkmate_list.reduce((acc, checkmate) => {
        if (isValidSubsequence(path, checkmate)) {
          acc += 1;
        }
        return acc;
      }, 0);
      const halfCheckmatePoint = comp_half_checkmate_list.reduce((acc, half_checkmate) => {
        if (isValidSubsequence(path, half_checkmate)) {
          acc += 1;
        }
        return acc;
      }, 0);
      point += checkMatePoint*300 + halfCheckmatePoint*200;
      return point;
    }
  }, 0);
}
// https://github.com/Mgla96/GomokuAI/blob/master/gobang.py
export function heuristic(state: State, previous_move: CellCoord) {
    // let c_win_point = 0;
    // let h_win_point = 0;
    let point = 0;

    let previous_state = cloneDeep(state);
    previous_state[previous_move[0]][previous_move[1]] = 0;

    getWinCases(state).forEach(path => {
      Object.keys(patterns).forEach((pattern) => {
        const patt = pattern.split('').map(cell => cell == '2' ? -1 : parseInt(cell));
        // console.log(patt);
        // console.log(path);
        // console.log(isValidSubsequence(patt, path));
        
        if(isValidSubsequence(patt, path)) {
          point += patterns[pattern];
        }
      });
    });
    console.log(point);
    return point;
    // // 1. neu co ben win => tra ve ket qua lien
    // if (wins(state, COMP)) {
    //   c_win_point += 1000;
    //   return c_win_point - h_win_point;
    // }
    // if (wins(state, HUMAN)) {
    //   h_win_point += 1000
    //   return c_win_point - h_win_point
    // }
    // // 2. tim cac checkmate
    // // previous state: curent state remove previous move
    // let previous_state = cloneDeep(state);
    // previous_state[previous_move[0]][previous_move[1]] = 0;

    // const currentHumanPoint = calculateCheckmateScore(state, HUMAN);
    // const prevHumanPoint = calculateCheckmateScore(previous_state, HUMAN);
    // const currentCompPoint = calculateCheckmateScore(state, COMP);
    // const prevCompPoint = calculateCheckmateScore(previous_state, COMP);
    // if(currentHumanPoint < prevHumanPoint) {
    //   c_win_point += prevHumanPoint - currentCompPoint;
    // } else {
    //   h_win_point += currentHumanPoint - prevHumanPoint
    // }
    // if(currentCompPoint < prevCompPoint) {
    //   h_win_point += prevCompPoint - currentCompPoint;
    // } else {
    //   c_win_point += currentCompPoint - prevCompPoint
    // }
    // // con lai, dem so nuoc lien ke trong win path
    // for path in current_win_cases:
    //     count_c = count_consecutive_duplicates(COMP, path)
    //     c_next_opponent = count_c[1]
    //     c_prev_opponent = count_c[1]-count_c[0]-1
    //     count_h = count_consecutive_duplicates(HUMAN, path)
    //     h_next_opponent = count_h[1]
    //     h_prev_opponent = count_h[1]-count_h[0]-1

    //     if (HUMAN not in path):
    //         c_win_point += count_c[0]*2
    //         // neu comp chua co thi uu tien phan o giua ban va gan human
    //     else:
    //         // neu doi thu nam sat ben => cong them diem doi thu de chan truoc
    //         if (c_next_opponent < len(path) and path[c_next_opponent] == HUMAN) or (c_prev_opponent > -1 and path[c_prev_opponent] == HUMAN):
    //             c_win_point += count_c[0]*1 + count_h[0]*1
    //         else:
    //             c_win_point += count_c[0]*2

    //     if (COMP not in path):
    //         h_win_point += count_h[0]*2
    //         // neu comp chua co thi uu tien phan o giua ban va gan human
    //     else:
    //         if (h_next_opponent < len(path) and path[h_next_opponent] == COMP) or (h_prev_opponent > -1 and path[h_prev_opponent] == COMP):
    //             h_win_point += count_h[0]*1 + count_c[0]*1
    //         else:
    //             h_win_point += count_h[0]*2

    // // none edge priority - uu tien di o trong hon la o canh
    // if previous_move[0] != 0 and previous_move[0] != 1 and previous_move[0] != BOARD_SIZE - 1 and previous_move[0] != BOARD_SIZE - 2:
    //     if previous_move[1] != 0 and previous_move[1] != 1 and previous_move[1] != BOARD_SIZE - 1 and previous_move[1] != BOARD_SIZE - 2:
    //         c_win_point += 2

    // return c_win_point - h_win_point;
}