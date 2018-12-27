const data_server = '//inpakrovmais:8080'
//const data_server = '//localhost:8080'
// NOTE: all dates in this code are ISO formated date strings (YYYY-MM-DD) in local time.
//      in the few cases where a javascript date object is needed it is called dateObj

const data_server = '//localhost:8080'

// Return bytes as human readable quantity
// Credit: https://stackoverflow.com/a/14919494
function humanFileSize (bytes, si) {
  var thresh = si ? 1000 : 1024
  if (Math.abs(bytes) < thresh) {
    return bytes + ' Bytes'
  }
  var units = si
    ? ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    : ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
  var u = -1
  do {
    bytes /= thresh
    ++u
  } while (Math.abs(bytes) >= thresh && u < units.length - 1)
  return bytes.toFixed(1) + ' ' + units[u]
}

// rounds a number to a specified number of decimal digits
// credit: http://www.jacklmoore.com/notes/rounding-in-javascript/
function round (value, decimals) {
  return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals)
}

// Adds or updates the parameter in a query string
// credit: https://stackoverflow.com/a/11654596
function UpdateQueryString (key, value, url) {
  if (!url) url = window.location.href
  var re = new RegExp('([?&])' + key + '=.*?(&|#|$)(.*)', 'gi'),
    hash

  if (re.test(url)) {
    if (typeof value !== 'undefined' && value !== null)
      return url.replace(re, '$1' + key + '=' + value + '$2$3')
    else {
      hash = url.split('#')
      url = hash[0].replace(re, '$1$3').replace(/(&|\?)$/, '')
      if (typeof hash[1] !== 'undefined' && hash[1] !== null)
        url += '#' + hash[1]
      return url
    }
  } else {
    if (typeof value !== 'undefined' && value !== null) {
      var separator = url.indexOf('?') !== -1 ? '&' : '?'
      hash = url.split('#')
      url = hash[0] + separator + key + '=' + value
      if (typeof hash[1] !== 'undefined' && hash[1] !== null)
        url += '#' + hash[1]
      return url
    } else return url
  }
}

// Left pad a number to two digits with a zero
function pad2 (n) {
  return n < 10 ? '0' + n : n
}

// Produce a short ISO formated date from a date object
function isoDateFormat (dateObj) {
  return (
    dateObj.getFullYear() +
    '-' +
    pad2(dateObj.getMonth() + 1) +
    '-' +
    pad2(dateObj.getDate())
  )
}

// Produce a date object from a short ISO formated date
// It is flexible in that zero padding is not required, and month/day default to Jan/1
// an invalid date will result in today's date being returned
function dateFromIso (str) {
  if (!str) {
    return new Date()
  }
  try {
    const parts = str.split('-')
    const year = parts[0]
    const month = (parts[1] || 1) - 1
    const day = parts[2] || 1
    const dateObj = new Date(year, month, day)
    if (dateObj instanceof Date && !isNaN(dateObj)) {
      return dateObj
    } else {
      return new Date()
    }
  } catch (error) {
    return new Date()
  }
}

// Validate a user provided iso date string
// if date is null then the current date will be assumed
// if date is outside range, then it will be clipped to the range
// Range is open, i.e. minDate and maxDate are allowed, if null then no limit
function validateDate (date, minDate, maxDate) {
  const dateObj = dateFromIso(date)
  const newDate = isoDateFormat(dateObj)
  if (minDate && newDate < minDate) {
    return minDate
  }
  if (maxDate && maxDate < newDate) {
    return maxDate
  }
  return newDate
}

// Returns an ISO format date for yesterday (presumably the last time robo ran)
function getYesterday () {
  const dateObj = new Date()
  dateObj.setDate(dateObj.getDate() - 1) // yesterday
  return isoDateFormat(dateObj)
}

// generic request to get JSON data from data service
function getJSON (url, callback, errorback) {
  const xhr = new XMLHttpRequest()
  xhr.open('GET', url, true)
  xhr.responseType = 'json'
  xhr.onload = function () {
    if (this.readyState == this.DONE) {
      if (this.status == 200) {
        if (this.response !== null) {
          callback(this.response)
        } else {
          errorback('Bad JSON object returned from Server')
        }
      } else {
        errorback(this.statusText)
      }
    }
  }
  xhr.onerror = function (e) {
    errorback('Error fetching data for report. Check if service is running.')
  }
  xhr.send()
}

// Success callback for adding summary data to the web page
function post_summary (data) {
  document.getElementById('summary_wait').hidden = true
  if (Object.keys(data).length === 0 && data.constructor === Object) {
    document.getElementById('summary_fail').hidden = false
    return
  }
  const date = data['summary_date']
  const count_starts = data['count_start']
  const count_unfinished = data['count_unfinished']
  const count_errors = data['count_with_errors']
  const has_changes = data['has_changes']
  const issues = count_errors > 0 || count_unfinished > 0

  const count_ele = document.getElementById('count_total_parks')
  if (count_starts == 0) {
    count_ele.textContent = 'no parks'
  } else if (count_starts > 1) {
    count_ele.textContent = count_starts + ' parks'
  }
  // case of "1 Park" is the default in the html

  if (count_unfinished > 1) {
    document.getElementById('summary_incomplete_count').textContent =
      count_unfinished + ' parks'
  }
  document.getElementById('summary_incomplete').hidden = count_unfinished == 0

  if (count_errors > 1) {
    document.getElementById('summary_errors_count').textContent =
      count_errors + ' parks'
  }
  document.getElementById('summary_errors').hidden = count_errors == 0

  if (issues) {
    document.getElementById('summary_issues').hidden = false
    document.getElementById('summary_no_issues').hidden = true
    if (count_errors == 0) {
      document
        .getElementById('summary_card')
        .classList.replace('nominal', 'warning')
    } else {
      document
        .getElementById('summary_card')
        .classList.replace('nominal', 'error')
    }
  } else {
    document.getElementById('summary_issues').hidden = true
    document.getElementById('summary_no_issues').hidden = false
  }

  if (has_changes) {
    document.getElementById('summary_changes').hidden = false
    document.getElementById('summary_no_changes').hidden = true
    document.getElementById('changelog_link').href =
      'PDS_ChangeLog.html#' + date
  } else {
    document.getElementById('summary_changes').hidden = true
    document.getElementById('summary_no_changes').hidden = false
  }
  document.getElementById('summary_card').hidden = false
}

// Success callback for adding park details to the web page
function post_park_details (data) {
  if (data.length === 1) {
    document.getElementById('park_wait').hidden = true
    document.getElementById('park_fail').hidden = false
    return
  }
  // ["park","date","finished","count_errors","files_copied","files_removed","files_scanned","time_copying","time_scanning","bytes_copied"]
  // Ignore the first row (header), assume there are no more then 20 parks
  let html = ''
  data.slice(1, 20).forEach(row => {
    const park = row[0]
    const date = row[1]
    const bytes_copied = row[9]
    const size_copied = humanFileSize(bytes_copied, true)
    const time_copying = row[7]
    const copy_speed = round(bytes_copied / time_copying / 1000.0, 1)
    let copy_text =
      time_copying == 0
        ? 'Nothing copied.'
        : `${size_copied} in ${time_copying} seconds (${copy_speed} kB/sec)`
    copy_text = time_copying == null ? 'Unknown' : copy_text
    const files_scanned = row[6]
    const time_scanning = row[8]
    const scan_speed = round(files_scanned / time_scanning, 1)
    const files_removed = row[5]
    const finished = row[2]
    const count_errors = row[3]
    const status =
      count_errors == 0 ? (finished == 1 ? 'nominal' : 'warning') : 'error'
    const error_str = count_errors == 0 ? '' : `${count_errors} Errors.`
    const finish_str =
      finished == 1 ? '' : 'Robocopy did not finish (no timing data).'
    let issues = 'No Issues.'
    if (error_str == '' && finish_str != '') {
      issues = finish_str
    } else if (error_str != '' && finish_str == '') {
      issues = error_str
    } else if (error_str != '' && finish_str != '') {
      issues = error_str + ' ' + finish_str
    }
    const scan_text =
      files_scanned == null
        ? 'Unknown'
        : `${files_scanned} files in ${time_scanning} seconds (${scan_speed} files/sec)`
    const removed_text =
      files_removed == null ? 'Unknown' : `${files_removed} files`
    const card_str = `
      <div class='card ${status} inline'>
        <h3>${park}</h3>
        <dt>Copied</dt>
        <dd>${copy_text}</dd>
        <dt>Scanned</dt>
        <dd>${scan_text}</dd>
        <dt>Removed</dt>
        <dd>${removed_text}</dd>
        <dt>Issues</dt>
        <dd>${issues}</dd>
        <a href='${data_server}/logfile?park=${park}&date=${date}'>Log file</a>
      </div>
    `
    html += card_str
  })
  document.getElementById('park_cards').innerHTML = html
  document.getElementById('park_wait').hidden = true
  document.getElementById('park_cards').hidden = false
}

// Error callback for adding summary error to the web page
function summary_failed (message) {
  const ele = document.getElementById('summary_fail')
  if (message == 'Service Unavailable') {
    const message2 = 'Check to make sure the python service is running.'
    ele.textContent = message + '. ' + message2
  } else {
    ele.textContent = message
  }
  ele.hidden = false
  document.getElementById('summary_wait').hidden = true
}

// Error callback for adding park details error to the web page
function parks_failed (message) {
  const ele = document.getElementById('park_fail')
  ele.textContent = message
  ele.hidden = false
  document.getElementById('park_wait').hidden = true
}

// Update the state of the date text and the next/previous date buttons
function fix_date_button_state (date) {
  const previous_button = document.getElementById('previous_date')
  const next_button = document.getElementById('next_date')

  // Use a javascript date object because it makes date math much easier
  //   getDate and setDate get/set the day of the month
  //   setDate will roll up/down a month/year as needed if the new day is out of range
  let dateObj = dateFromIso(date)
  dateObj.setDate(dateObj.getDate() + 1) // Add one day to the date
  next_button.dataset.destination = isoDateFormat(dateObj)
  dateObj = dateFromIso(date)
  dateObj.setDate(dateObj.getDate() - 1) // Subtract one day to the date
  previous_button.dataset.destination = isoDateFormat(dateObj)

  previous_button.hidden = date <= previous_button.dataset.limit
  next_button.hidden = next_button.dataset.limit <= date
}

function plot_2bars (x, l1, y1, l2, y2, title) {
  const trace1 = {
    x: x,
    y: y1,
    name: l1,
    type: 'bar'
  }

  const trace2 = {
    x: x,
    y: y2,
    name: l2,
    type: 'bar'
  }
  const layout = {
    barmode: 'group',
    title: title
  }
  Plotly.newPlot('graph_div', [trace1, trace2], layout)
}

function plot_2lines (x, l1, y1, l2, y2, title) {
  const trace1 = {
    x: x,
    y: y1,
    name: l1,
    type: 'scatter',
    mode: 'lines'
  }
  const trace2 = {
    x: x,
    y: y2,
    name: l2,
    type: 'scatter',
    mode: 'lines'
  }
  const layout = {
    title: title
  }
  Plotly.newPlot('graph_div', [trace1, trace2], layout)
}

function plot_5lines (x, l1, y1, l2, y2, l3, y3, l4, y4, l5, y5, title) {
  const trace1 = {
    x: x,
    y: y1,
    name: l1,
    type: 'scatter',
    mode: 'lines'
  }
  const trace2 = {
    x: x,
    y: y2,
    name: l2,
    type: 'scatter',
    mode: 'lines'
  }
  const trace3 = {
    x: x,
    y: y3,
    name: l3,
    type: 'scatter',
    mode: 'lines'
  }
  const trace4 = {
    x: x,
    y: y4,
    name: l4,
    type: 'scatter',
    mode: 'lines'
  }
  const trace5 = {
    x: x,
    y: y5,
    name: l5,
    type: 'scatter',
    mode: 'lines'
  }
  const layout = {
    title: title
  }
  Plotly.newPlot('graph_div', [trace1, trace2, trace3, trace4, trace5], layout)
}

function unpack (rows, key) {
  return rows.map(function (row) {
    return row[key]
  })
}

function plot1 (data) {
  if (data.length < 2) {
    get_plot_data_fail('No plot data for this date.')
    return
  }
  document.getElementById('graph_wait').hidden = true
  document.getElementById('graph_div').hidden = false
  plot_2bars(
    unpack(data, 0), // park
    'Copy Speed (kB/s)',
    unpack(data, 2), // copy_speed
    'Scan Speed (files/s)',
    unpack(data, 1), // scan_speed
    'Park Speed Comparison (single night)'
  )
}

function plot2 (data) {
  document.getElementById('graph_wait').hidden = true
  document.getElementById('graph_div').hidden = false
  plot_2bars(
    unpack(data, 0), // park
    'Scan Speed (files/s)',
    unpack(data, 1), // avg scan speed
    '# of days',
    unpack(data, 2), // # of days
    'Average Scan Speed by Park (last 90 days)'
  )
}

function plot3 (data) {
  document.getElementById('graph_wait').hidden = true
  document.getElementById('graph_div').hidden = false
  plot_2bars(
    unpack(data, 0), // park
    'Copy Speed (kB/s)',
    unpack(data, 1), // avg copy speed
    '# of days',
    unpack(data, 2), // # of days
    'Average Copy Speed by Park (last 90 days)'
  )
}

function plot4 (data) {
  document.getElementById('graph_wait').hidden = true
  document.getElementById('graph_div').hidden = false
  const park = data[0][0]
  const title = 'Historic Speeds for ' + park
  plot_2lines(
    // data 0 has the park name
    unpack(data, 1),
    'Scan Speed (files/s)',
    unpack(data, 2),
    'Copy Speed (kB/s)',
    unpack(data, 3),
    title
  )
}

function plot4a (data) {
  document.getElementById('graph_wait').hidden = true
  document.getElementById('graph_div').hidden = false
  const park = data[0][0]
  const title = 'Historic speeds for ' + park
  plot_5lines(
    // data 0 has the park name
    unpack(data, 1),
    'Scan Speed (files/s)',
    unpack(data, 2),
    'Copy Speed (kB/s)',
    unpack(data, 3),
    'Avg Size of File (kB)',
    unpack(data, 4),
    'Copy Size (files)',
    unpack(data, 5),
    'Copy Size (MBytes)',
    unpack(data, 6),
    title
  )
  document.getElementById('graph_wait').hidden = true
  document.getElementById('graph_div').hidden = false
}

function get_plot_data_fail (err) {
  const ele = document.getElementById('graph_fail')
  ele.hidden = false
  if (err) {
    ele.textContent = err
  }
  document.getElementById('graph_wait').hidden = true
}

// ===========
// DOM Events
// ===========

function next_date () {
  const new_date = document.getElementById('next_date').dataset.destination
  const url = UpdateQueryString('date', new_date)
  window.history.pushState({}, '', url)
  setup_page(new_date)
}

function previous_date () {
  const new_date = document.getElementById('previous_date').dataset.destination
  const url = UpdateQueryString('date', new_date)
  window.history.pushState({}, '', url)
  setup_page(new_date)
}

function prep_for_new_graph () {
  const graph = document.getElementById('graph_div')
  graph.hidden = true
  document.getElementById('graph_fail').hidden = true
  document.getElementById('graph_wait').hidden = false
  while (graph.firstChild) {
    graph.removeChild(graph.firstChild)
  }
}

function plot_parks1 () {
  prep_for_new_graph()
  const date = document.getElementById('page_date').textContent
  const url = data_server + '/plot1?date=' + date
  getJSON(url, plot1, get_plot_data_fail)
}

function plot_parks2 () {
  prep_for_new_graph()
  document.getElementById('graph_fail').hidden = true
  const url = data_server + '/scanavg?date=2018-09-01'
  getJSON(url, plot2, get_plot_data_fail)
}

function plot_parks3 () {
  prep_for_new_graph()
  document.getElementById('graph_fail').hidden = true
  const url = data_server + '/copyavg?date=2018-09-01'
  getJSON(url, plot3, get_plot_data_fail)
}

function plot_parks4 () {
  prep_for_new_graph()
  document.getElementById('graph_fail').hidden = true
  const url = data_server + '/speed?park=YUGA&start=2018-07-01&end=2018-11-01'
  getJSON(url, plot4, get_plot_data_fail)
}

// Get data from the services and update the page
function setup_page (date) {
  document.getElementById('page_date').textContent = date
  fix_date_button_state(date)
  const query = '?date=' + date
  document.getElementById('summary_wait').hidden = false
  document.getElementById('summary_card').hidden = true
  document.getElementById('summary_fail').hidden = true
  getJSON(data_server + '/summary' + query, post_summary, summary_failed)
  document.getElementById('park_wait').hidden = false
  document.getElementById('park_cards').hidden = true
  document.getElementById('park_fail').hidden = true
  getJSON(data_server + '/parks' + query, post_park_details, parks_failed)
}

// Get data from the services and update the page
function setup_site () {
  const last_night = getYesterday()
  const first_night = '2018-01-22'
  document.getElementById('previous_date').dataset.limit = first_night
  document.getElementById('next_date').dataset.limit = last_night
  const params = new URLSearchParams(document.location.search.substring(1))
  const date = validateDate(params.get('date'), first_night, last_night)
  setup_page(date)
}

setup_site()
