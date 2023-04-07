var projects;
$( document ).ready(function() {
  $.get('/static/data/projects.json')
    .done(function(data) {
      projects = data;
      console.log(projects);
    });

  $('#today h1').text(new Date().toJSON().slice(0,10));
});

