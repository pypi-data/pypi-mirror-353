(function() {

var eveProjection = new ol.proj.Projection({
	code: 'EVE:SYS',
	units: 'm',
	extent: [-1000000000000000000, -1000000000000000000, 1000000000000000000, 1000000000000000000],
	global: false,
	metersPerUnit: 1
});
ol.proj.addProjection(eveProjection);

// point colour
function getColorForValue(value) {

	if (value > 0.9) {
		return '#2e74dc';
	} else if (value > 0.8) {
		return '#389cf3';
	} else if (value > 0.7) {
		return '#4acff2';
	} else if (value > 0.6) {
		return '#60daa6';
	} else if (value > 0.5) {
		return '#71e452';
	} else if (value > 0.4) {
		return '#eeff83';
	} else if (value > 0.3) {
		return '#e16a0b';
	} else if (value > 0.2) {
		return '#d1440d';
	} else if (value > 0.1) {
		return '#bc1114';
	} else if (value > 0.0) {
		return '#6d2122';
	} else {
		return '#8f2f69';
	}
  }

  const pointStyleFunction = function(feature, resolution) {
	const attr = feature.get('security_status');
	const fillColor = getColorForValue(attr);
	const zoom = map.getView().getZoom();
	const radius = 0 + (zoom * 0.6);

	return new ol.style.Style({
	  image: new ol.style.Circle({
		radius: radius,
		fill: new ol.style.Fill({ color: fillColor }),
	  }),
	});
  };

var solarSystemsLayer = new ol.layer.Vector({
	source: new ol.source.Vector({
		url: '/evemap/solar_systems_geojson',
		format: new ol.format.GeoJSON()
	}),
	style: pointStyleFunction
});

var map = new ol.Map({
	target: 'map',
	layers: [solarSystemsLayer],
	view: new ol.View({
		projection: eveProjection,
		center: [0, 0],
		zoom: 1
	})
});

var popup = document.getElementById('popup');
map.on('singleclick', function(evt) {
	var feature = map.forEachFeatureAtPixel(evt.pixel, function(feat) {
		return feat;
	});
	if (feature) {
		var props = feature.getProperties();
		delete props.geometry;
		popup.innerHTML = 'name: ' + props.name + '<br />';
		popup.innerHTML += 'Security Status: ' + props.security_status.toFixed(3) + '<br />';
		popup.style.display = 'block';
		var coordinate = evt.coordinate;
		var pixel = map.getPixelFromCoordinate(coordinate);
		popup.style.left = (pixel[0]) + 'px';
		popup.style.top = (pixel[1]) + 'px';
	} else {
		popup.style.display = 'none';
	}
});

})();
