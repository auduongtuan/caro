<script lang="ts">
  import Cell from "./Cell.svelte";
  const COMP = +1;
  const HUMAN = -1;
  const BOARD_SIZE = 10
  // Large board size -> need to limit the depth
  const DEPTH_LIMIT = 3
  const WIN_STREAK = 5
  const TIME_LIMIT = 2.0
  let currentTurn: number;
  // let count: number = 0
  // const increment = () => {
    //   count += 1
    // }
  type Player = typeof COMP | typeof HUMAN;
  type GameState = number[][];
  type Move = [number, number];
  let board: GameState = Array(10).fill(null).map(()=>Array(10).fill(0))

  function isSameMove(move1: Move, move2: Move) {
    return move1[0] == move2[0] && move1[1] == move2[1];
  }
  function emptyCells(state: GameState) {
    return state.reduce<Move[]>((acc, row, x) => {
      row.forEach((cell, y) => {
        if(cell == 0) acc.push([x, y]);
      });
      return acc;
    }, []);
  }
  function validMove(move: Move) {
    // console.log(emptyCells(board));
    return emptyCells(board).find(emptyCell => isSameMove(emptyCell, move)) ? true : false;
  }
  function setMove(move: Move, player: Player) {
    console.log(`Moved ${move[0]}, ${move[1]}`);
    board[move[0]][move[1]] = player;
  }
  function aiTurn() {
    const validMoves = emptyCells(board);
    const randomMove = validMoves[Math.floor(Math.random() * validMoves.length)];
    setMove(randomMove, COMP);
  }
  function humanTurn(move: Move) {
    if(validMove(move)) {
      setMove(move, HUMAN);
      aiTurn();
    }
    else {
      alert('Not a valid move');
    }
  }
</script>

<div>
{#each board as row, x}
  <div class="flex gap-4">
  {#each row as cell, y}
    <Cell on:click={() => humanTurn([x,y])} value={cell}></Cell>
  {/each}
  </div>
{/each}

</div>
