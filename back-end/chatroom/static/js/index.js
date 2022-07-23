const $ = document

connection = null
const connect = (room_name) => {
	const ws = new WebSocket(`ws://${window.location.host}/chat/${room_name}`)

	ws.onopen = (e) => {
		console.log(`Websocker connected successfully in room of ${room_name}`);
	}

	ws.onclose = (e) => {
		console.log("Websocket disconnected")

		setTimeout(() => {
			console.log("Connecting ....");
			connect()
		}, 10000)
	}

	ws.onmessage = (e) => {
		let data = JSON.parse(e.data)
		let message = data.msg_handler ?? "invalid type sended"

		console.log(message)
	}
}

function test() {
    console.log("CLICKED");
}
 