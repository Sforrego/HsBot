This is a tracker bot for Oldschool Runescape, it connects Discord with SQL databases that are updated with data obtained from https://secure.runescape.com/m=hiscore_oldschool/a=13/overall. It's main purpose is to help tracking members stats within a community, this allows competitions to be automated and friendly competition between it's players, it's secondary purpose is to help organize a discord community, managing and tracking members and their roles.

It is no longer working since our friends at https://wiseoldman.net have done an excellent job in achieving the same goal as this bot, and any further work done here could be done helping them. The other reason is that everytime Jagex, the company running Oldschool Runescape, updates the game with a new boss or skill, all the stats move (because their API is pretty bad) and the bot stops being accurate, this implies continous updates to keep the bot working properly are needed.

### How it started

In a group of over 100  players, with players continously joining and leaving (currently 180, over 500 players have been in and out between 2019-2021), changing their names, and progressing their accounts, a need for automated organization appeared. The community was formed within the game, but also outside the game using a Discord server. To track the players a google spreadsheet was used, and so the first version of the bot (wrote in Node js) wrote directly to that spreadsheet to help track the players in a simple way.

### How it Works

First a discord bot is created, the first version was written using Node js, but the time past and for a more efficient way of adapting the bot it was rewritten in Python. This discord bot is then hosted in a Heroku server for free. Now that it is being hosted you add the bot to your server by giving it certain permissions. So it could write to the google spreadsheets it also needed the spreadsheet owners permissions. When new needs of tracking emerged, the only way to continue was to create an SQL database stored in heroku to rapidly track and update stats.

Finally a simple command in the discord server, makes a request to the SQL database which is then translated in readable language and sent back to the discord.



![HsTopTotal](https://user-images.githubusercontent.com/26422390/125109717-b4acf880-e0b1-11eb-9686-782be907e7c4.png)



### Commands
<pre>
Replace spaces with _ in names.

Hiscores:
  add              Adds players to the clan's hiscores. 
                   !hs add player1 player2 ...
  change2          Changes the name in the clan's hiscores.
                   !hs change2 old_name new_name
  check            Checks if a player is in the clan's hs. 
                   !hs check player
  fullupdate       Updates every player in the clan's hiscores. 
                   !hs fullupdate
  my               Gets the person using the command lvl/kc in a stat. 
                   !hs my stat
  rank             Shows the rank within the clan of a member in a specific stat. 
                   !hs rank stat player
  ranks            Shows the ranks within the clan of all the stats related to skills or bosses of a player. 
                   !hs ranks skills/bosses player
  rm               Removes names from the clan's hiscores. 
                   !hs rm player1 player2 ...
  rmoutdated       Removes outdated names from the clan's hiscores. 
                   !hs rmoutdated
  top              Shows the top 5 players and their kc/lvl+xp for a specific stat. 
                   !hs top stat
  top10            Shows the top 10 players and their kc/lvl+xp for a specific stat.
                   !hs top10 stat
  update           Updates a players stats in the clan's hiscores. 
                   !hs update player1 player2 ...

Tracker:
  addtotracker     Adds players to the clan tracker. 
                   !hs addtotracker player1 player2 ...
  checktracker     Checks a players progress according to the clan tracker. 
                   !hs checktracker player stat
  mytracker        Check's xp/kills gained since being tracked with the personal tracker. 
                   !hs mytracker stat
  playerstracked   Checks which players are being tracked by the clan tracker. 
                   !hs playerstracked
  resetclantracker Removes everyone from the clantracker.
                   !hs resetclantracker
  resetmytracker   Resets a player's personal tracker.
                   !hs resetmytracker
  startmytracker   Starts a player's personal tracker. 
                   !hs startmytracker
  toptracker       Checks the top 5 progress according to the clan tracker in a stat.
                   !hs toptracker stat
  toptracker10     Checks the top 10 progress according to the clan tracker in a stat.
                   !hs toptracker10 stat
  trackercommands  Shows all the tracker related commands
                   !hs trackercommands
  updatetracker    Updates all players in the tracker.
                   !hs updatetracker
  
Bingo:
  addteam          Add a team of players.
                   !hs addteam team_number player1 player2 ...
  bingocommands    Shows all the bingo related commands
                   !hs bingocommands
  checkallteams    Checks xp/kc gained by all teams in a skill/boss.
                   !hs checkallteams
  checkdone        Checks tiles done by a team.
                   !hs checkdone team_number
  checkleft        Checks tiles that have not been done by a team.
                   !hs checkleft team_number
  checkteam        Checks xp/kc gained by a team in a skill/boss.
                   !hs checkteam team_number stat
  complete         Completes a Tile.
                   !hs complete team_number tile_name
  getteam          Returns the players of a specific team.
                   !hs getteam team_number
  modifyteam       Updates a specific player of a team. 
                   !hs modifyteam <team_number> <player_number> <player>
  resetteams       Removes all teams.
                   !hs resetteams
  undo             Undo a Tile.
                   !hs undo team_number tile_name
  updateteam       updates a bingo team on the hiscores.
                   !hs updateteam team_number
  
Management
  change           Changes a players rsn in the spreadsheets (Admin).
                   !hs change old_name new_name
  clan_ranks       Return all players with a specific rank (Admin).
                   !hs clan_ranks rank
  due              Return all players due rank in the spreadsheets (Admin).
                   !hs due rank
  help             Shows all the commands.
                   !hs help
  joindate         Shows a player and their join date.
                   !hs joindate player
  myjoindate       Shows your join date.
                   !hs myjoindate
  remove           Removes players from the cc (sheets) (Admin).
                   !hs remove player1 player2 ...
  shorts           Gets all the short ways of calling each stat
                   !hs shorts
  superadd         Changes a players discord nick, gives him role, and adds it to the membership list (Admin).
                   !hs superadd discord_name runescape_name
</pre>
