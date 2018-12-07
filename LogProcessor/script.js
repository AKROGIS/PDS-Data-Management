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

// Adds or updates the parameter in a query string
// credit: https://stackoverflow.com/a/11654596
function UpdateQueryString(key, value, url) {
    if (!url) url = window.location.href;
    var re = new RegExp("([?&])" + key + "=.*?(&|#|$)(.*)", "gi"),
        hash;

    if (re.test(url)) {
        if (typeof value !== 'undefined' && value !== null)
            return url.replace(re, '$1' + key + "=" + value + '$2$3');
        else {
            hash = url.split('#');
            url = hash[0].replace(re, '$1$3').replace(/(&|\?)$/, '');
            if (typeof hash[1] !== 'undefined' && hash[1] !== null)
                url += '#' + hash[1];
            return url;
        }
    }
    else {
        if (typeof value !== 'undefined' && value !== null) {
            var separator = url.indexOf('?') !== -1 ? '&' : '?';
            hash = url.split('#');
            url = hash[0] + separator + key + '=' + value;
            if (typeof hash[1] !== 'undefined' && hash[1] !== null)
                url += '#' + hash[1];
            return url;
        }
        else
            return url;
    }
}

// generic request to get JSON data from data service
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

// Success callback for adding summary data to the web page
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
	var count_not_finished = data['count_incomplete'] + data['count_unfinished'];
	var count_total_parks = data['count_complete'] + count_not_finished;
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
	fix_button_state();
}

// Success callback for adding date limitsto the web page
function post_dates(data) {
	document.getElementById('previous_date').dataset.limit = data['first_date'];
	document.getElementById('next_date').dataset.limit = data['last_date'];
	fix_button_state();
}

// Error callback for adding summary error to the web page
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

// Update the state of the next/previous date buttons
// called both when date is updated and when the min/max dates are updated.
function fix_button_state() {
	var date = document.getElementById('summary_date').textContent;
	var previous_button = document.getElementById('previous_date');
	var next_button = document.getElementById('next_date');
	var min_date = previous_button.dataset.limit;
	var max_date = next_button.dataset.limit;

	//TODO: instantiating a new date with a string is discouraged due to browser differences
	var next_date = new Date(date);
	next_date.setDate(next_date.getDate() + 1);
	var next_text = next_date.toISOString().substring(0, 10);
	next_button.dataset.destination = next_text;

	var previous_date = new Date(date);
	previous_date.setDate(previous_date.getDate() - 1)
	var previous_text = previous_date.toISOString().substring(0, 10);
	previous_button.dataset.destination = previous_text;

	previous_button.disabled = (date <= min_date);
	next_button.disabled = (max_date <= date);
}

// Validate a user provided iso date string
function is_valid_date(date) {
	//TODO: validate date
	return date !== null;
}

// ===========
// DOM Events
// ===========

function next_date() {
	var destination = document.getElementById('next_date').dataset.destination;
	location.href = UpdateQueryString('date', destination);
}

function previous_date() {
	var destination = document.getElementById('previous_date').dataset.destination;
	location.href = UpdateQueryString('date', destination);
}

// Get data from the services and update the page
function get_data() {
	let params = new URLSearchParams(document.location.search.substring(1));
	let date = params.get("date");
	var url = '/robodata/summary';
	if (is_valid_date(date)) {
		url += '?date=' + date;
	}
	getJSON(url, post_summary, summary_failed)
	//TODO: if date not provided, check if returned date is within 24 hours, otherwise we have a problem
	getJSON('/robodata/dates', post_dates)
}

get_data();
