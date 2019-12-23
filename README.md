## Future implementations:
  !hs vs bossname rsn1 rsn2 rsn3 rsn4 ....
  !hs hespori n (top n players)


## Commands
```bash
!hs
```
Prints every boss top 3 kcs, only doable by a high rank because it uses too much space on a channel.
```bash
!hs boss
```
Prints its top 3 kc.
```bash
!update player boss kc.
```
It updates the current kc of a player in a certain boss, if the player was not on the db
it creates an entry for that payer with 0 kc on every boss and then updates it accordingly.
```bash
!clear n
```
If no n is given default is 2, max n is 10.
```bash
!load
```
loads the bot with all current changes.


## How it works
 * All commands with permission are doable by Ranks that can kick players.
 * reads the db (local txt currently) and creates dictionaries.
   boss_kills = {"Kraken":[[IronRok,200],[CHProduct,250]], "Kree'Arra"...}
 * !hs boss
  Before replying with the boss top kc's it sorts each boss list by kc.
 * !hs
   Creates a very long message and just divides it by the boss that's ideally
  in the middle, in this case Kraken, then send both messages (because of the 2000 char limit).
