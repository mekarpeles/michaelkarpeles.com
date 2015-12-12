var GedcomConst = {
	VERSION : "1.0.1",

	path : {
		RESSOURCE_PATH : "/static/misc/genealogy",
		GED_PATH : "/static/data/genealogy.ged"
	},

	id : {
		CANVAS_ID : "canvas",
		HISTORY_ID : "history",
		DETAIL_ID : "detail",
		CONTENT_ID : "content",
		LOG_ID : "log",
		QUICK_SELECT_ID : "quickSelect",
		CLOSE_DETAIL_ID : "closeDetail",
		DOWNLOAD_ID : "download"
	},

	QUERY_PARAM : "root",

	LANGUAGE : "en",

	SHOW_DOWNLOAD : false,
	SHOW_LOG : false,
	SHOW_PRIVATE_RECORD : false,

	SHOW_GEOLOC : true,

	indicator : {
		personne : "INDI",
		famille : "FAM",
		source : "SOUR",
		note : "NOTE",
		newLine : "CONT",
		append : "CONC"

	},

	logLevels : {
		DEBUG : 0,
		INFO : 1,
		WARN : 2,
		ERROR : 3
	},

	logLevel : 3

};
