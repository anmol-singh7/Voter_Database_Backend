const mongoose = require("mongoose");
// const validator = require("validator");

const VoterSchema = new mongoose.Schema({
    ConNum:{
        type: Number,
        // require: true
    },
    ConName:{
        type:String,
    },
    PartNo:{
        type:Number
    },
    SecNo:{
        type:Number
    },
    SecName:{
        type:String
    },
    SrNo: {
        type: Number
    },
    VoterId:{
         type:String
    },
    Name: {
        type: String,
        // required: true
        // minlength: 3,
    },
    FatherName: {
        type: String,
        // required: true
        // minlength: 3,
    }, 
    HusbandName: {
        type: String,
        // required: true
        // minlength: 3,
    }, 
    MotherName: {
        type:String
    },
    Address:{
        type:String
    },
    Age: {
        type: Number,
    //    require: true
    },
    Sex:{
        type:String,
        // require:true
    }

    
})

const Voter = new mongoose.model("Voter",VoterSchema);

module.exports = Voter;