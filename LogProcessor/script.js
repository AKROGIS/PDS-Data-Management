
// Return bytes as human readable quantity
// Credit: https://stackoverflow.com/a/14919494
function humanFileSize(bytes, si) {
    var thresh = si ? 1000 : 1024;
    if(Math.abs(bytes) < thresh) {
        return bytes + ' Bytes';
    }
    var units = si
        ? ['kB','MB','GB','TB','PB','EB','ZB','YB']
        : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while(Math.abs(bytes) >= thresh && u < units.length - 1);
    return bytes.toFixed(1)+' '+units[u];
}


function fix() {
	document.getElementById('h2_test').textContent = "Hello Regan";
}
setTimeout(function(){fix();}, 1000);

function getJSON(url, callback, errorback) {
	let xhr = new XMLHttpRequest();
	xhr.open('GET', url, true);
	xhr.responseType = 'json';
	xhr.onload = function() {
		if (this.readyState == this.DONE) {
			if (this.status == 200) {
				if (this.response !== null) {
					callback(this.response);
				} else {
					errorback('Bad JSON object returned from Server');
				}
			} else {
				errorback(this.statusText);
			}
		}
		 };
	xhr.send();
  }

function post_summary(data) {
	var attr = Object.getOwnPropertyNames(data);
	attr.forEach((key) => {
		var ele = document.getElementById(key);
		if (ele != undefined) {
			ele.textContent = data[key];
		}
	});
	document.getElementById('bytes_copied').textContent = humanFileSize(data['bytes_copied'],true);
	document.getElementById('bytes_removed').textContent = humanFileSize(data['bytes_removed'],true);
	var count_not_finished = data['count_incomplete'] + data['count_unfinished']
	var count_total_parks = data['count_complete']
	var total_errors = data['total_errors']
	var issues = total_errors > 0 || count_not_finished > 0;
	document.getElementById('count_total_parks').textContent = count_total_parks;
	document.getElementById('count_not_finished').textContent = count_not_finished;
	if (issues) {
		document.getElementById('no_issues').hidden = true;
	}
	if (count_not_finished > 0) {
		document.getElementById('summary_incomplete').hidden = false;
		document.getElementById('summary_card').style.cssText = 'background-color: #ffffdd;';;
	}
	if (total_errors > 0) {
		document.getElementById('summary_errors').hidden = false;
		document.getElementById('summary_card').style.cssText = 'background-color: #ffdddd;';;
	}
}

function summary_failed(message) {
	ele = document.getElementById('summary_fail');
	if (message == 'Service Unavailable') {
		message2 = 'Check to make sure the python service is running.';
		ele.textContent = message + '. ' + message2;
	} else {
		ele.textContent = message;
	}
	ele.style.cssText = 'color: #990000; background-color: #ffdddd;';
}

getJSON('/robodata/summary', post_summary, summary_failed)
