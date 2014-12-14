(function($) {
  $.fn.extend({
    keybind: function(seq, handler) {
      var data = this.data('keybind');

      if (!data) {
        data = { bindings: {} };
        this.data('keybind', data)
            .bind({ keypress: keypressHandler,
                    keydown:  keydownHandler });
      }

      if (typeof seq === "object")
        $.each(seq, function(s, h) { attachBinding(data.bindings, seqChords(s), h); });
      else
        attachBinding(data.bindings, seqChords(seq), handler);

      return this;
    },

    keyunbind: function(seq, handler) {
      var data = this.data('keybind');

      if (handler !== undefined) {
        data.bindings[seq] = $.grep(data.bindings[seq], function(h) {
          return h !== handler;
        });
      } else
        delete data.bindings[seq];

      return this;
    },

    keyunbindAll: function() {
      $(this).removeData('keybind')
             .unbind({ keypress: keypressHandler,
                       keydown:  keydownHandler });
      return this;
    }
  });

  function keypressHandler(event) {
    var data = $(this).data('keybind'),
        desc = keyDescription(event);

    if (shouldTriggerOnKeydown(desc, event))
      return true;

    return triggerHandlers(data.bindings, desc, event);
  }

  function keydownHandler(event) {
    var data = $(this).data('keybind'),
        desc = keyDescription(event);

    if (!shouldTriggerOnKeydown(desc, event))
      return true;

    return triggerHandlers(data.bindings, desc, event);
  }

  function attachBinding(bindings, chords, handler) {
    var chord = chords.shift(),
        entry = bindings[chord];

    if (entry) {
      if (chords.length > 0 && entry.length !== undefined)
        throw "Keybinding would be shadowed by pre-existing keybinding";

      if (chords.length === 0 && entry.length === undefined)
        throw "Keybinding would shadow pre-existing keybinding";

    } else {
      if (chords.length > 0)
        bindings[chord] = entry = {};
      else
        bindings[chord] = entry = [];
    }

    if (chords.length === 0)
      entry.push(handler);
    else
      attachBinding(entry, chords, handler);
  }

  function triggerHandlers(bindings, desc, event) {
    var handlers = bindings[desc.name],
        retVal   = true;

    if (handlers === undefined)
      return retVal;

    $.each(handlers, function(i, fn) {
      if (fn(desc, event) === false)
        retVal = false;
    });

    return retVal;
  }

  function seqChords(seq) {
    return seq.split(/\s+/);
  }

  function shouldTriggerOnKeydown(desc, event) {
    if (desc.ctrl || desc.meta || desc.alt)
      return true;

    // % .. (, which look like arrow keys
    if ((desc.charCode >= 37 && desc.charCode <= 40) ||
        // same thing but on IE
        (event.type === 'keypress' && desc.keyCode >= 37 && desc.keyCode <= 40))
      return false;

    if (desc.keyCode === 189 || desc.keyCode === 187)
      return true;

    if (desc.charCode === 45 || desc.keyCode === 45) // -
      return true;

    if (desc.charCode === 95 || desc.keyCode === 95) // _
      return true;

    if (desc.charCode === 61 || desc.keyCode === 61
        || desc.charCode === 43 || desc.keyCode === 43) // =
      return true;

    if (desc.keyCode in _specialKeys)
      return true;

    return false;
  }

  function keyDescription(event) {
    var desc = {};

    if (event.ctrlKey)
      desc.ctrl = true;
    if (event.altKey)
      desc.alt = true;
    if (event.originalEvent.metaKey)
      desc.meta = true;
    if (event.shiftKey)
      desc.shift = true;

    desc.keyCode  = realKeyCode(desc, event);
    desc.charCode = event.charCode;
    desc.name = keyName(desc, event);

    return desc;
  }

  function realKeyCode(desc, event) {
    var keyCode = event.keyCode;
    if (keyCode in _funkyKeyCodes)
      keyCode = _funkyKeyCodes[keyCode];
    return keyCode;
  }

  function keyName(desc, event) {
    var name, mods = '';

    if (desc.ctrl) mods += 'C-';
    if (desc.alt)  mods += 'A-';
    if (desc.meta) mods += 'M-';

    if (event.type === 'keydown') {
      var keyCode = desc.keyCode;

      if (keyCode in _specialKeys)
        name = _specialKeys[keyCode];
      else
        name = String.fromCharCode(keyCode).toLowerCase();

      if (desc.shift && name in _shiftedKeys)
        name = _shiftedKeys[name];
      else if (desc.shift)
        mods += 'S-';

    } else if (event.type === 'keypress') {
      name = String.fromCharCode(desc.charCode || desc.keyCode);

    } else
      throw("could prolly support keyup but explicitly don't right now");

    return mods + name;
  }

  var _specialKeys = {
    8: 'Backspace', 9: 'Tab', 13: 'Enter', 27: 'Esc',
    32: 'Space', 33: 'PageUp', 34: 'PageDown', 35: 'End', 36: 'Home',
    37: 'Left', 38: 'Up', 39: 'Right', 40: 'Down', 45: 'Insert', 46: 'Del',
    112: 'F1', 113: 'F2', 114: 'F3', 115: 'F4', 116: 'F5', 117: 'F6',
    118: 'F7', 119: 'F8', 120: 'F9', 121: 'F10', 122: 'F11', 123: 'F12',
    187: '=', 189: '-'
  };

  // Gecko -> WebKit/IE
  var _funkyKeyCodes = {
    109: 189
  };

  var _shiftedKeys = {
    '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
    '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
    '=': '+', '-': '_'
  };

}(jQuery));
