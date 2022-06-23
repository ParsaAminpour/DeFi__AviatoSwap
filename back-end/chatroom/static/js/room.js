let $ = document
let room_name = $.getElementById('room_name')
let room_id = $.getElementById('room_id')
let back = $.getElementById('back')


window.addEventListener('load', () => {
	const ws = new WebSocket(`ws://${window.location.host}/ws/chat/rooms/${room_id}`);

	ws.onopen = (e) => {
        Swal.fire({
            title: '<strong>Connection Stablished Successfuly </strong>',
            html: '',
 
            showCloseButton: true,
            focusConfirm: true,
  
            confirmButtonText: '<i class="fa fa-thumbs-up"></i> Great!',
            confirmButtonAriaLabel: 'Thumbs up, great!',
        })		
	} 

	ws.onclose = (e) => {
        setTimeout(() => {
        	Swal.fire({
            	title: '<strong>Connection is failed, reconnecting in 10sec..</strong>',
            	html: '',
        	})
        }, 10000)
	}

	ws.onmessage = async(e) => {
		data = JSON.parse(e.data)
		message = data['message']
		username = data['username']

		await switch(data.tye){
			case 'message_handler':
				console.log('Received')
				break
		}
	}
})

function backing() {
	return history.back()
}
