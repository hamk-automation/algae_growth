//FINAL PRODUCT HERE
var bodyParser     = require("body-parser"),
    methodOverride = require("method-override"),
    express        = require("express"),
    flash          = require("connect-flash"),
    cookieParser   = require("cookie-parser"),
    session        = require("express-session"),
    flash          = require("connect-flash"),
    app            = express();
var server         = require("http").Server(app);
var io             = require('socket.io')(server);
app.use(express.static('public'));
app.use(flash());
app.use(session({
    secret: "secret",
    resave: false,
    saveUninitialized: false
}));
app.use(function(req, res, next){
   // res.locals.currentUser = req.user;
   res.locals.error   = req.flash("error");
   res.locals.success = req.flash("success");
   next();
});

app.use(bodyParser.urlencoded({
  extended: true
}));
app.set('view engine', 'ejs');
app.get('/',(req,res)=>{
  res.render('index2');
});
io.on('connect',function(socket){
  console.log("Open the socket");
  app.post('/new_ph',(req,res)=>{
    console.time('test');
    position = Object.getOwnPropertyNames(req.body)[0];
    console.log(position);
    console.log(typeof(position));
    io.emit('welcome', { "data":position });
    socket.on('success',function(){
      console.log("success");
      req.flash("success","Successful Calibration with " + position + " position !!!");
      console.log(res.locals);
      // res.redirect('/bio');
      //socket.removeAllListeners("success");
    });
    socket.on('error',function(){
      console.log("error");
      req.flash("error","Some error exists!! Try to recalibrate !!!");
      // res.redirect('/bio');
      //socket.removeAllListeners("error");
    });
    setTimeout(function(){
      res.redirect('/bio');
      socket.removeAllListeners("success");
      socket.removeAllListeners("error");
      console.timeEnd('test');
    },2500)
  });

});

server.listen(process.env.PORT || 9000, process.env.IP, function(){
    console.log("SERVER IS RUNNING!");
})
