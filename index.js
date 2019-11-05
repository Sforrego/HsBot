const Discord = require('discord.js');
const bot = new Discord.Client();
const PREFIX = "!";
var f = require('./functions.js');
const fs = require('fs');
const consts = require('./const.js');

const GoogleSpreadsheet = require('google-spreadsheet');
const { promisify } = require('util');
const creds = require('./client_secret.json');

async function accessSpreadsheet() {
  const doc = new GoogleSpreadsheet('1wWLt9pkC1doPSZyHmD_AewvUVupXcEtqqymcGSoHG6U');
  await promisify(doc.useServiceAccountAuth)(creds);
  const info = await promisify(doc.getInfo)();
  const sheet = info.worksheets[0];
  const rows = await promisify(sheet.getRows)({
    offset: 1
  });
  const cells = await promisify(sheet.getCells)({
    'min-row': 1,
    'max-row': 120,
    'min-col':1,
    'max-col':52,
  });
  // Transform google sheets to list of lists
  var row0 = [[]];
  for(i=1;i<52;i++){
    row0[0].push(cells[i].value);
  }
  var rowsn = [];
  for(i=0;i<rows.length;i++){
    rowsn.push([rows[i].rsn]);
    for(k=0;k<row0[0].length;k++){
      rowsn[i].push(rows[i][row0[0][k].toLowerCase()]);
    }
  }
  hs = row0.concat(rowsn);
  //console.log(hs);
  // creates dictionaries from the lists
  [players, players_index, players_low] = f.create_players(hs);
  [boss_kills, boss_index, boss_names,boss_names_low] = f.create_bosses(hs);
  boss_shorts = consts.boss_shorts;

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
          args[1] = args[1].toLowerCase();
          if((!Object.keys(boss_shorts).includes(args[1])) && (!Object.keys(boss_names_low).includes(args[1]))){
            msg.channel.send("That boss name doesn't match any existent boss.");
          }

          else{
            if (Object.keys(boss_shorts).includes(args[1])){
              boss_name = boss_shorts[args[1]]
            }
            else{
              boss_name = boss_names_low[args[1]]
            }
            copy_boss = [...boss_kills[boss_name]];
            copy_boss.sort(function (a, b) {
                return b[1]-a[1];
                });
            bstring = `${boss_name}\n`
            bstring = bstring.concat(`1. ${copy_boss[0][0]}: ${copy_boss[0][1]}\n`);
            bstring = bstring.concat(`2. ${copy_boss[1][0]}: ${copy_boss[1][1]}\n`);
            bstring = bstring.concat(`3. ${copy_boss[2][0]}: ${copy_boss[2][1]}\n`);
            msg.channel.send(bstring);
          }
        }
        break;
      case 'update':
        if(msg.member.hasPermission('KICK_MEMBERS')){
          args[2] = args[2].toLowerCase();
          if (!args.length==4){
            msg.channel.send("To update some you need to do !update rsn boss kc");
          }

          else{

            if((!Object.keys(boss_shorts).includes(args[2])) && (!Object.keys(boss_names_low).includes(args[2]))){
              msg.channel.send("That boss name doesn't match any existent boss.");
            }

            else{
              if (Object.keys(boss_shorts).includes(args[2])){
                boss_name = boss_shorts[args[2]]
              }
              else{
                boss_name = boss_names_low[args[2]]
              }
              if (Object.keys(players_low).includes(args[1])){
                rsn = players_low[args[1]]
              }
              else{
                rsn = args[1]
              }
              kc = args[3]
              while (!players.includes(rsn)) {
                f.create_player(boss_kills,players,rsn);
                }
              boss_kills = f.updatedict(boss_kills, players, players_index, rsn, boss_name, kc);
              msg.channel.send("Hs updated!");
              }}}

        else {
          msg.channel.send("You don't have enough permission to do this");
        }
        break;
      case 'save':
        msg.channel.send("Data saved.");
        f.update_sheet(boss_kills,boss_index,players,players_index,rows,sheet);
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
      case 'shorts':
       ans = '';
       for(key in boss_shorts){
         ans = ans.concat(`,${key}`);
       }
       ans = ans.slice(1,ans.length);
       msg.channel.send(ans);
      break;
      case 'help':
      msg1 = "I can't deal with spaces please remove them from rsn and boss names.\n Commands and examples:\n !hs\n Prints all the highscores (Admin only).\n\n "
      msg1 = msg1.concat("!hs KalphiteQueen\n Prints the highscores of a certain boss.\n\n !update IronRok KalphiteQueen 100\n ");
      msg1 = msg1.concat("Updates the information of a players kc in a specific boss (Admin only)\n\n !save\n Saves all the changes to the db.\n\n !clear n \n Clears the last n comments in the current cannel (Admin only)\n\n ");
      msg1 = msg1.concat("!shorts\n Prints all the possible abbreviations.");
      msg.channel.send(msg1);
      break;
    }
  })


  bot.login(token);

  process.on('SIGTERM', function () {
    console.log("Data saved.");
    f.update_sheet(boss_kills,boss_index,players,players_index,rows,sheet);
    process.exit(0);
  });

  process.on('SIGINT', function () {
      console.log("Data saved.");
      f.update_sheet(boss_kills,boss_index,players,players_index,rows,sheet);
      process.exit(0);
  });

  process.on('exit', function() {
    console.log("Data saved.\nByeBye.");
    f.update_sheet(boss_kills,boss_index,players,players_index,rows,sheet);
    process.exit(0);
  });
//bot.login(process.env.BOT_TOKEN);
}
accessSpreadsheet();

//BOT_TOKEN is the Client Secret
