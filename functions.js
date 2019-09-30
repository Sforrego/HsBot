var fs = require("fs");
var csv = require('fast-csv');

exports.create_bosses = function(hs){
  var boss_kills = {};
  var boss_index = {};
  var boss_names = [];
  for(i=1;i<hs[0].length;i++){
    boss_kills[hs[0][i]] = [];
    boss_index[hs[0][i]] = i;
    boss_names.push(hs[0][i]);
    for(k=1;k<hs.length-1;k++){
      boss_kills[hs[0][i]].push([hs[k][0],hs[k][i]]);
   }}
   return [boss_kills,boss_index,boss_names];
};

exports.create_players=function(hs){
  var players = [];
  var players_index = {};
  for(var i=1;i<hs.length-1;i++){
    players.push(`${hs[i][0]}`);
    players_index[hs[i][0]]=i;}
  return [players,players_index];
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

exports.create_player=function(boss_kills,players,rsn){
  players.push(rsn);
  players_index[rsn] = players.length-1;
  for(var key in boss_kills){
    boss_kills[key].push([rsn,0]);
  }
};

exports.write_file=function(boss_kills,boss_index,players,players_index,db_file){
  data = 'Rsn';
  for(var i = 0; i<boss_names.length;i++){
    data = data.concat(`,${boss_names[i]}`);
    }
  data = data.concat('\n');
  for(var i = 0; i<players.length;i++){
    data = data.concat(`${players[i]}`);
    for(var key in boss_kills){
      data = data.concat(`,${boss_kills[key][i][1]}`);
    }
    data = data.concat(`\n`);
  }
  fs.writeFileSync(db_file,data,'utf8');
};
