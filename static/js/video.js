// 다른 유저와 연결된 RTCPeerConnection 객체를 username으로 저장하는 객체
var mapPeers = {};

// local video element
const localVideo = document.querySelector("#local-video");

// local video stream
var localStream = new MediaStream();

// websocket address
var loc = window.location;
var wsStart = "ws://";
if (loc.protocol == "https:") {
    wsStart = "wss://";
}
var endPoint = wsStart + loc.host + "/video";

var username = document.getElementById("data").getAttribute("data-username");

// media stream constraints
const constraints = {
    "video": true,
    "audio": true
}

// ice server configuration
// 나중에 turn server를 추가하면 됨
const iceConfiguration = {
    iceServers: [
        {
            urls: ["turn:175.45.202.123:3478"],
            username: "terry",
            credential: "terry"
        }
    ]
};

var webSocket;

console.log(username)

webSocket = new WebSocket(endPoint);

webSocket.onopen = (e) => {
    console.log("WS Connection opened!");

    sendSignal("new-peer", {});
}

webSocket.onmessage = (e) => {
    var parsedData = JSON.parse(e.data);
    var action = parsedData["action"];
    var peerUsername = parsedData["peer"];

    console.debug("New message from " + peerUsername + ": " + action)

    if (peerUsername == username) {
        // 본인이 전송한 메시지는 무시
        return;
    }

    console.log("New message from " + peerUsername + ": " + action)

    // 수신자를 특정하기 위해 channel_name 활용
    // new-offer를 모든 유저가 서로 수신 할 필요는 없기 때문에
    var receiver_channel_name = parsedData["message"]["receiver_channel_name"];

    // in case of new peer
    // 새로운 유저가 접속하면 다른 모든 유저가 수신
    if (action == "new-peer") {
        // create new RTCPeerConnection
        createOfferer(peerUsername, receiver_channel_name);
        return;
    }

    // in case of new offer
    // 처음 접속한 유저만 수신
    if (action == "new-offer") {
        // create new RTCPeerConnection
        // set offer as remote description
        var offer = parsedData["message"]["sdp"];
        var ices = parsedData["message"]["ice"];
        console.log("ICE, ", ices)
        createAnswerer(offer, ices, peerUsername, receiver_channel_name);
        return;
    }

    // in case of new answer
    // 이미 접속해 있던 유저만 수신
    if (action == "new-answer") {
        // createOfferer에서 생성한 peer 가져오기
        var peer = mapPeers[peerUsername];
        // get the answer
        var answer = parsedData["message"]["sdp"];
        var ices = parsedData["message"]["ice"];

        // 생성했던 peer에 remote description연결
        peer.setRemoteDescription(answer)
            .then(() => {
                console.log("Set remote description for %s.", peerUsername);
            })
            .catch(error => {
                console.error("Error creating answer for %s.", peerUsername, error);
            });

        // 전송받은 ice candidate 추가
        console.log("Ice candidate added.");
        ices.forEach(ice => {
            peer.addIceCandidate(ice)
                .catch(error => {
                    console.error("Error adding ice candidate:", error);
                });
        })
        return;
    }
}

webSocket.onclose = function (e) {
    console.log("WS Connection closed! ", e);
}

webSocket.onerror = function (e) {
    console.error("WS Error occured! ", e);
}

function sendSignal(action, message) {
    webSocket.send(
        JSON.stringify(
            {
                "action": action,
                "message": message,
            }
        )
    )
}

// User media 설정
userMedia = navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
        localStream = stream;
        console.log("Got MediaStream:", stream);
        var mediaTracks = stream.getTracks();

        console.debug("Got MediaStreamTrack: ")
        for (i = 0; i < mediaTracks.length; i++) {
            console.debug(mediaTracks[i]);
        }

        // 비디오 연결
        localVideo.srcObject = localStream;
        // 본인 오디오 mute
        localVideo.muted = true;

        audioTracks = stream.getAudioTracks();
        videoTracks = stream.getVideoTracks();

        // unmute audio and video by default
        audioTracks[0].enabled = true;
        videoTracks[0].enabled = true;
    })
    .catch(error => {
        console.error("Error accessing media devices.", error);
    });


// create RTCPeerConnection as offerer and store it
// send sdp to remote peer after gathering is complete
function createOfferer(peerUsername, receiver_channel_name) {
    console.log("createOfferer called.")
    var peer = new RTCPeerConnection(iceConfiguration);
    var ICECandidate = [];

    // local user media stream tracks 추가
    addLocalTracks(peer)

    // remote video element 생성
    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);
    console.debug("Create video source: ", remoteVideo.srcObject);

    // store the RTCPeerConnection
    mapPeers[peerUsername] = peer;

    // ice connection state가 변경될 때마다 호출
    peer.oniceconnectionstatechange = () => {
        var iceConnectionState = peer.iceConnectionState;
        if (iceConnectionState === "failed" || iceConnectionState === "disconnected" || iceConnectionState === "closed") {
            console.warn("peer.iceConnectionState: ", iceConnectionState)
            delete mapPeers[peerUsername];
            if (iceConnectionState != "closed") {
                peer.close();
            }
            removeVideo(remoteVideo);
        }
    };

    // ice값을 수집할 때마다 호출
    peer.onicecandidate = (event) => {
        // event.candidate == null 일 때 수집 완료
        if (event.candidate) {
            console.debug("New candidate, ", event.candidate);
            ICECandidate.push(event.candidate);
            return;
        }

        console.log("Gathering finished! Sending offer SDP to ", peerUsername, ".");
        console.debug("receiverChannelName: ", receiver_channel_name);
        console.debug("New Ice Candidate! Reprinting SDP" + JSON.stringify(peer.localDescription));

        // send offer to new peer
        sendSignal("new-offer", {
            "sdp": peer.localDescription,
            "ice": ICECandidate,
            "receiver_channel_name": receiver_channel_name,
        });
    }

    console.log("Creating offer.")
    peer.createOffer()
        .then(o => {
            return peer.setLocalDescription(o)
        })
        .then(() => {
            console.log("Local Description Set successfully.");
        })
        .catch(error => {
            console.error("Error creating offer:", error);
        });

    return peer;
}

// create RTCPeerConnection as answerer and store it
// send sdp to remote peer after gathering is complete
function createAnswerer(offer, ices, peerUsername, receiver_channel_name) {
    console.log("createAnswerer called.")
    var peer = new RTCPeerConnection(iceConfiguration);
    var ICECandidate = [];

    // local user media stream tracks 추가
    addLocalTracks(peer);

    // remote video element 생성
    var remoteVideo = createVideo(peerUsername);
    setOnTrack(peer, remoteVideo);

    console.debug("Create video source: ", remoteVideo.srcObject);

    // store the RTCPeerConnection
    mapPeers[peerUsername] = peer;

    // ice connection state가 변경될 때마다 호출
    peer.oniceconnectionstatechange = () => {
        var iceConnectionState = peer.iceConnectionState;
        if (iceConnectionState === "failed" || iceConnectionState === "disconnected" || iceConnectionState === "closed") {
            console.warn("peer.iceConnectionState: ", iceConnectionState)
            delete mapPeers[peerUsername];
            if (iceConnectionState != "closed") {
                peer.close();
            }
            removeVideo(remoteVideo);
        }
    };

    // ice값을 수집할 때마다 호출
    peer.onicecandidate = (event) => {
        // event.candidate == null 일 때 수집 완료
        if (event.candidate) {
            console.debug("New candidate, ", event.candidate);
            ICECandidate.push(event.candidate);
            return;
        }

        console.log("Gathering finished! Sending offer SDP to ", peerUsername, ".");
        console.debug("receiverChannelName: ", receiver_channel_name);
        console.debug("New Ice Candidate! Reprinting SDP" + JSON.stringify(peer.localDescription));

        // send answer to offering peer
        sendSignal("new-answer", {
            "sdp": peer.localDescription,
            "ice": ICECandidate,
            "receiver_channel_name": receiver_channel_name
        });
    }

    // 전송받은 offer를 remote description으로 설정
    peer.setRemoteDescription(offer)
        .then(() => {
            console.log("Set offer from %s.", peerUsername);
            return peer.createAnswer();
        })
        .then(a => {
            console.debug("Setting local answer for %s.", peerUsername);
            return peer.setLocalDescription(a);
        })
        .then(() => {
            console.log("Answer created for %s.", peerUsername);
        })
        .catch(error => {
            console.error("Error creating answer for %s.", peerUsername, error);
        });

    console.log("Ice candidate added.");
    ices.forEach(ice => {
        // 전송받은 ice candidate 추가
        peer.addIceCandidate(ice)
            .catch(error => {
                console.error("Error adding ice candidate:", error);
            });
    })

    return peer
}

// 새로운 유저가 연결되면 video element 생성
function createVideo(peerUsername) {
    var videoContainer = document.querySelector("#video-container");
    // create the new video element
    var remoteVideo = document.createElement("video");
    remoteVideo.id = peerUsername + "-video";
    remoteVideo.autoplay = true;
    remoteVideo.playsinline = true;

    // add the video to the container
    videoContainer.appendChild(remoteVideo);
    return remoteVideo;
}

// remoteStream에 remote tracks를 추가하고
// 해당 remote video element에 연결
function setOnTrack(peer, remoteVideo) {
    console.log("Setting ontrack:");
    // create new MediaStream for remote tracks
    var remoteStream = new MediaStream();

    remoteVideo.srcObject = remoteStream;

    peer.addEventListener("track", async (event) => {
        console.log("Adding track: ", event.track);
        remoteStream.addTrack(event.track, remoteStream);
    });
}

// peer에 localStream tracks를 추가
function addLocalTracks(peer) {
    localStream.getTracks().forEach(track => {
        console.debug("Adding localStream tracks.", track);
        peer.addTrack(track, localStream);
    });
    return;
}

// video element 삭제
function removeVideo(video) {
    video.parentNode.removeChild(video);
}