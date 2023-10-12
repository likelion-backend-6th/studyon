// 다른 유저와 연결된 RTCPeerConnection 객체를 channel_name으로 저장하는 객체
const mapPeers = {};

// local video element
const localVideo = document.querySelector("#local-video");

// websocket address
const loc = window.location;
console.log("loc: ", loc.pathname);
const wsStart = loc.protocol == "https:" ? "wss://" : "ws://";
const endPoint = wsStart + loc.host + "/ws" + loc.pathname;

// local video stream
var localStream = new MediaStream();

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

const webSocket = new WebSocket(endPoint);

webSocket.onopen = (e) => {
    console.log("WS Connection opened!");

    sendSignal("new-peer", {});
}

webSocket.onmessage = (e) => {
    const parsedData = JSON.parse(e.data);
    const action = parsedData["action"];
    const peerUsername = parsedData["peer"];

    console.log("New message from " + peerUsername + ": " + action)

    // 수신자를 특정하기 위해 channel_name 활용
    // new-offer를 모든 유저가 서로 수신 할 필요는 없기 때문에
    const receiver_channel_name = parsedData["message"]["receiver_channel_name"];

    // 새로운 유저가 접속하면 다른 모든 유저가 수신
    if (action == "new-peer") {
        // create new RTCPeerConnection
        createOfferer(peerUsername, receiver_channel_name);
        return;
    }
    // 처음 접속한 유저만 수신
    else if (action == "new-offer") {
        // create new RTCPeerConnection
        // set offer as remote description
        const offer = parsedData["message"]["sdp"];
        const ices = parsedData["message"]["ice"];
        console.log("ICE, ", ices)
        createAnswerer(offer, ices, peerUsername, receiver_channel_name);
        return;
    }
    // 이미 접속해 있던 유저만 수신
    else if (action == "new-answer") {
        // createOfferer에서 생성한 peer 가져오기
        const peer = mapPeers[receiver_channel_name][0];
        // get the answer
        const answer = parsedData["message"]["sdp"];
        const ices = parsedData["message"]["ice"];

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
    // 다른 유저의 연결 해제
    else if (action == "disconnect") {
        if (mapPeers[receiver_channel_name]) {
            const [peer, remoteVideo] = mapPeers[receiver_channel_name]
            console.log(peer, remoteVideo)
            console.warn("Disconnecting from ", peerUsername)
            peer.close()
            removeVideo(remoteVideo)
            delete mapPeers[receiver_channel_name]
        }
    }
    return
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
        const mediaTracks = stream.getTracks();

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
    const peer = new RTCPeerConnection(iceConfiguration);
    const ICECandidate = [];

    // local user media stream tracks 추가
    addLocalTracks(peer)

    // remote video element 생성
    const remoteVideo = createVideo(receiver_channel_name, peerUsername);
    setOnTrack(peer, remoteVideo);
    console.debug("Create video source: ", remoteVideo.srcObject);

    // store the RTCPeerConnection
    mapPeers[receiver_channel_name] = [peer, remoteVideo];

    // ice connection state가 변경될 때마다 호출
    peer.oniceconnectionstatechange = () => {
        const iceConnectionState = peer.iceConnectionState;
        console.log("peer.iceConnectionState: ", iceConnectionState)
        if (iceConnectionState === "failed" || iceConnectionState === "closed") {
            console.warn("peer.iceConnectionState: ", iceConnectionState)
            if (iceConnectionState != "closed") {
                peer.close();
            }
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
    const peer = new RTCPeerConnection(iceConfiguration);
    const ICECandidate = [];

    // local user media stream tracks 추가
    addLocalTracks(peer);

    // remote video element 생성
    const remoteVideo = createVideo(receiver_channel_name, peerUsername);
    setOnTrack(peer, remoteVideo);

    console.debug("Create video source: ", remoteVideo.srcObject);

    // store the RTCPeerConnection
    mapPeers[receiver_channel_name] = [peer, remoteVideo];

    // ice connection state가 변경될 때마다 호출
    peer.oniceconnectionstatechange = () => {
        const iceConnectionState = peer.iceConnectionState;
        console.log("peer.iceConnectionState: ", iceConnectionState)
        if (iceConnectionState === "failed" || iceConnectionState === "closed") {
            console.warn("peer.iceConnectionState: ", iceConnectionState)
            if (iceConnectionState != "closed") {
                peer.close();
            }
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
function createVideo(videoID, username) {
    const videoContainer = document.querySelector("#video-container");
    const videoWrapper = document.createElement("div");
    const remoteVideo = document.createElement("video");
    const videoLabel = document.createElement("p");

    // 설정
    videoWrapper.className = "relative aspect-video video-box max-w-xl bg-neutral-900 flex justify-center items-center";
    remoteVideo.id = videoID + "-video";
    remoteVideo.className = "w-full h-full object-cover";
    remoteVideo.autoplay = true;
    remoteVideo.playsinline = true;
    videoLabel.className = "absolute px-2 bg-[rgba(25,25,25,.60)] left-0 bottom-0 text-sm text-white";
    videoLabel.innerText = username;

    // add the video to the container
    videoWrapper.appendChild(remoteVideo);
    videoWrapper.appendChild(videoLabel);
    videoContainer.appendChild(videoWrapper);

    // grid layout 설정
    gridResize();

    return remoteVideo;
}

function gridResize() {
    const videoContainer = document.querySelector("#video-container");
    const numVideoBoxes = videoContainer.querySelectorAll('.video-box').length;
    const gridColumns = Math.ceil(Math.sqrt(numVideoBoxes));
    videoContainer.style.gridTemplateColumns = `repeat(${gridColumns}, 1fr)`;
}

// remoteStream에 remote tracks를 추가하고
// 해당 remote video element에 연결
function setOnTrack(peer, remoteVideo) {
    console.log("Setting ontrack:");
    // create new MediaStream for remote tracks
    const remoteStream = new MediaStream();

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
    const videoWrapper = video.parentNode;
    videoWrapper.parentNode.removeChild(videoWrapper);
}

document.querySelector("#new-video").onclick = () => {
    createVideo("asdf", "testUser")
}

document.querySelector("#btn_microphone").onclick = () => {
    const audioTracks = localStream.getAudioTracks();
    const on = document.querySelector("#microphone_on")
    const off = document.querySelector("#microphone_off")
    audioTracks[0].enabled = !audioTracks[0].enabled
    if (audioTracks[0].enabled) {
        on.hidden = false
        off.hidden = true
    } else {
        on.hidden = true
        off.hidden = false
    }
}

document.querySelector("#btn_camera").onclick = () => {
    const videoTracks = localStream.getVideoTracks();
    const on = document.querySelector("#camera_on")
    const off = document.querySelector("#camera_off")
    videoTracks[0].enabled = !videoTracks[0].enabled
    if (videoTracks[0].enabled) {
        on.hidden = false
        off.hidden = true
    } else {
        on.hidden = true
        off.hidden = false
    }
}

