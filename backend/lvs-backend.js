var express = require('express');
var app = express();
var port = process.env.PORT || 8088;
var fs = require('fs');
var parse = require('csv-parse');
var request = require('request');
var responses="";
var p=[];
// start the server
app.listen(port);
console.log('Server started! At http://localhost:' + port);

app.post('/create_stream', function(req, res) {
  var id = req.param('id');
  var playurl = req.param('playurl');  
  var nocheck = req.headers['no-check']
  var pwd = req.headers['pwd']
  var inputFile='../config/realserver-backup-list.csv';
  console.log("processing realserver list file");
  var dict=[];
  var cntr = 0;
  var final_stat = 1;
  var parser = parse({from:'2'}, function (err, data) {
     var data_len = data.length;
     //console.log(data_len);
     data.forEach(function(line) {
      var realserver =line[0];
      var headers = {
    	'no-check': nocheck,
    	'pwd':  pwd
      }
      var options = {
        url: 'http://'+realserver+':8088/create_stream',
        method: 'POST',
        headers: headers,
        qs: {'id': id, 'playurl': playurl}
	}
        request(options, function (error, response, body) {
		dict[cntr]={
    		server:  line[0],
        	message: response.body,
                stat:  response.statusCode
		};
                if (response.statusCode !=  200) {
                   final_stat = 0;
                }
                cntr += 1;
		//console.log(cntr);
		//console.log(dict);
                if (cntr == data_len) {
                   if (final_stat == 1) {
                     console.log('Success \n');
                     res.status(200).send(dict);
                   } else {
                     console.log('Error \n');
                     res.status(500).send(dict);
                   }
                   console.log(dict);
                }
		});
	});    
  });
  fs.createReadStream(inputFile).pipe(parser);
});

app.delete('/remove_stream', function(req, res) {
  var id = req.param('id'); 
  var nocheck = req.headers['no-check']
  var pwd = req.headers['pwd']
  var inputFile='../config/realserver-backup-list.csv';
  var dict = [];
  var cntr = 0;
  var final_stat = 1;
  console.log("processing realserver list file");
  var parser = parse({from:'2'}, function (err, data) {
    // when all countries are available,then process them
    // note: array element at index 0 contains the row of headers that we should skip
     var data_len = data.length;
     //console.log(data_len);

     data.forEach(function(line) {

      // create country object out of parsed fields
      var realserver =line[0];
     console.log(realserver);
      var headers = {
    	'no-check': nocheck,
    	'pwd':  pwd
      }
      var options = {
        url: 'http://'+realserver+':8088/remove_stream',
        method: 'DELETE',
        headers: headers,
        qs: {'id': id}
	}
        request(options, function (error, response, body) {
		dict[cntr]={
    		server:  line[0],
        	message: response.body,
                stat:  response.statusCode
		};
                if (response.statusCode !=  200) {
                   final_stat = 0;
                }
                cntr += 1;
		//console.log(cntr);
		//console.log(dict);
                if (cntr == data_len) {
                   //console.log(final_stat);
                   if (final_stat == 1) {
                     console.log('Success \n');
                     res.status(200).send(dict);
                   } else {
                     console.log('Error \n');
                     res.status(500).send(dict);
                   }
                   console.log(dict);
                }
		});

     });    

    });    
  fs.createReadStream(inputFile).pipe(parser);
});
