const express = require("express");
require("../db/conn")
const router = new express.Router();
const Voter = require("../models/voter");

router.post("/Voters", async (req, res) => {
    try {
        list =req.body
        list.map(async(voterToBeInserted)=>{
            const voter = await Voter.find({ VoterId: voterToBeInserted.VoterId})
            // console.log(voter.length)
            if(voter.length===0){
                // console.log("xx",voter)
                const user = new Voter(voterToBeInserted);
              await  user.save();
            }
        })
        console.log("heool")
        res.status(201).send("successful in ert voters");
    } catch (e) {
        res.status(400).send(e)
    }
});

router.post("/Voter", async (req, res) => {
    try {
            const voter = await Voter.find({ VoterId: req.body.VoterId })
            console.log(voter)
            if (voter.length===0) {
                console.log("xx", req.body)
                const user = new Voter(req.body);
                user.save();
            }
        res.status(201).send(voter);
    } catch (e) {
        res.status(400).send(e)
    }
});

// router.get("/Voters", async (req, res) => {
//     try {
//         const VotersData = await Voter.find();
//         res.send(VotersData);
//     } catch (err) {
//         res.send(err)
//     }
// });


router.get("/Voters/ConNum", async (req, res) => {
    try {
        const Num = req.body.ConNum;   //<--- this id is same as written in get in in get /Voters/:xyz written then we have to use req.params.xyz 
        const VotersData = await Voter.find({ConNum:Num});
        res.status(200).send(VotersData);
    } catch (err) {
        res.status(500).send(err);
    }
});

router.get("/Voters/ConNum/SecNo", async (req, res) => {
    try {
        const ConNo = req.body.ConNum; 
        const SecN =req.body.SecNo
        const VotersData = await Voter.find({ ConNum: ConNo ,SecNo:SecN});
        res.status(200).send(VotersData);
    } catch (err) {
        res.status(500).send(err);
    }
});

router.patch("/Voters/update/VoterId", async (req, res) => {
    try {
        const Id = req.body.VoterId
        const updatedData = await Voter.updateMany({VoterId:Id}, req.body, { new: true });
        res.send(updatedData);
    } catch (err) {
        res.status(400).send(err);
    }
});

router.delete("/Voter/:VoterId", async (req, res) => {
    try {
        const Id = req.body.VoterId;
        console.log(Id)
        const deletedVoter = await Voter.deleteMany({VoterId:Id});
        if (!Id) {    //<-- this extra check just in case _id/req.params.id is int present in database/undefined
            return res.status(400).send("No voter with this Voter id found in database");
        }
        res.send(deletedVoter);
    } catch (err) {
        console.log("error")
        res.status(500).send(err);
    }
});

module.exports = router;