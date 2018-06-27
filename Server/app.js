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
   res.locals.error = req.flash("error");
   res.locals.success = req.flash("success");
   next();
});
// app.use(cookieParser('keyboard cat'));
// app.use(session({ cookie: { maxAge: 60000 }}));
// app.use(flash());

app.use(bodyParser.urlencoded({
  extended: true
}));
// app.use(cookieParser('secret'));
//app.use(express.session({ cookie: { maxAge: 60000 }}));
app.set('view engine', 'ejs');
app.get('/',(req,res)=>{
  res.render('index2');
  // while(true){
  //   continue;
  // }
});
io.on('connect',function(socket){
  console.log("Open the socket");
  app.post('/new_ph',(req,res)=>{
    socket.removeAllListeners("success");
    socket.removeAllListeners("error");
    position = Object.getOwnPropertyNames(req.body)[0];
    console.log(position);
    console.log(typeof(position));
    io.emit('welcome', { "data":position });
    socket.on('success',function(){
      console.log("success");
      req.flash("success","Successful Calibration !!!");
      res.redirect('/bio');
      //socket.removeAllListeners("success");
    });
    socket.on('error',function(){
      console.log("error");
      req.flash("error","Some error exists!! Try to recalibrate !!!");
      res.redirect('/bio');
      //socket.removeAllListeners("error");
    });
    // console.log("before");
    // res.redirect('/bio');
    // socket.on('error',()=>{
    //   console.log("error");
    // });

  });

});
// app.post('/new_ph',(req,res)=>{
//   position = Object.getOwnPropertyNames(req.body)[0];
//   console.log(position);
//   console.log(typeof(position));
//   io.emit('welcome', { "data":position });
//   res.redirect('/bio');
// });
// io.on('connect', function (socket) {
//   console.log("Socket is open");
//   socket.on('success', function () {
//     // req.flash('success', 'This is a flash message using the express-flash module.');
//     console.log("success");
//     console.log(socket.handshake);
//   });
//   socket.on('error', function () {
//     console.log("error");
//   });
// });
// io.on('success',function(){
// console.log("Outside");
// });
// io.on('connection', function (socket) {
//   socket.on('success', function () {
//     // req.flash('success', 'This is a flash message using the express-flash module.');
//     console.log("success");
//     console.log(socket.handshake);
//   });
//   socket.on('error', function () {
//     console.log("error");
//   });
// });
// app.use(function(req, res, next){
//    res.locals.error = req.flash("error");
//    res.locals.success = req.flash("success");
//    next();
// });

server.listen(process.env.PORT || 9000, process.env.IP, function(){
    console.log("SERVER IS RUNNING!");
})
