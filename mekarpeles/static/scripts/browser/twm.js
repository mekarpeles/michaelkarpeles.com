// minimal example of setting up an Isfahan tiling window environment
var wm = new Isfahan.WindowManager({
  container: '#canvas', // DOM element to which Workspace binds
  layout: {type: "row"}, // Initial window structure
  onEnter: function(window) {
    $('.layout-slot').removeClass('selected');
    window.$container.addClass('selected');

    // get workspace from outside closure
    // this.selectedWindow = window;
  },
  onExit: function(window) {
    $('.layout-slot').removeClass('selected');

    //window.neighbor().$container.add
    //window.$container.addClass('selected');
  },
  onUpdate: function(window) {}
});

(function keybindings() {
  var keys = {
    'h': 'l',
    'j': 'u',
    'k': 'd',
    'l': 'r'
  };
  Object.keys(keys).forEach(function(key) {
    Mousetrap.bindGlobal(['meta+' + key, 'alt+' + key], function(e) {
      workspace.split(workspace.selectedWindow, keys[key]);
    });
    Mousetrap.bindGlobal(['command+' + key, 'ctrl+' + key], function(e) {
      workspace.select(workspace.selectedWindow, keys[key]);
    });
  })

  Mousetrap.bindGlobal(['meta+r', 'alt+r'], function(e) {
    workspace.remove(workspace.selectedWindow);
  });

  Mousetrap.bindGlobal(['meta+x', 'alt+x'], function(e) {
    $('#omnibox').select();
  });
})();