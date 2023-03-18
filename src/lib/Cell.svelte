<script lang="ts">
  export let value: number;
  const SYMBOLS = {
    "-1": "X",
    "1": "O"
  }
</script>
<button on:click>
  {value != 0 && value in SYMBOLS ? SYMBOLS[value] : '_'}
</button>