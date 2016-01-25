/*jslint browser: true*/
/*global  $*/
/*global  paper*/
"use strict";

$(window).resize(function () {
	$('.height-anchored').css('top', $('.layout-background').height());
});

function forceResize() {
    setTimeout(function(){$(window).trigger('resize');}, 100);
}

$(document).ready(function () {

    /* force resizing once any dropdown/tab is clicked */
    $('.mdl-tabs__tab').click(forceResize);

    setTimeout(forceResize, 100);
});
