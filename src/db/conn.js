const mongoose = require("mongoose");
mongoose.set('strictQuery', false);
const DB =process.env.DATABASE;
mongoose.connect(DB
    // , {
    //     useCreateIndex: true,
    //     useNewUrlParser: true,
    //     useUnifiedTopology: true,
    //     useFindAndModify:false
    // }
).then(() => {
    console.log("connection successfull  by mongoose")
})
    .catch((err) => {
        console.log("ohh no error!")
        console.log(err);
    })