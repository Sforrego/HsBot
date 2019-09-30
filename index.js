const Discord = require('discord.js');
const bot = new Discord.Client();
const token = 'NjI3NDAzMzAzMzY1Mzc4MDQ4.XZGqqw.59OmaOOuDLhNORG4b3vNEbaTAL4';
const PREFIX = "!";
var db_path = 'hiscores.txt';
var f = require('./functions.js');

hs = f.csv_to_lists(db_path);
[players, players_index] = f.create_players(hs);
[boss_kills, boss_index, boss_names] = f.create_bosses(hs);


bot.on('ready', ()=> {
  console.log("This bot is online!");
});

bot.on('message', msg=>{
  let args = msg.content.substring(PREFIX.length).split(" ");
  switch(args[0]){
    case 'hs':
      //sort the boss lists into new lists to get the first x players

      if (!args[1]){
        str1 = ''
        for(var k = 0; k < boss_names.length;k++){
          key = boss_names[k];
          copy_boss = [...boss_kills[key]];
          copy_boss.sort(function (a, b) {
              return b[1]-a[1];
              });
          str1 = str1.concat(`\n${key}\n`)
          str1 = str1.concat(`1. ${copy_boss[0][0]}: ${copy_boss[0][1]}\n`);
          str1 = str1.concat(`2. ${copy_boss[1][0]}: ${copy_boss[1][1]}\n`);
          str1 = str1.concat(`3. ${copy_boss[2][0]}: ${copy_boss[2][1]}\n`);

        }
        index = str1.indexOf("Kraken");
        str2 = str1.slice(0,index);
        str3 = str1.slice(index,str1.length);
        msg.channel.send(str2);
        msg.channel.send(str3);
      }
      else{
        if(!boss_names.includes(args[1])){
          msg.channel.send("That boss name doesn't match any existent boss.");
        }
        else{
          copy_boss = [...boss_kills[args[1]]];
          copy_boss.sort(function (a, b) {
              return b[1]-a[1];
              });
          bstring = `${args[1]}\n`
          bstring = bstring.concat(`1. ${copy_boss[0][0]}: ${copy_boss[0][1]}\n`);
          bstring = bstring.concat(`2. ${copy_boss[1][0]}: ${copy_boss[1][1]}\n`);
          bstring = bstring.concat(`3. ${copy_boss[2][0]}: ${copy_boss[2][1]}\n`);
          msg.channel.send(bstring);
        }
      }
      break;
    case 'update':
      if(msg.member.hasPermission('KICK_MEMBERS')){


        if (!args.length==4){
          msg.channel.send("To update some you need to do !update rsn boss kc");
        }
        else{
          rsn = args[1]
          boss = args[2]
          kc = args[3]
          if(!boss_names.includes(boss)){
            msg.channel.send("That boss name doesn't match any existent boss.");
          }
          else{
            while (!players.includes(rsn)) {
              f.create_player(boss_kills,players,rsn);
              }
            boss_kills = f.updatedict(boss_kills, players, players_index, args[1], args[2], args[3]);
            msg.channel.send("Hs updated!");
            }}}

      else {
        msg.channel.send("You don't have enough permission to do this");
      }
      break;
    case 'help':
      msg1 = 'Examples:\n !hs (Admin only)\n !hs KalphiteQueen\n !update IronRok KalphiteQueen 100 (Admin only)\n!save\n!clear n (Admin only)';
      msg.channel.send(msg1);
      break;
    case 'save':
      msg.channel.send("Data saved.");
      f.write_file(boss_kills,boss_index,players,players_index,db_path);
      break;
    case 'clear':
      if(msg.member.hasPermission('KICK_MEMBERS')){
        if(!args[1]){
          msg.channel.bulkDelete(2);
        }
        else {
          if(args[1]<=10){
            msg.channel.bulkDelete(10);
          }
          else{
            msg.channel.send("You can't delete more than 10 messages at a time.");
          }
        }
      }
      else {
        msg.channel.send("You don't have enough permission to do this");
      }
    break;
  }
})


bot.login(token);

process.on('SIGTERM', function () {
  console.log("Data saved.");
  f.write_file(boss_kills,boss_index,players,players_index, db_path);
  process.exit(0);
});

process.on('SIGINT', function () {
    console.log("Data saved.");
    f.write_file(boss_kills,boss_index,players,players_index, db_path);
    process.exit(0);
});
