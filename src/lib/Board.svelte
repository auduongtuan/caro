<script lang="ts">
  import Cell from "./Cell.svelte";
  import {range, cloneDeep} from "lodash";
  console.log('re-render');
  import {COMP, HUMAN, BOARD_SIZE, DEPTH_LIMIT, WIN_STREAK, TIME_LIMIT} from './game';
  import type {Player, CellValue, State, CellCoord} from './game';
  import {calculateCheckmateScore, winPaths, wins, gameOver, getWinCases, isSameMove, emptyCells, heuristic} from './game';
  /* State */
  let isGameOver = false;
  let startTime = Date.now();
  let lastMove: CellCoord;
  let aiThinking = false;
  // let count: number = 0
  // const increment = () => {
    //   count += 1
    // }
  
  let board: State = range(BOARD_SIZE).map(()=>Array(10).fill(0))
 
  function validMove(move: CellCoord) {
    // console.log(emptyCells(board));
    return emptyCells(board).find(emptyCell => isSameMove(emptyCell, move)) ? true : false;
  }
  function setMove(move: CellCoord, player: Player) {
    console.log(`Moved ${move[0]}, ${move[1]}`);
    lastMove = move;
    board[move[0]][move[1]] = player;
  }

  async function aiTurn() {
    const validMoves = emptyCells(board);
    const depth = validMoves.length;
    startTime = Date.now();
    if(depth == BOARD_SIZE) {
      const randomMove = validMoves[Math.floor(Math.random() * validMoves.length)];
      setMove(randomMove, COMP);
    } else {
      aiThinking = true;
      (new Promise((resolve, reject) => {
        setTimeout(() => {
          const move = minimax(cloneDeep(board), depth, -Infinity, Infinity, COMP, lastMove);     
          resolve(move);
        }, 100);
      })).then(move => {
        console.log(move);
        setMove([move[0], move[1]], COMP);
        aiThinking = false;
        if(gameOver(board)) {
          isGameOver = true;
        }
      });

    }
    
   
  }
  function humanTurn(move: CellCoord) {
    if(validMove(move)) {
      setMove(move, HUMAN);
      console.log(board);
      console.log(calculateCheckmateScore(board, HUMAN));
      if(!gameOver(board)) {
        aiTurn();
      }
      else {
        isGameOver = true;
      }
    }
    else {
      alert('Not a valid move');
    }
  }

  function minimax(state: State, depth: number, alpha, beta, player: Player, previousMove?: CellCoord): [number, number, number] {
    let best: [number, number, number] = (player == COMP) ? [-1, -1, -Infinity] : [-1, -1, +Infinity];
    
    let currentDepth = emptyCells(board).length;
    if (depth == 0 || gameOver(state) || depth < currentDepth - DEPTH_LIMIT || Date.now() - startTime > TIME_LIMIT) {
      let score: number = heuristic(state, previousMove);
      console.log(score);
      return [-1, -1, score];
    }
    for(const cell of emptyCells(state)) {
       // toa do cua cai move toi
        const [x, y] = cell;
       // dien vao o trong de tao ra state
        state[x][y] = player;
       // ghi nho nuoc di vua roi
       // danh gia trang thai khi di
        let score: [number, number, number] = minimax(state, depth - 1, alpha, beta, -player as Player, cell);
        // reset lai trang thai
        state[x][y] = 0;
        score[0] = x;
        score[1] = y;
 
        if (player == COMP) {
            if (score[2] > best[2]) best = score; // max value
            alpha = Math.max(alpha, score[2]);
            if (beta <= alpha) 
                break;
        }
        else {
            if (score[2] < best[2])
                best = score;  // min value
            beta = Math.min(beta, score[2]);
            if (beta <= alpha)
                break;
        }
    }
    return best;
  }
  // console.log(calculateCheckmateScore(test_board as State, HUMAN));

</script>

<div class="font-['Jetbrains_Mono']">

<div class="h-[24px]">
{#if isGameOver}
Trò chơi kết thúc!!
{/if}

{#if aiThinking}
Chờ xíu nha bà ơi!
{/if}

</div>
{#each board as row, x}
  <div class="flex gap-4">
  {#each row as cell, y}
    <Cell on:click={() => humanTurn([x,y])} value={cell} disabled={isGameOver}></Cell>
  {/each}
  </div>
{/each}

</div>
