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

//rounds a number to a specified number of decimal digits
//credit: http://www.jacklmoore.com/notes/rounding-in-javascript/
function round(value, decimals) {
	return Number(Math.round(value+'e'+decimals)+'e-'+decimals);
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
	if (Object.keys(data).length === 0 && data.constructor === Object) {
		document.getElementById('summary').hidden = true;
		document.getElementById('graphs').hidden = true;
		document.getElementById('summary_fail').hidden = false;
		return
	}
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
	var total_errors = data['total_errors'] || 0;
	var issues = total_errors > 0 || count_not_finished > 0;
	document.getElementById('count_total_parks').textContent = count_total_parks;
	document.getElementById('count_not_finished').textContent = count_not_finished;
	if (issues) {
		document.getElementById('no_issues').hidden = true;
		if (total_errors == 0) {
			document.getElementById('summary_card').classList.replace('nominal', 'warning');
		} else {
			document.getElementById('summary_card').classList.replace('nominal', 'error');
		}
	}
	if (count_not_finished > 0) {
		document.getElementById('summary_incomplete').hidden = false;
	}
	if (total_errors > 0) {
		document.getElementById('summary_errors').hidden = false;
	}
	document.getElementById('changelog_link').href = 'PDS_ChangeLog.html#' + data['page_date']
}

// Success callback for adding park details to the web page
function post_park_details(data) {
	if (data.length === 1) {
		document.getElementById('park_details').hidden = true;
		return
	}
	//["park","date","finished","count_errors","files_copied","files_removed","files_scanned","time_copying","time_scanning","bytes_copied"]
	//Ignore the first row (header), assume there are no more then 20 parks
	html = '';
	data.slice(1, 20).forEach((row) => {
		var park = row[0];
		var date = row[1];
		var bytes_copied = row[9];
		var size_copied = humanFileSize(bytes_copied,true);
		var time_copying = row[7];
		var copy_speed = round(bytes_copied/time_copying/1000.0,1);
		var copy_text = time_copying == 0 ? 'Nothing copied.' : `${size_copied} in ${time_copying} seconds => ${copy_speed} kB/second`;
		var files_scanned = row[6];
		var time_scanning = row[8];
		var scan_speed = round(files_scanned/time_scanning,1);
		var files_removed = row[5];
		var finished = row[2];
		var count_errors = row[3];
		var status = count_errors == 0 ? (finished == 1 ? 'nominal' : 'warning') : 'error';
		var error_str = count_errors == 0 ? '' : `${count_errors} Errors.`;
		var finish_str = finished == 1 ? '' : 'Robocopy did not finish (no timing statistics).';
		var issues = 'No Issues.';
		if (error_str == '' && finish_str != '') {
			issues = finish_str;
		} else if (error_str != '' && finish_str == '') {
			issues = error_str;
		} else if (error_str != '' && finish_str != '') {
			issues = error_str + ' ' + finish_str;
		}
		var card_str = `
			<div class='card ${status}'>
				<h3>${park}</h3>
				<a href='//inpakrovmais:8080/logfile?park=${park}&date=${date}'>Log file</a>
				<dt>Copied</dt>
				<dd>${copy_text}</dd>
				<dt>Scanned</dt>
				<dd>${files_scanned} files in ${time_scanning} seconds => ${scan_speed} files/second</dd>
				<dt>Removed</dt>
				<dd>${files_removed} files</dd>
				<dt>Issues</dt>
				<dd>${issues}</dd>
			</div>
		`
		html += card_str
	});
	document.getElementById('park_cards').innerHTML = html;
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

// Error callback for adding park details error to the web page
function parks_failed(message) {
	ele = document.getElementById('parks_fail');
	ele.textContent = message;
	ele.style.cssText = 'color: #990000; background-color: #ffdddd;';
}

// Update the state of the date text and the next/previous date buttons
function fix_date_button_state(date, min_date, max_date) {
	document.getElementById('page_date').textContent = date;
	var previous_button = document.getElementById('previous_date');
	var next_button = document.getElementById('next_date');
	previous_button.dataset.limit = min_date;
	next_button.dataset.limit = max_date;

	//TODO: instantiating a new date with a string is discouraged due to browser differences
	var next_date = new Date(date);
	next_date.setDate(next_date.getDate() + 1);
	var next_text = next_date.toISOString().substring(0, 10);
	next_button.dataset.destination = next_text;

	var previous_date = new Date(date);
	previous_date.setDate(previous_date.getDate() - 1)
	var previous_text = previous_date.toISOString().substring(0, 10);
	previous_button.dataset.destination = previous_text;

	previous_button.hidden = (date <= min_date);
	next_button.hidden = (max_date <= date);
}

// Validate a user provided iso date string
// Range is open, i.e. min_date and max_date are allowed, if null then no limit
function is_valid_date(date, min_date, max_date) {
	//TODO: validate date
	return date !== null && date !== undefined;
}

function plot_2bars(x, l1, y1, l2, y2, title) {
	var trace1 = {
		x: x,
		y: y1,
		name: l1,
		type: 'bar'
	};

	var trace2 = {
		x: x,
		y: y2,
		name: l2,
		type: 'bar'
	};
	var layout = {
		barmode: 'group',
		title: title
	};
	Plotly.newPlot("graph_div", [trace1, trace2], layout);
}

function plot_2lines(x, l1, y1, l2, y2, title) {
	var trace1 = {
		x: x,
		y: y1,
		name: l1,
		type: "scatter",
		mode: "lines"
	};
	var trace2 = {
		x: x,
		y: y2,
		name: l2,
		type: "scatter",
		mode: "lines"
	};
	var layout = {
		title: title
	};
	Plotly.newPlot("graph_div", [trace1, trace2], layout);
}

function plot_5lines(x, l1, y1, l2, y2, l3, y3, l4, y4, l5, y5, title) {
	var trace1 = {
		x: x,
		y: y1,
		name: l1,
		type: "scatter",
		mode: "lines"
	};
	var trace2 = {
		x: x,
		y: y2,
		name: l2,
		type: "scatter",
		mode: "lines"
	};
	var trace3 = {
		x: x,
		y: y3,
		name: l3,
		type: "scatter",
		mode: "lines"
	};
	var trace4 = {
		x: x,
		y: y4,
		name: l4,
		type: "scatter",
		mode: "lines"
	};
	var trace5 = {
		x: x,
		y: y5,
		name: l5,
		type: "scatter",
		mode: "lines"
	};
	var layout = {
		title: title
	};
	Plotly.newPlot("graph_div", [trace1, trace2, trace3, trace4, trace5], layout);
}

function unpack(rows, key) {
	return rows.map(function(row) { return row[key]; });
}

function plot1(data) {
	plot_2bars(
		unpack(data,0), //park
		'Copy Speed (kB/s)',
		unpack(data,2), //copy_speed
		'Scan Speed (files/s)',
		unpack(data,1), // scan_speed
		"Park Speed Comparison (single night)"
	)
}

function plot2(data) {
	plot_2bars(
		unpack(data,0), //park
		'Scan Speed (files/s)',
		unpack(data,1), // avg scan speed
		'# of days',
		unpack(data,2), // # of days
		"Average Scan Speed by Park (last 90 days)"
	)
}

function plot3(data) {
	plot_2bars(
		unpack(data,0), //park
		'Copy Speed (kB/s)',
		unpack(data,1), // avg copy speed
		'# of days',
		unpack(data,2), // # of days
		"Average Copy Speed by Park (last 90 days)"
	)
}

function plot4(data) {
	park = data[0][0];
	title = "Historic Speeds for " + park
	plot_2lines(
		// data 0 has the park name
		unpack(data,1),
		'Scan Speed (files/s)',
		unpack(data,2),
		'Copy Speed (kB/s)',
		unpack(data,3),
		title
	)
}

function plot4a(data) {
	park = data[0][0];
	title = "Historic speeds for " + park
	plot_5lines(
		// data 0 has the park name
		unpack(data,1),
		'Scan Speed (files/s)',
		unpack(data,2),
		'Copy Speed (kB/s)',
		unpack(data,3),
		'Avg Size of File (kB)',
		unpack(data,4),
		'Copy Size (files)',
		unpack(data,5),
		'Copy Size (MBytes)',
		unpack(data,6),
		title
	)
}

function get_plot_data_fail(err) {
	console.log(err)
}

function get_last_night() {
	today = new Date()
	today.setDate(today.getDate() - 1)  //yesterday
	date = today.toISOString().substring(0,10)
	return date;
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

function plot_parks1() {
	var date = document.getElementById('page_date').textContent;
	var url = '//inpakrovmais:8080/plot1?date=' + date;
	getJSON(url, plot1, get_plot_data_fail)
}

function plot_parks2() {
	var url = '//localhost:8080/scanavg?date=2018-09-01';
	getJSON(url, plot2, get_plot_data_fail)
}

function plot_parks3() {
	var url = '//localhost:8080/copyavg?date=2018-09-01';
	getJSON(url, plot3, get_plot_data_fail)
}

function plot_parks4() {
	var url = '//localhost:8080/speed?park=YUGA&start=2018-07-01&end=2018-11-01';
	getJSON(url, plot4, get_plot_data_fail)
}

// Get data from the services and update the page
function setup_page() {
	var last_night = get_last_night();
	var first_night = '2018-01-22'
	let params = new URLSearchParams(document.location.search.substring(1));
	let date = params.get("date");
	if (!is_valid_date(date, first_night, last_night)) {
		//TODO: show error, hide everything else and add 'goto last night' button
		date = last_night
	}
	query = '?date=' + date;
	fix_date_button_state(date, first_night, last_night);
	getJSON('//inpakrovmais:8080/summary' + query, post_summary, summary_failed)
	getJSON('//inpakrovmais:8080/parks' + query, post_park_details, parks_failed)
}

setup_page();
