<script lang="ts">
  export let value: number;
  export let disabled: boolean;
  const SYMBOLS = {
    "-1": "X",
    "1": "O"
  }
</script>
<button on:click disabled={disabled}>
  {value != 0 && value in SYMBOLS ? SYMBOLS[value] : '_'}
</button>