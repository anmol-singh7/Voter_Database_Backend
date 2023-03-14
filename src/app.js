const dotenv = require("dotenv")
dotenv.config({ path: "./config.env" });
const express = require("express");
const bodyParser = require("body-parser");
require("./db/conn");


const VoterRouter = require("./routers/Voter");

const app = express();
const PORT = process.env.PORT || 8000;
app.use(bodyParser.urlencoded({ extended: true,parameterLimit:100000, limit: "50mb" }));
// app.use(bodyParser.json())
app.use(express.json({ limit: '50mb' }));
// app.use(express.urlencoded({ limit: '50mb' }));
// app.use(express.json());   //<-- use to read req.body withot it give undefined
app.use(VoterRouter);



app.listen(PORT, () => {
    console.log(`connection is setup at ${PORT}`);
})