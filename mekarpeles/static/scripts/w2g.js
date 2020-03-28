(function () {
  $("cite").mousedown(function(e){
    if (e.which == 1) {
      if ($(this).attr("w2gid")) {
        localStorage.setItem('history', window.location.href);
        window.location = 'https://graph.global/?id=' + $(this).attr("w2gid");
      }
    }
  });
}());