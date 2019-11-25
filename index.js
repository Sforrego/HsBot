const Discord = require('discord.js');
const bot = new Discord.Client();
const PREFIX = "!";
var f = require('./functions.js');
const fs = require('fs');
const consts = require('./const.js');
//to run from heroku delete token, change bot.login and enable worker in heroku.
//const token = "";
const GoogleSpreadsheet = require('google-spreadsheet');
const { promisify } = require('util');
const creds = require('./client_secret.json');
// to do: change name feature, add herbiboar.
async function accessSpreadsheet() {
  const doc = new GoogleSpreadsheet('1wWLt9pkC1doPSZyHmD_AewvUVupXcEtqqymcGSoHG6U');
  await promisify(doc.useServiceAccountAuth)(creds);
  const info = await promisify(doc.getInfo)();
  const sheet = info.worksheets[0];
  var rows = await promisify(sheet.getRows)({
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
  // creates dictionaries from the lists
  [players, players_index, players_low] = f.create_players(hs);
  [boss_index, boss_names,boss_names_low] = f.create_bosses(hs);
  boss_shorts = consts.boss_shorts;

  bot.on('ready', ()=> {
    console.log("This bot is online!");
  });

  bot.on('message', msg=>{
    // IT IS NOT ! FIRST LETTER, ITS ANYTHING
    let args = msg.content.substring(PREFIX.length).split(" ");
    switch(args[0]){
      case 'hs':
      // msg.channel.bulkDelete(1);
      boss_kills = f.get_bosses(rows,boss_names);
      //console.log(boss_kills);
        if (!args[1]){
          strings_dict = {};
          for(var boss in boss_names){
            copy_boss = [...boss_kills[boss_names[boss]]];
            copy_boss.sort(function (a, b) {
                return b[1]-a[1];
                });
            str1 = ''
            str1 = str1.concat(`\n${boss_names[boss]}\n`)
            str1 = str1.concat(`1. ${copy_boss[0][0]}: ${copy_boss[0][1]}\n`);
            str1 = str1.concat(`2. ${copy_boss[1][0]}: ${copy_boss[1][1]}\n`);
            str1 = str1.concat(`3. ${copy_boss[2][0]}: ${copy_boss[2][1]}\n`);
            strings_dict[boss] = str1;
          }

          strings_list = ['']
          k = 0
          Object.keys(strings_dict).forEach(function(key) {
              if (strings_list[k].concat(strings_dict[key]).length >= 2000){
                k += 1;
                strings_list.push('');
              }
              strings_list[k] = strings_list[k].concat(strings_dict[key]);
          });
          //console.log(strings_dict);
          for (index in strings_list){
            msg.channel.send(strings_list[index]);
          }
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
            msg.channel.send("To update you need to do !update rsn boss kc");
            // setTimeout(donothing, 5000);
            // msg.channel.bulkDelete(2);
          }

          else{

            if((!Object.keys(boss_shorts).includes(args[2])) && (!Object.keys(boss_names_low).includes(args[2]))){
              msg.channel.send("That boss name doesn't match any existent boss.");
              // setTimeout(donothing, 5000);
              // msg.channel.bulkDelete(2);
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
              if (!players.includes(rsn)) {
                f.create_player(boss_names,players,players_index,rsn,rows);
                }
              //boss_kills = f.updatedict(boss_kills, players, players_index, rsn, boss_name, kc);
              f.update_rows(players_index,rsn,boss_name,kc,rows)
              msg.channel.send("Hs updated!");
              // setTimeout(donothing, 2000);
              // msg.channel.bulkDelete(2);
              }}}

        else {
          msg.channel.send("You don't have enough permission to do this");
          // setTimeout(donothing, 5000);
          // msg.channel.bulkDelete(2);
        }
        break;
      // case 'save':
      //   update_sheet(boss_kills,boss_index,players,players_index,rows,sheet);
      //   msg.channel.send("Data saved.");
      //   break;
      case 'HsClear':
        if(msg.member.hasPermission('KICK_MEMBERS')){
          if(!args[1]){
            msg.channel.bulkDelete(2);
          }
          else {
            if(args[1]<=10){
              msg.channel.bulkDelete(10);
            }
            if(args[1]==50){
              msg.channel.bulkDelete(50);
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
      case 'HsCommands':
        msg1 = "I can't deal with spaces please replace them with _.\n Commands and examples:\n !hs\n Prints all the highscores (Admin only).\n\n "
        msg1 = msg1.concat("!hs KalphiteQueen\n Prints the highscores of a certain boss.\n\n !update IronRok KalphiteQueen 100\n ");
        msg1 = msg1.concat("Updates the information of a players kc in a specific boss (Admin only)\n\n !save\n Saves all the changes to the db.\n\n !clear n \n Clears the last n comments in the current cannel (Admin only)\n\n ");
        msg1 = msg1.concat("!shorts\n Prints all the possible abbreviations.\n\n");
        msg1 = msg1.concat("!load\n Use this after making changes in the spreadsheet manually so the changes are incorporated.");
        msg.channel.send(msg1);
      break;
      case 'load':
        nrows = f.get_rows(sheet,rows);
        nrows.then(function(value) {
          rows = value;})
        msg1 = 'Newest version of sheets loaded.';
        msg.channel.send(msg1);
        // setTimeout(donothing, 2000);
        // msg.channel.bulkDelete(2);
      break;
    }
  })


  bot.login(process.env.BOT_TOKEN);//token);//

};

function donothing() {
    // all the stuff you want to happen after that pause
    //console.log('Blah blah blah blah extra-blah');
};

accessSpreadsheet();

//BOT_TOKEN is the Client Secret
