var weather = msg.payload.WeatherForecasts[0];

for (var i = 0; i < weather.forecasts.length; i++) {
    var dateObj = new Date(weather.forecasts[i].time);

    // Formatting the date object to YYYY-MM-DD HH:MM:SS format
    var formattedDate = dateObj.getFullYear() + '-' +
        ('0' + (dateObj.getMonth() + 1)).slice(-2) + '-' +
        ('0' + dateObj.getDate()).slice(-2) + ' ' +
        ('0' + dateObj.getHours()).slice(-2) + ':' +
        ('0' + dateObj.getMinutes()).slice(-2) + ':' +
        ('0' + dateObj.getSeconds()).slice(-2);
    var lat = weather.location.lat
    var lon = weather.location.lon
    var cond = weather.forecasts[i].data.cond
    var rain = weather.forecasts[i].data.rain
    var tc = weather.forecasts[i].data.tc
    var rh = weather.forecasts[i].data.rh

    msg.payload[i] = {
        time: formattedDate,
        lat: lat,
        lon: lon,
        cond: cond,
        rain: rain,
        tc: tc,
        rh: rh
    };
}

return msg;