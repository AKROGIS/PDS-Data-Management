function fix() {
	document.getElementById('h2').textContent = "Hello Regan";
}
setTimeout(function(){fix();}, 1000);

function getJSON(url, callback) {
	let xhr = new XMLHttpRequest();
	xhr.onload = function () {
		callback(JSON.parse(this.responseText))
	};
	xhr.open('GET', url, true);
	xhr.send();
  }

function post(data) {
	var str = ""
	var attr = Object.getOwnPropertyNames(data)
	var kv = attr.map((key) => key + '=' + data[key])
	var txt = kv.join(';')
	document.getElementById('p2').textContent = txt;
}

getJSON('/robodata/summary', post)
