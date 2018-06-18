//FINAL PRODUCT HERE
var bodyParser     = require("body-parser"),
    methodOverride = require("method-override"),
    express        = require("express"),
    flash          = require("connect-flash"),
    cookieParser   = require("cookie-parser"),
    session        = require("express-session"),
    app            = express();
var server         = require("http").Server(app);
var io             = require('socket.io')(server);
app.use(express.static('public'));
// app.use(flash());
// app.use(require("express-session")({
//     secret: "Once again Rusty wins cutest dog!",
//     resave: false,
//     saveUninitialized: false
// }));
app.use(bodyParser.urlencoded({
  extended: true
}));
// app.use(cookieParser('secret'));
//app.use(express.session({ cookie: { maxAge: 60000 }}));
app.set('view engine', 'ejs');
app.get('/',(req,res)=>{
  res.render('index2');
});
app.post('/new',(req,res)=>{
  position = Object.getOwnPropertyNames(req.body)[0];
  console.log(position);
  console.log(typeof(position));
  io.emit('welcome', { "data":position });
  res.redirect('/bio');

});

server.listen(process.env.PORT || 9000, process.env.IP, function(){
    console.log("SERVER IS RUNNING!");
})
