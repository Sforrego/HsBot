var fs = require("fs");
var csv = require('fast-csv');
const { promisify } = require('util');

exports.create_bosses = function(hs){
  var boss_index = {};
  var boss_names = [];
  var boss_names_low = {};
  for(i in hs[0]){
    boss_index[hs[0][i]] = i;
    boss_names.push(hs[0][i]);
    boss_names_low[hs[0][i].toLowerCase()] = hs[0][i];
  }
   return [boss_index,boss_names, boss_names_low];
};


exports.get_bosses = function(rows, boss_names){
  var boss_kills = {};
  for(i in boss_names){
    boss_kills[boss_names[i]] = [];

    for(k in rows){
      if (rows[k].rsn=='@'){
        break;
      }
      boss_kills[boss_names[i]].push([rows[k].rsn,rows[k][boss_names[i].toLowerCase()]]);
   }
}
 return boss_kills;
}


exports.create_players=function(hs){
  var players = [];
  var players_index = {};
  var players_low = {};
  for(var i=1;i<hs.length;i++){
    if (hs[i][0]=='@'){
      break;
    }
    players.push(`${hs[i][0]}`);
    players_low[hs[i][0].toLowerCase()] = hs[i][0];
    players_index[hs[i][0]]=i-1;}
  return [players,players_index, players_low];
};

exports.csv_to_lists=function(db_path){
  var info = fs.readFileSync(db_path,'utf8');
  var hs = info.split('\n'); // list of lines
  var hs_matrix = [];                //list of lists, matrix of the data
    for(r=0;r<hs.length;r++){
      hs_matrix.push(hs[r].split(","));
   }
   return hs_matrix;
};

exports.updatedict=function(boss_kills, players, players_index, rsn, boss, kills){
    if(Object.keys(boss_kills).includes(boss)){
      boss_kills[boss][players_index[rsn]][1] = kills;
    }
  return boss_kills;
};

exports.update_rows=async function(players_index, rsn, boss, kills, rows){
    rows[players_index[rsn]][boss] = kills;
    await rows[players_index[rsn]].save();

}

exports.create_player=async function(boss_names,players,players_index,rsn,rows){
  //console.log(boss_names);
  players.push(rsn);
  players_index[rsn] = players.length-1;
  rows[[players_index[rsn]]].rsn = rsn;
  for(var boss in boss_names){
    rows[[players_index[rsn]]][boss_names[boss]] = 0;
  }
  await rows[[players_index[rsn]]].save();
};

exports.get_rows=async function(sheet,rows){
  rows = await promisify(sheet.getRows)({
      offset: 1
    });
  return rows;
}


function asyncAddRow(row) {
  return new Promise((res, rej) => {
    sheet.addRow(row, (err) => {
      if (err) rej(err);
      else res(true);
    });
  })
}



update_sheet=async function(boss_kills,boss_index,players,players_index,rows,sheet){
  for(var i = 0; i < players.length;i++){
    if (i >= rows.length){
      newdict = {Rsn:`${players[i]}`};
      for(var key in boss_kills){
        newdict[key] = boss_kills[key][i][1];
      }
      //console.log(`adding a new row for ${players[i]}`);
      await sheet.AddRow(newdict);
    }
    else {
    for(var key in boss_kills){
      rows[i][key] = boss_kills[key][i][1]
      rows[i].save()
    }
  }}
};
