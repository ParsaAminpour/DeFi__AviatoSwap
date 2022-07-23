// let msg_box = document.getElementById("text-message")
let send_btn = document.getElementById("sending")
let content = document.querySelector(".msg-area")

let roomName = room_name
let roomId = room_id
let user_name = username

let ws = null

window.onload = () => {
    console.log(roomName)
}

const connect = () => {
    ws = new WebSocket(`ws//${window.location.host}/chart/room_${roomName}`)

    ws.onopen = (e) => {
        console.log("web socket opened successfully :)")
    }

    ws.onmessage = (e) => {
        let data_msg = JSON.parse(e.data)
        let message;
        data_msg.type === "msg_handler" 
            ? message = data.message
            : console.log("invalid message sent")
    }

    ws.onclose = (e) => {
        console.log("connecting...")
        setTimeout(() => {
            connect()
        },10000)
    }

    ws.onerror = (e) => {
        console.error(e)
        ws.close()
    }
}

connect.onclick = () => {
    console.log("clicked")
}
// ws.send(JSON.stringify({
//     'message' : msg_box.value 
// }))