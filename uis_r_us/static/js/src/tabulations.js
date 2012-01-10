var debugMode = true;

var NMIS = (function(){
    var data, opts;

var Breadcrumb = (function(){
    var levels = [];
    var elem;
    var context = {};

    function init(_elem, _opts) {
        elem = $(_elem).eq(0);
        var opts = _.extend({
            draw: true
        }, _opts);
        levels = _.extend(levels, (opts.levels || []));
        if(!!opts.draw) {
            draw();
        }
    }
    function clear() {
        if (elem !== undefined) {
            elem.empty();
        }
        levels = [];
    }
    function setLevels(_levels) {
        levels = _.extend(levels, (_levels || []));
        draw();
        return context;
    }
    function setLevel(ln, d) {
        levels[ln] = d;
        return context;
    }
    function draw() {
        if (elem !== undefined) {
            elem.empty();
        }
        var a;
        _.each(levels, function(level, i){
            if(i!==0) {
                $('<span />')
                    .text('/')
                    .appendTo(elem);
            }
            a = $('<a />')
                .text(level[0])
                .attr('href', level[1]);
            if(level.length > 2) { a.click(level[2]); }
            a.appendTo(elem);
        });
    }
    return {
        init: init,
        setLevels: setLevels,
        setLevel: setLevel,
        draw: draw,
        _levels: function(){return levels;},
        clear: clear
    }
})();

var MapMgr = (function(){
    var opts,
        started = false,
        finished = false,
        callbackStr = "NMIS.MapMgr.loaded";
    function init(_opts) {
        if(started) {
            return true;
        }
        //log("MapMgr initting");
        opts = _.extend({
            //defaults
            launch: true,
            fake: false,
            fakeDelay: 3000,
            mapLoadFn: function(){
                $.getScript('http://maps.googleapis.com/maps/api/js?sensor=false&callback='+callbackStr);
            },
            elem: 'body',
            defaultMapType: 'SATELLITE',
            loadCallbacks: []
        }, _opts);
        if(!opts.ll) {
            if(opts.llString) {
                var t = opts.llString.split(' ');
                opts.ll = { lat: +t[0], lng: +t[1] };
            }
        }
        started = true;
        opts.elem = $(opts.elem);
        if(!opts.fake) {
            opts.mapLoadFn();
        } else {
            _.delay(loaded, opts.fakeDelay);
        }
        return false;
    }
    function loaded() {
        //log("MapMgr has finished loading");
        finished = true;
        _.each(opts.loadCallbacks, function(cb){
            cb.call(opts);
        });
    }
    function addLoadCallback(cb) {
        opts.loadCallbacks.push(cb);
    }
    function isLoaded() {
        return finished;
    }
    function clear() {
        started = finished = false;
    }
    return {
        init: init,
        clear: clear,
        loaded: loaded,
        isLoaded: isLoaded,
        addLoadCallback: addLoadCallback
    }
})();

var S3Photos = (function(){
    var s3Root = "http://nmisstatic.s3.amazonaws.com/facimg";
    function url(s3id, size) {
        if(!size) size = "0";
        var codes = s3id.split(":");
        return [s3Root,
            codes[0],
            size,
            codes[1] + ".jpg"].join("/");
    }
    return {
        url: url
    }
})();

var HackCaps = (function(){
    function capitalize(str) {
        if(!str) {
            return "";
        } else {
            return str[0].toUpperCase() + str.slice(1);
        }
    }

    return function(str){
        return _.map(str.split("_"), capitalize).join(" ");
    }
})();

var FacilitySelector = (function(){
    var active = false;
    function activate(params){
        log(fId);
        var fId = params.id;
        NMIS.IconSwitcher.shiftStatus(function(id, item) {
            if(id !== fId) {
                return "background";
            } else {
                active = true;
                return "normal";
            }
        });
        var facility = _.find(NMIS.data(), function(val, key){
            return key==params.id;
        });
        NMIS.FacilityPopup(facility);
    }
    function isActive(){
        return active;
    }
    function deselect() {
        if(active) {
            var sector = NMIS.activeSector();
            NMIS.IconSwitcher.shiftStatus(function(id, item) {
                return item.sector === sector ? "normal" : "background";
            });
            active = false;
            dashboard.setLocation(NMIS.urlFor(NMIS.Env.extend({facilityId: false})));
        }
    }
    return {
        activate: activate,
        isActive: isActive,
        deselect: deselect
    }
})();
var FacilityHover = (function(){
    var hoverOverlayWrap,
        hoverOverlay,
        wh = 90;

    function getPixelOffset(marker, map) {
        var scale = Math.pow(2, map.getZoom());
        var nw = new google.maps.LatLng(
            map.getBounds().getNorthEast().lat(),
            map.getBounds().getSouthWest().lng()
        );
        var worldCoordinateNW = map.getProjection().fromLatLngToPoint(nw);
        var worldCoordinate = map.getProjection().fromLatLngToPoint(marker.getPosition());
        return pixelOffset = new google.maps.Point(
            Math.floor((worldCoordinate.x - worldCoordinateNW.x) * scale),
            Math.floor((worldCoordinate.y - worldCoordinateNW.y) * scale)
        );
    }
    function show(marker) {
        var map = marker.map;
        if(!hoverOverlayWrap) {
            hoverOverlayWrap = $('<div />').addClass('hover-overlay-wrap');
            hoverOverlayWrap.insertBefore(map.getDiv());
        }
        var pOffset = getPixelOffset(marker, map);
        var obj = {
            top: pOffset.y + 10,
            left: pOffset.x - 25,
            arrowLeft: 22,
            name: _getNameFromFacility(marker.nmis.item),
            community: marker.nmis.item.community,
            title: marker.nmis.id,
            img_thumb: NMIS.S3Photos.url(marker.nmis.item.s3_photo_id, 200)
        };
        hoverOverlay = $(Mustache.to_html($('#facility-hover').eq(0).html().replace(/<{/g, '{{').replace(/\}>/g, '}}'), obj));
        var img = $('<img />').load(function(){
            var $this = $(this);
            if($this.width() > $this.height()) {
                $this.width(wh);
            } else {
                $this.height(wh);
            }
            $this.css({
                marginTop: -.5*$this.height(),
                marginLeft: -.5*$this.width()
            });
        }).attr('src', NMIS.S3Photos.url(marker.nmis.item.s3_photo_id, 90));
        hoverOverlay.find('div.photothumb').html(img);
        hoverOverlayWrap.html(hoverOverlay);
    }
    function hide(delay) {
        if(!!hoverOverlay) {
            hoverOverlay.hide();
        }
    }
    return {
        show: show,
        hide: hide
    }
})();
function _getNameFromFacility(f) {
    return f.name || f.facility_name || f.school_name
}
var FacilityPopup = (function(){
    var div;
    function make(facility) {
        if(!!div) {
            div.remove();
        }
        var obj = _.extend({
            thumbnail_url: function() {
                return NMIS.S3Photos.url(this.s3_photo_id, 200);
            },
            image_url: function() {
                return NMIS.S3Photos.url(this.s3_photo_id, "0");
            },
            name: _getNameFromFacility(facility)
        }, facility);
        div = $(Mustache.to_html($('#facility-popup').eq(0).html().replace(/<{/g, '{{').replace(/\}>/g, '}}'), obj));
        div.dialog({
            width: 500,
            height: 300,
            resizable: false,
            close: function(){
                FacilitySelector.deselect();
            }
        });
        return div;
    }
    return make;
})();

var Env = (function(){
    var env = undefined;
    function EnvAccessor(arg) {
        if(arg===undefined) {
            return getEnv();
        } else {
            setEnv(arg);
        }
    }
    EnvAccessor.extend = function(o){
        return _.extend(getEnv(), o);
    }
    function setEnv(_env) {
        env = _.extend({}, _env);
    }
    function getEnv() {
        if(env === undefined) {
            throw new Error("NMIS.Env is not set");
        } else {
            return _.extend({}, env);
        }
    }
    return EnvAccessor;
})();

var Sectors = (function(){
    var sectors, defaultSector;
    function changeKey(o, key) {
        o['_' + key] = o[key];
        delete(o[key]);
        return o;
    }
    function Sector(d){
        changeKey(d, 'subgroups');
        changeKey(d, 'columns');
        changeKey(d, 'default');
        $.extend(this, d);
    }
    Sector.prototype.subGroups = function() {
        if(!this._subgroups) { return []; }
        return this._subgroups;
    }
    Sector.prototype.subSectors = function() {
        return this.subGroups();
    }
    Sector.prototype.getColumns = function() {
        if(!this._columns) { return []; }
        function displayOrderSort(a,b) { return (a.display_order > b.display_order) ? 1 : -1 }
        return this._columns.sort(displayOrderSort);
    }
    Sector.prototype.getIndicators = function() {
        return this._columns || [];
    }
    Sector.prototype.isDefault = function() {
        return !!this._default;
    }
    Sector.prototype.getSubsector = function(query) {
        if(!query) { return; }
        var ssSlug = query.slug || query;
        var ssI = 0, ss = this.subSectors(), ssL = ss.length;
        for(;ssI < ssL; ssI++) {
            if(ss[ssI].slug === ssSlug) {
                return new SubSector(this, ss[ssI]);
            }
        }
    }
    Sector.prototype.getIndicator = function(query) {
        if(!query) { return; }
        var islug = query.slug || query;
        var ssI = 0, ss = this.getIndicators(), ssL = ss.length;
        for(;ssI < ssL; ssI++) {
            if(ss[ssI].slug === islug) {
                return new Indicator(this, ss[ssI]);
            }
        }
    }
    //
    // The Indicator ans SubSector objects might be unnecessary.
    // We can see if the provide any benefit at some point down the line.
    //
    function SubSector(sector, opts) {
        this.sector = sector;
        _.extend(this, opts);
    }
    function Indicator(sector, opts) {
        this.sector = sector;
        _.extend(this, opts);
    }
    function init(_sectors, opts) {
        if(!!opts && !!opts['default']) {
            defaultSector = new Sector(_.extend(opts['default'], {'default': true}));
        }
        sectors = _(_sectors).chain()
                        .clone()
                        .map(function(s){return new Sector(_.extend({}, s));})
                        .value();
        return true;
    }
    function clear() {
        sectors = [];
    }
    function pluck(slug) {
        return _(sectors).chain()
                .filter(function(s){return s.slug == slug;})
                .first()
                .value() || defaultSector;
    }
    function all() {
        return sectors;
    }
    function validate() {
        if(!sectors instanceof Array)
            warn("Sectors must be defined as an array");
        if(sectors.length===0)
            warn("Sectors array is empty");
        _.each(sectors, function(sector){
            if(sector.name === undefined) { warn("Sector name must be defined."); }
            if(sector.slug === undefined) { warn("Sector slug must be defined."); }
        });
        var slugs = _(sectors).pluck('slug');
        if(slugs.length !== _(slugs).uniq().length) {
            warn("Sector slugs must not be reused");
        }
        // $(this.columns).each(function(i, val){
        //   var name = val.name;
        //   var slug = val.slug;
        //   name === undefined && warn("Each column needs a slug", this);
        //   slug === undefined && warn("Each column needs a name", this);
        // });
        return true;
    }
    function slugs() {
        return _.pluck(sectors, 'slug');
    }
    return {
        init: init,
        pluck: pluck,
        slugs: slugs,
        all: all,
        validate: validate,
        clear: clear
    };
})();

var Tabulation = (function(){
    function init () {
        return true;
    }
    function filterBySector (sector) {
        var sector = Sectors.pluck(sector);
        return _.filter(NMIS.data(), function(d){
            return d.sector == sector;
        })
    }
    function sectorSlug (sector, slug, keys) {
        var occurrences = {};
        var values = _(filterBySector(sector)).chain()
                        .pluck(slug)
                        .map(function(v){
                            return '' + v;
                        })
                        .value();
        if(keys===undefined) keys = _.uniq(values).sort();
        _.each(keys, function(key) { occurrences[key] = 0; });
        _.each(values, function(d){
            if(occurrences[d] !== undefined)
                occurrences[d]++;
        });
        return occurrences;
    }
    function sectorSlugAsArray (sector, slug, keys) {
        var occurrences = sectorSlug.apply(this, arguments);
        if(keys===undefined) { keys = _.keys(occurrences).sort(); }
        return _(keys).map(function(key){
            return {
                occurrences: '' + key,
                value: occurrences[key]
            };
        });
    }
    return {
        init: init,
        sectorSlug: sectorSlug,
        sectorSlugAsArray: sectorSlugAsArray,
    };
})();


var DataLoader = (function(){
    function fetch(url){
        return $.getJSON(url);
    }
    return {
        fetch: fetch
    };
})();


var DisplayWindow = (function(){
    var elem, elem1, elem0, elem1content;
    var fullHeight;
    var opts;
    var visible;
    var hbuttons;
    var titleElems = {};
    var curSize;
    function init(_elem, _opts) {
        if(opts !== undefined) { clear(); }
        elem = $(_elem);
        opts = _.extend({
            //default options:
            height: 100,
            clickSizes: [
                ['full', 'Table Only'],
                ['middle', 'Split'],
                ['minimized', 'Map Only']
            ],
            size: 'full',
            sizeCookie: false,
            callbacks: {},
            visible: false,
            heights: {
                full: Infinity,
                middle: 280,
                minimized: 46
            },
            allowHide: true,
            fullResizer: true,
            padding: 45
        }, _opts);
        elem0 = $('<div />')
            .appendTo(elem);
        elem1 = $('<div />')
            .appendTo(elem);
        visible = !!opts.visible;
        setVisibility(visible, false);
        if(opts.sizeCookie) {
            opts.size = $.cookie("displayWindowSize") || opts.size;
        }

        if(opts.fullResizer) {
            var oh = 0;
            $(opts.offsetElems).each(function(){ oh += $(this).height(); });
            fullHeight = $(window).height() - oh - opts.padding;
            elem.height(fullHeight);
            elem.addClass('display-window-wrap');
            elem0.height(fullHeight);
            elem1.addClass('display-window-content');
        }
        createHeaderBar()
            .appendTo(elem1);
        elem1content = $('<div />')
            .appendTo(elem1);
        setSize(opts.size);
    }
    function setTitle(t, tt) {
        _.each(titleElems, function(e){
            e.text(t);
        });
        if(tt!== undefined) {
            $('head title').text('NMIS: '+ tt);
        } else {
            $('head title').text('NMIS: '+ t);
        }
    }
    var curTitle;
    function showTitle(i) {
        curTitle = i;
        _.each(titleElems, function(e, key){
            if(key===i) {
                e.show();
            } else {
                e.hide();
            }
        });
    }
    function addCallback(cbname, cb) {
        if(opts.callbacks[cbname]===undefined) {
            opts.callbacks[cbname] = [];
        }
        opts.callbacks[cbname].push(cb);
    }
    function setBarHeight(h, animate, cb) {
        if(animate) {
            elem1.animate({
                height: h
            }, {
                duration: 200,
                complete: cb
            });
        } else {
            elem1.css({
                height: h
            });
            (cb || function(){})();
        }
    }
    var prevSize, sizeTempSet = false;
    function setTempSize(size, animate) {
        prevSize = curSize;
        sizeTempSet = true;
        setSize(size, animate);
    }
    function unsetTempSize(animate) {
        if(sizeTempSet) {
            setSize(prevSize, animate);
            prevSize = undefined;
            sizeTempSet = false;
        }
    }
    function setSize(_size, animate) {
        var size;
        if(opts.heights[_size] !== undefined) {
            size = opts.heights[_size];
            if(size === Infinity) {
                size = fullHeight;
            }
            $.cookie("displayWindowSize", _size);
            setBarHeight(size, animate, function(){
                if(!!curSize) elem1.removeClass('size-'+curSize);
                elem1.addClass('size-'+_size);
            });
            curSize = _size;
        }
        if(opts.callbacks[_size] !== undefined) {
            _.each(opts.callbacks[_size], function(cb){
                cb(animate);
            });
        }
        if(opts.callbacks.resize !== undefined) {
            _.each(opts.callbacks.resize, function(cb){
                cb(animate, _size, elem, elem1, elem1content);
            });
        }
        hbuttons.find('.primary')
            .removeClass('primary');
        hbuttons.find('.clicksize.'+_size)
            .addClass('primary');
    }
    function setVisibility(tf) {
        var css = {};
        if(!tf) {
            css = {'left': '1000em'};
        } else {
            css = {'left': '0'};
        }
        elem0.css(css);
        elem1.css(css);
    }
    function addTitle(key, jqElem) {
        titleElems[key] = jqElem;
        if(curTitle===key) {
            showTitle(key);
        }
    }
    function createHeaderBar() {
        hbuttons = $('<span />'); //.addClass('print-hide-inline');
        _.each(opts.clickSizes, function(sizeArr){
            var size = sizeArr[0],
                desc = sizeArr[1];
            $('<a />')
                .attr('class', 'btn small clicksize ' + size)
                .text(desc)
                .attr('title', desc)
                .click(function(){
                    setSize(size, true)
                })
                .appendTo(hbuttons);
        });
        titleElems.bar = $('<h3 />').addClass('bar-title').hide();
        return $('<div />', {'class': 'display-window-bar breadcrumb'})
            .css({'margin':0})
            .append(titleElems.bar)
            .append(hbuttons);
    }
    function clear(){
        elem !== undefined && elem.empty();
        titleElems = {};
    }
    function getElems() {
        return {
            wrap: elem,
            elem0: elem0,
            elem1: elem1,
            elem1content: elem1content
        }
    }
    function elem1contentHeight() {
        var padding = 30;
        return elem1.height() - hbuttons.height() - padding;
    }
    return {
        init: init,
        clear: clear,
        setSize: setSize,
        setTempSize: setTempSize,
        setVisibility: setVisibility,
        unsetTempSize: unsetTempSize,
        addCallback: addCallback,
        addTitle: addTitle,
        setTitle: setTitle,
        showTitle: showTitle,
        elem1contentHeight: elem1contentHeight,
        getElems: getElems
    };
})();

var IconSwitcher = (function(){
    var context = {};
    var callbacks = ["createMapItem",
                        "shiftMapItemStatus",
                        "statusShiftDone",
                        "hideMapItem",
                        "showMapItem",
                        "setMapItemVisibility"];
    function init(_opts) {
        //log("IconSwitcher initting");
        var noop = function(){};
        var items = {};
        context = _.extend({
            items: {},
            mapItem: mapItem
        }, _opts);
        _.each(callbacks, function(cbname){
            if(context[cbname]===undefined) { context[cbname] = noop; }
        });
    }
    var mapItems = {};
    function mapItem(id, value) {
        if(arguments.length===1) {
            //get mapItem
            return mapItems[id];
        } else if(arguments.length===2) {
            //set mapItem
            mapItems[id] = value;
        }
    }
    function hideItem(item) {
        item.hidden = true;
    }
    function showItem(item) {
        item.hidden = false;
    }
    function setVisibility(item, tf) {
        if(!!tf) {
            if(!item.hidden) {
                item.hidden = true;
                context.setMapItemVisibility.call(item, false, item, context.items);
                return true;
            }
        } else {
            if(!!item.hidden) {
                item.hidden = false;
                context.setMapItemVisibility.call(item, true, item, context.items);
                return true;
            }
        }
        return false;
    }
    function iterate(cb) {
        _.each(context.items, function(item, id, itemset){
            cb.apply(context, [item, id, itemset]);
        });
    }
    function shiftStatus(fn) {
        iterate(function(item, id){
            var status = fn.call(context, id, item, context.items);
            var visChange = setVisibility(item, status === false),
                statusChange = false;
            if(status === undefined) {
                //do nothing
            } else if(status === false) {
                item.status = undefined;
            } else if(item.status !== status) {
                item._prevStatus = status;
                item.status = status;
                statusChange = true;
            }
            if(statusChange || visChange) {
                context.shiftMapItemStatus(item, id);
            }
        });
        context.statusShiftDone();
    }
    function all() { return _.values(context.items); }
    function setCallback(cbName, cb) {
        if(callbacks.indexOf(cbName) !== -1) {
            context[cbName] = cb;
        }
    }
    function filterStatus(status) {
        return _.filter(context.items, function(item){ return item.status === status; });
    }
    function filterStatusNot(status) {
        return _.filter(context.items, function(item){ return item.status !== status; });
    }
    function allShowing() {
        return filterStatusNot(undefined);
    }
    function createAll() {
        iterate(context.createMapItem);
    }
    function clear() {
        context = {};
    }
    return {
        init: init,
        clear: clear,
        allShowing: allShowing,
        createAll: createAll,
        filterStatus: filterStatus,
        filterStatusNot: filterStatusNot,
        all: all,
        setCallback: setCallback,
        shiftStatus: shiftStatus,
        iterate: iterate
    }
})();

var LocalNav = (function(){
    var elem, wrap, opts;
    var buttonSections = {};
    var submenu;
    function init(selector, _opts) {
        wrap = $(selector);
        opts = _.extend({
            sections: []
        }, _opts);
        elem = $('<ul />', {'id': 'local-nav', 'class': 'nav'});
        wrap = $('<div />', {'class': 'row'})
                .css({'position':'absolute','top':82,'left':0,'z-index':99})
                .html(elem);
        $('.content').eq(0).prepend(wrap);
        _.each(opts.sections, function(section, i){
            if(i!==0) {
                $("<li />", {'class': 'small spacer'})
                    .html('&nbsp;')
                    .appendTo(elem);
            }
            _.each(section, function(arr){
                var code = arr[0].split(":");
                if(buttonSections[code[0]]===undefined) {buttonSections[code[0]] = {};}
                var a = $('<a />', {'href':arr[2], 'text': arr[1]});
                buttonSections[code[0]][code[1]] = a;
                $('<li />').html(a)
                    .appendTo(elem);
            });
        });
        submenu = $('<ul />')
            .addClass('submenu')
            .appendTo(elem);
    }
    function getNavLink(code) {
        var _x = code.split(":"),
            section = _x[0],
            name = _x[1];
        return buttonSections[section][name];
    }
    function markActive(codesArray) {
        wrap.find('.active').removeClass('active');
        _.each(codesArray, function(code){
            getNavLink(code).parents('li').eq(0).addClass('active')
        });
    }
    function clear() {
        wrap.empty();
        wrap = undefined;
        elem = undefined;
        buttonSections = {};
        submenu = undefined;
    }
    function hideSubmenu() {
        submenu.hide();
    }
    function displaySubmenu(nlcode, a, _opts) {
        var navLink = getNavLink(nlcode);
        var lpos = navLink.parents('li').eq(0).position().left;
        submenu.hide()
                .empty()
                .css({'left': lpos});
        _.each(a, function(aa){
            $('<li />')
                .html($('<a />', {text: aa[0], 'href': aa[1]}))
                .appendTo(submenu);
        });
        submenu.show();
    }
    function iterate(cb) {
        _.each(buttonSections, function(buttons, sectionName){
            _.each(buttons, function(button, buttonName){
                cb.apply(this, [sectionName, buttonName, button])
            });
        });
    }
    return {
        init: init,
        clear: clear,
        iterate: iterate,
        displaySubmenu: displaySubmenu,
        hideSubmenu: hideSubmenu,
        markActive: markActive
    }
})();

    function init(_data, _opts) {
        opts = _.extend({
            iconSwitcher: true,
            sectors: false
        }, _opts);
        data = {};
        if(!!opts.sectors) {
            loadSectors(opts.sectors);
        }
        loadFacilities(_data);
    	if(opts.iconSwitcher) {
            NMIS.IconSwitcher.init({
        	    items: data,
        	    statusShiftDone: function(){
        	        var tally = {};
    	            _.each(this.items, function(item){
    	                if(!tally[item.status]) {
    	                    tally[item.status]=0;
    	                }
    	                tally[item.status]++;
    	            });
//    	            log(JSON.stringify(tally));
        	    }
        	});
        }
        return true;
    }
    function loadSectors(_sectors, opts){
        Sectors.init(_sectors, opts);
    }
    function loadFacilities(_data, opts) {
        _.each(_data, function(val, key){
            data[key] = cloneParse(val);
        });
    }
    function clear() {
        data = [];
        Sectors.clear();
    }
    function ensureUniqueId(datum) {
        if(datum._uid === undefined) {
            datum._uid = _.uniqueId('fp');
        }
    }
    function ensureLatLng(datum) {
        if(datum._latlng === undefined && datum.gps !== undefined) {
            var llArr = datum.gps.split(' ');
            datum._latlng = [ llArr[0], llArr[1] ];
        }
    }
    function validateData() {
        Sectors.validate();
        _(data).each(ensureUniqueId);
        _(data).each(ensureLatLng);
        return true;
    }
    var _s;
    function activeSector(s) {
        if(s===undefined) {
            return _s;
        } else {
            _s = s;
        }
    }
    function cloneParse(d) {
        var datum = _.clone(d);
    	if(datum.gps===undefined) {
    	    datum._ll = false;
    	} else {
    	    var ll = datum.gps.split(' ');
    	    datum._ll = [ll[0], ll[1]];
    	}
    	var sslug = datum.sector.toLowerCase();
    	datum.sector = Sectors.pluck(sslug);
    	return datum;
    }
    function dataForSector(sectorSlug) {
        var sector = Sectors.pluck(sectorSlug);
        return _(data).filter(function(datum, id){
            return datum.sector.slug === sector.slug;
        });
    }
    function dataObjForSector(sectorSlug) {
        var sector = Sectors.pluck(sectorSlug);
        var o = {};
        _(data).each(function(datum, id){
            if(datum.sector.slug === sector.slug) {
                o[id] = datum;
            }
        });
        return o;
    }
    return {
        Sectors: Sectors,
        Tabulation: Tabulation,
        IconSwitcher: IconSwitcher,
        LocalNav: LocalNav,
        Breadcrumb: Breadcrumb,
        DisplayWindow: DisplayWindow,
        DataLoader: DataLoader,
        FacilityPopup: FacilityPopup,
        FacilityHover: FacilityHover,
        FacilitySelector: FacilitySelector,
        HackCaps: HackCaps,
        MapMgr: MapMgr,
        Env: Env,
        S3Photos: S3Photos,
        activeSector: activeSector,
        data: function(){return data;},
        dataForSector: dataForSector,
        dataObjForSector: dataObjForSector,
        validateData: validateData,
        loadSectors: loadSectors,
        loadFacilities: loadFacilities,
        init: init,
        clear: clear
    }
})();
