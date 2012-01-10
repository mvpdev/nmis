//FacilitySelector will probably end up in the NMIS object like all the other modules.

+function facilitiesDisplay(){
    var lgaData = NMIS.DataLoader.fetch("/facilities/site/" + lgaUniqueSlug);
	var variableData = NMIS.DataLoader.fetch("/facility_variables");
    function loadFacilities() {
	    var params = {};
        if((""+window.location.search).match(/facility=(\d+)/)) {
            params.facilityId = (""+window.location.search).match(/facility=(\d+)/)[1];
        }
        $('#conditional-content').hide();
	    _.each(this.params, function(param, pname){
	        if($.type(param)==="string" && param !== '') {
	            params[pname] = param.replace('/', '');
	        }
	    });
        if(params.sector === 'overview') {
            params.sector = undefined;
        }
	    prepFacilities(params);
	    $.when(lgaData, variableData)
    		.done(function(req1, req2){
    		    var lgaData = req1[0];
                var variableData = req2[0];
                launchFacilities(lgaData, variableData, params);
    		});
	}
	dashboard.get("/nmis~/:state/:lga/facilities/?(#.*)?", loadFacilities);
	dashboard.get("/nmis~/:state/:lga/facilities/:sector/?(#.*)?", loadFacilities);
    dashboard.get("/nmis~/:state/:lga/facilities/:sector/:subsector/?(#.*)?", loadFacilities);
    dashboard.get("/nmis~/:state/:lga/facilities/:sector/:subsector/:indicator/?(#.*)?", loadFacilities);
}();

function prepBreadcrumbValues(e, keys, env){
    var i, l, key, val, name, arr = [];
    for(i=0, l=keys.length; i < l; i++) {
        key = keys[i];
        val = e[key];
        if(val !== undefined) {
            name = val.name || val.slug || val;
            env[key] = val;
            arr.push([name, NMIS.urlFor(env)])
        } else {
            return arr;
        }
    }
    return arr;
}

function prepFacilities(params) {
    NMIS.DisplayWindow.setVisibility(true);
    var facilitiesMode = {name:"Facility Detail", slug:"facilities"};
	var e = {
	    state: state,
	    lga: lga,
	    mode: facilitiesMode,
	    sector: NMIS.Sectors.pluck(params.sector),
	};
	e.subsector = e.sector.getSubsector(params.subsector);
	e.indicator = e.sector.getIndicator(params.indicator);
    var bcValues = prepBreadcrumbValues(e,
                    "state lga mode sector subsector indicator".split(" "),
                    {state:state,lga:lga});
    NMIS.LocalNav.markActive(["mode:facilities", "sector:" + e.sector.slug]);
    NMIS.Breadcrumb.clear();
	NMIS.Breadcrumb.setLevels(bcValues);
    NMIS.LocalNav.iterate(function(sectionType, buttonName, a){
        var env = _.extend({}, e, {subsector: false});
        env[sectionType] = buttonName;
        a.attr('href', NMIS.urlFor(env));
    });
}

function launchFacilities(lgaData, variableData, params) {
    if(lgaData.profileData===undefined) { lgaData.profileData = {}; }
    if(lgaData.profileData.gps === undefined) {
        lgaData.profileData.gps = {
            value: "40.809587 -73.953223 183.0 4.0"
        };
    }
	var facilities = lgaData.facilities;
	var sectors = variableData.sectors;
	var sector = NMIS.Sectors.pluck(params.sector)
	var e = {
	    state: state.slug,
        lga: lga.slug,
        mode: 'facilities',
	    sector: sector,
	    subsector: sector.getSubsector(params.subsector),
	    indicator: sector.getIndicator(params.indicator),
	    facilityId: params.facilityId
	};
	NMIS.Env(e);
	NMIS.activeSector(sector);
	NMIS.loadFacilities(facilities);
	if(e.sector !== undefined && e.subsector === undefined) {
	    e.subsector = _.first(e.sector.subGroups());
	    e.subsectorUndefined = true;
	}

    var MapMgr_opts = {
        llString: lgaData.profileData.gps.value,
        elem: wElems.elem0
    };
	if(!NMIS.MapMgr.init(MapMgr_opts)) {
	    NMIS.MapMgr.addLoadCallback(function(){
            var map = new google.maps.Map(this.elem.get(0), {
                zoom: 8,
                center: new google.maps.LatLng(this.ll.lat, this.ll.lng),
                streetViewControl: false,
                panControl: false,
                mapTypeControlOptions: {
                    mapTypeIds: ["roadmap", "satellite", "terrain", "OSM"]
                },
                mapTypeId: google.maps.MapTypeId[this.defaultMapType]
            });
            // OSM google maps layer code from:
            // http://wiki.openstreetmap.org/wiki/Google_Maps_Example#Example_Using_Google_Maps_API_V3
            map.mapTypes.set("OSM", new google.maps.ImageMapType({
                getTileUrl: function(coord, zoom) {
                    return "http://tile.openstreetmap.org/" + zoom + "/" + coord.x + "/" + coord.y + ".png";
                },
                tileSize: new google.maps.Size(256, 256),
                name: "OSM",
                maxZoom: 18
            }));

            this.map = map;
            var bounds = new google.maps.LatLngBounds();
            function iconURL(slug, status) {
                var iconFiles = {
                    education: "education.png",
                    health: "health.png",
                    water: "water.png",
                    'default': "book_green_wb.png"
                };
                var url = "/static/images/icons_f/" + status + "_" + (iconFiles[slug] || iconFiles['default']);
                return url
            }
            function iconURLData(slug, status) {
                return [iconURL(slug, status), 32, 24];
            }
            function markerClick(){
                var sslug = NMIS.activeSector().slug;
                if(sslug==this.nmis.item.sector.slug || sslug === "overview") {
                    dashboard.setLocation(NMIS.urlFor(_.extend(e, {
                        facilityId: this.nmis.id
                    })));
                }
            }
            function markerMouseover() {
                var sslug = NMIS.activeSector().slug;
                if(this.nmis.item.sector.slug === sslug || sslug === "overview") {
                    NMIS.FacilityHover.show(this);
                }
            }
            function markerMouseout() {
                NMIS.FacilityHover.hide();
            }
            function mapClick() {
                if(NMIS.FacilitySelector.isActive()) {
                    NMIS.FacilitySelector.deselect();
                    dashboard.setLocation(NMIS.urlFor(_.extend(e, {
                        facilityId: false
                    })));
                }
            }
            google.maps.event.addListener(map, 'click', mapClick);
            NMIS.IconSwitcher.setCallback('createMapItem', function(item, id, itemList){
                if(!!item._ll && !this.mapItem(id)) {
                    var $gm = google.maps;
                    var iconData = (function iconDataForItem(i){
                        i.iconSlug = i.iconType || i.sector.slug;
                        var td = iconURLData(i.iconSlug, i.status || "normal");
                        return {
                            url: td[0],
                            size: new $gm.Size(td[1], td[2])
                        };
                    })(item);
                    var mI = {
                        latlng: new $gm
                                    .LatLng(item._ll[0], item._ll[1]),
                        icon: new $gm
                                    .MarkerImage(iconData.url, iconData.size)
                    };
                    mI.marker = new $gm
                                    .Marker({
                                        position: mI.latlng,
                                        map: map,
                                        icon: mI.icon
                                    });
                    mI.marker.setZIndex(item.status === "normal" ? 99: 11);
                    mI.marker.nmis = {
                        item: item,
                        id: id
                    };
                    google.maps.event.addListener(mI.marker, 'click', markerClick);
                    google.maps.event.addListener(mI.marker, 'mouseover', markerMouseover);
                    google.maps.event.addListener(mI.marker, 'mouseout', markerMouseout);
                    bounds.extend(mI.latlng);
                    this.mapItem(id, mI);
                }
            });
            NMIS.IconSwitcher.createAll();
            map.fitBounds(bounds);
            NMIS.IconSwitcher.setCallback('shiftMapItemStatus', function(item, id){
                var mapItem = this.mapItem(id);
                if(!!mapItem) {
                    var icon = mapItem.marker.getIcon();
                    icon.url = iconURL(item.sector.slug, item.status);
                    mapItem.marker.setIcon(icon);
                }
            });
	    });
	}

	if(e.sector.slug==='overview') {
	    wElems.elem1content.empty();
	    NMIS.DisplayWindow.setTempSize("minimized", true);
        var displayTitle = "Facility Detail: "+lga.name+" Overview";
        NMIS.DisplayWindow.setTitle(displayTitle);
        NMIS.IconSwitcher.shiftStatus(function(id, item) {
            return "normal";
        });
    } else {
        if(!!e.subsectorUndefined || !NMIS.FacilitySelector.isActive()) {
            NMIS.IconSwitcher.shiftStatus(function(id, item) {
                return item.sector === e.sector ? "normal" : "background";
            });
        }
        var displayTitle = "Facility Detail: "+lga.name+" " + e.sector.name;
        if(!!e.subsector) {
            NMIS.DisplayWindow.setTitle(displayTitle, displayTitle + " - " + e.subsector.name);
        }
        NMIS.DisplayWindow.unsetTempSize(true);
        var tableElem = FacilityTables.createForSectors([e.sector.slug], {
            callback: function(div){
                var pageTitle = $('<h1 />')
                            .addClass('facilities-content-title')
                            .hide()
                            .text(displayTitle);
                div.prepend(pageTitle);
                NMIS.DisplayWindow.addTitle('tables', pageTitle);
            },
            sectorCallback: function(sector, div, createNav, odiv) {
                createNav(sector, function(sg){
                    return NMIS.urlFor({
                        state: state.slug,
                        lga: lga.slug,
                        mode: 'facilities',
                        sector: sector.slug,
                        subsector: sg.slug
                    });
                }).prependTo(div);
            },
            indicatorClickCallback: function() {
                if(!!this.clickable) {
                    var clickUrl = NMIS.urlFor(_.extend({}, e, {
                        indicator: this.slug
                    }));
                    dashboard.setLocation(clickUrl);
                }
            }
        });
        tableElem.find('tbody').delegate('tr', 'click', function(){
            dashboard.setLocation(NMIS.urlFor(_.extend(e, {
                facilityId: $(this).data('facilityId')
            })));
        });
        tableElem.appendTo(wElems.elem1content);
        if(!!e.subsector) FacilityTables.select(e.sector, e.subsector);
        if(!!e.indicator) (function(){
            $('.indicator-feature').remove();
            var obj = _.extend({}, e.indicator);
            var mm = $(mustachify('indicator-feature', obj));
            mm.find('a.close').click(function(){
                var xx = NMIS.urlFor(_.extend({}, e, {indicator: false}));
                dashboard.setLocation(xx);
                return false;
            });
            (function(rcElem, rtElem){
                var r = Raphael(rcElem),
                    r2 = Raphael(rtElem);
                r.g.txtattr.font = "12px 'Fontin Sans', Fontin-Sans, sans-serif";
                var pie = r.g.piechart(35, 35, 34, [22,5], {"colors":["#21c406","#ff5555"]});
                $(rtElem).css({'height':'45px'});
/*                var pieText = r2.g.piechart(40, 120, 20, [22, 5],
                        {"colors":["#21c406","#ff5555"],"legend":["%% - Yes (##)","%% - No (##)"],"legendpos":"west"}); */
            })(mm.find('.raph-circle').get(0), mm.find('.raph-legend').get(0));
            mm.prependTo('.facility-display');
            FacilityTables.highlightColumn(e.indicator);
        })();
	}
	if(!!e.facilityId) {
	    NMIS.FacilitySelector.activate({
	        id: e.facilityId
	    });
	}
}
function mustachify(id, obj) {
    return Mustache.to_html($('#'+id).eq(0).html().replace(/<{/g, '{{').replace(/\}>/g, '}}'), obj);
}