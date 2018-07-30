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
var connected_socket;
app.use(express.static('public'));
app.use(flash());
app.use(session({
    secret: "secret",
    resave: false,
    saveUninitialized: false
}));
app.use(function(req, res, next){
  res.io = io;
  next();
});
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
io.on("connection",(socket)=>{
  connected_socket = socket;
});
app.get('/',(req,res)=>{
  res.render('home');
});
app.get('/instruction',(req,res)=>{
  res.render('instruction');
});
app.post('/new_ph',(req,res)=>{
  position = Object.getOwnPropertyNames(req.body)[0];
  res.io.emit('send_data', { "data":position });
  //console.log(connected_socket.connected);
  connected_socket.on('success',function(){
      console.log("success");
      req.flash("success",position);
    });
  connected_socket.on('error',function(){
      console.log("error");
      req.flash("error","Some error exists!! Try to recalibrate !!!");
    });
  setTimeout(function(){
      //res.redirect('/bio');
      connected_socket.removeAllListeners("success");
      connected_socket.removeAllListeners("error");
      res.redirect('/');

    },2500)
});


server.listen(process.env.PORT || 9000, process.env.IP, function(){
    console.log("SERVER IS RUNNING!");
})
