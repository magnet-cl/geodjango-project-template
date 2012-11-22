{% load l10n %}

{% block vars %}var {{ module }} = {};
{{ module }}.map = null; {{ module }}.controls = null; {{ module }}.panel = null; {{ module }}.re = new RegExp("^SRID=\\d+;(.+)", "i"); {{ module }}.layers = {};
{{ module }}.modifiable = {{ modifiable|yesno:"true,false" }};
{{ module }}.wkt_f = new OpenLayers.Format.WKT();
{{ module }}.is_collection = {{ is_collection|yesno:"true,false" }};
{{ module }}.collection_type = '{{ collection_type }}';
{{ module }}.is_linestring = {{ is_linestring|yesno:"true,false" }};
{{ module }}.is_polygon = {{ is_polygon|yesno:"true,false" }};
{{ module }}.is_point = {{ is_point|yesno:"true,false" }};
{% endblock %}
{{ module }}.get_ewkt = function(feat){return 'SRID={{ srid }};' + {{ module }}.wkt_f.write(feat);}
{{ module }}.read_wkt = function(wkt){
  // OpenLayers cannot handle EWKT -- we make sure to strip it out.
  // EWKT is only exposed to OL if there's a validation error in the admin.
  var match = {{ module }}.re.exec(wkt);
  if (match){wkt = match[1];}
  return {{ module }}.wkt_f.read(wkt);
}
{{ module }}.write_wkt = function(feat){
  if ({{ module }}.is_collection){ {{ module }}.num_geom = feat.geometry.components.length;}
  else { {{ module }}.num_geom = 1;}
  document.getElementById('{{ id }}').value = {{ module }}.get_ewkt(feat);
}
{{ module }}.add_wkt = function(event){
  // This function will sync the contents of the `vector` layer with the
  // WKT in the text field.
  if ({{ module }}.is_collection){
    var feat = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.{{ geom_type }}());
    for (var i = 0; i < {{ module }}.layers.vector.features.length; i++){
      feat.geometry.addComponents([{{ module }}.layers.vector.features[i].geometry]);
    }
    {{ module }}.write_wkt(feat);
  } else {
    // Make sure to remove any previously added features.
    if ({{ module }}.layers.vector.features.length > 1){
      old_feats = [{{ module }}.layers.vector.features[0]];
      {{ module }}.layers.vector.removeFeatures(old_feats);
      {{ module }}.layers.vector.destroyFeatures(old_feats);
    }
    {{ module }}.write_wkt(event.feature);
  }
}
{{ module }}.modify_wkt = function(event){
  if ({{ module }}.is_collection){
    if ({{ module }}.is_point){
      {{ module }}.add_wkt(event);
      return;
    } else {
      // When modifying the selected components are added to the
      // vector layer so we only increment to the `num_geom` value.
      var feat = new OpenLayers.Feature.Vector(new OpenLayers.Geometry.{{ geom_type }}());
      for (var i = 0; i < {{ module }}.num_geom; i++){
	feat.geometry.addComponents([{{ module }}.layers.vector.features[i].geometry]);
      }
      {{ module }}.write_wkt(feat);
    }
  } else {
    {{ module }}.write_wkt(event.feature);
  }
}
// Function to clear vector features and purge wkt from div
{{ module }}.deleteFeatures = function(){
  {{ module }}.layers.vector.removeFeatures({{ module }}.layers.vector.features);
  {{ module }}.layers.vector.destroyFeatures();
}
{{ module }}.clearFeatures = function (){
  {{ module }}.deleteFeatures();
  document.getElementById('{{ id }}').value = '';
  {% localize off %}
  {{ module }}.map.setCenter(new OpenLayers.LonLat({{ default_lon }}, {{ default_lat }}), {{ default_zoom }});
  {% endlocalize %}
}
// Add Select control
{{ module }}.addSelectControl = function(){
  var select = new OpenLayers.Control.SelectFeature({{ module }}.layers.vector, {'toggle' : true, 'clickout' : true});
  {{ module }}.map.addControl(select);
  select.activate();
}
{{ module }}.enableDrawing = function(){ {{ module }}.map.getControlsByClass('OpenLayers.Control.DrawFeature')[0].activate();}
{{ module }}.enableEditing = function(){ {{ module }}.map.getControlsByClass('OpenLayers.Control.ModifyFeature')[0].activate();}
// Create an array of controls based on geometry type
{{ module }}.getControls = function(lyr){
  {{ module }}.panel = new OpenLayers.Control.Panel({'displayClass': 'olControlEditingToolbar'});
  var nav = new OpenLayers.Control.Navigation();
  var draw_ctl;
  if ({{ module }}.is_linestring){
    draw_ctl = new OpenLayers.Control.DrawFeature(lyr, OpenLayers.Handler.Path, {'displayClass': 'olControlDrawFeaturePath'});
  } else if ({{ module }}.is_polygon){
    draw_ctl = new OpenLayers.Control.DrawFeature(lyr, OpenLayers.Handler.Polygon, {'displayClass': 'olControlDrawFeaturePolygon'});
  } else if ({{ module }}.is_point){
    draw_ctl = new OpenLayers.Control.DrawFeature(lyr, OpenLayers.Handler.Point, {'displayClass': 'olControlDrawFeaturePoint'});
  }
  if ({{ module }}.modifiable){
    var mod = new OpenLayers.Control.ModifyFeature(lyr, {'displayClass': 'olControlModifyFeature'});
    {{ module }}.controls = [nav, draw_ctl, mod];
  } else {
    if(!lyr.features.length){
      {{ module }}.controls = [nav, draw_ctl];
    } else {
      {{ module }}.controls = [nav];
    }
  }
}

{{ module }}.init = function(){
    var position;

    var wkt = document.getElementById('{{ id }}').value;
    if (wkt){
      // After reading into geometry, immediately write back to
      // WKT <textarea> as EWKT (so that SRID is included).
      var admin_geom = {{ module }}.read_wkt(wkt);
      {{ module }}.write_wkt(admin_geom);

      position =  new google.maps.LatLng(
          admin_geom.geometry.y, admin_geom.geometry.x);
    }
    else{
      position = new google.maps.LatLng({{ default_lon }}, {{ default_lat }});
    }

    // The options hash, w/ zoom, resolution, and projection settings.
    {% block map_options %}
    var options = {
      zoom: {{point_zoom}},
      center: position,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };{% endblock %}

    // The admin map for this geometry field.
    {{ module }}.map = new google.maps.Map(
        document.getElementById('{{ id }}_map'), options);

    var marker = new google.maps.Marker({
        position: position,
        map: {{ module }}.map,
        title: "Marker"
    });


    // This allows editing of the geographic fields -- the modified WKT is
    // written back to the content field (as EWKT, so that the ORM will know
    // to transform back to original SRID).
    google.maps.event.addListener({{ module }}.map, 'click', function(event){
      marker.setPosition(event.latLng);
      debugger;
      var admin_geom = {{ module }}.read_wkt(
        'Point(' + event.latLng.lng() + ' ' + event.latLng.lat() +')');
      {{ module }}.write_wkt(admin_geom);
    });
}
