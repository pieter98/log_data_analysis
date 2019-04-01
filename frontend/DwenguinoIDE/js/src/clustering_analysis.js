
var ClusteringAnalysis = {
    tsne_data: [],
    code_tree: 0,
    session_number: 1,
    loadSessionData: function(){
        console.log("loading tsne data");
        $.ajax({
            type: "GET",
            url: "http://localhost:20042/evaluate_clustering?session=" + ClusteringAnalysis.session_number,
            datatype: "json"},
        ).done(function(data){
            ClusteringAnalysis.tsne_data = JSON.parse(data);
            console.log(ClusteringAnalysis.tsne_data);
            ClusteringAnalysis.plotClusteringData();
        }).fail(function(response, status)  {
            console.warn('Failed to fetch sessionIdList:', status);
        });
    },
    plotClusteringData: function(){
      var myPlot = document.getElementById("db_clustering_plot");
      var xCoords = [];
      var yCoords = [];
      var cCoords = [];
      this.tsne_data.forEach(function(entry){
        //console.log(entry);
        xCoords.push(entry[0][0]);
        yCoords.push(entry[0][1]);
        var rgb = hsluv.hsluvToRgb([entry[1]*3, 100, 50]);
        cCoords.push(Colors.rgb2hex(Math.round(rgb[0] * 255), Math.round(rgb[1] * 255), Math.round(rgb[2] * 255)));
      });
      data = [{x:xCoords, y:yCoords, type:"scatter", mode:"markers", marker:{size:5, color: cCoords}}];
      layout = { hovermode:'closest', title:'Click on Points'};
      Plotly.newPlot('db_clustering_plot', data, layout);
      myPlot.on('plotly_click', function(eventdata){
        console.log(eventdata);
        var pointIndex = eventdata.points[0].pointIndex;
        console.log(pointIndex);
        ClusteringAnalysis.getCodeTreeForIndex(pointIndex);
      });

    },
    getCodeTreeForIndex: function(index){
      $.ajax({
          type: "GET",
          url: "http://localhost:20042/get_code_tree_for_index?session=" + ClusteringAnalysis.session_number + "&index=" + index,
          datatype: "json"},
      ).done(function(data){
          ClusteringAnalysis.code_tree = JSON.parse(data);
          console.log(ClusteringAnalysis.code_tree);
          ClusteringAnalysis.workspace.clear();
          var xml = Blockly.Xml.textToDom(ClusteringAnalysis.code_tree);
          Blockly.Xml.domToWorkspace(xml, ClusteringAnalysis.workspace);
      }).fail(function(response, status)  {
          console.warn('Failed to fetch sessionIdList:', status);
      });
    },
    onresize: function(){
        var blocklyArea = document.getElementById('db_blockly');
        var blocklyDiv = document.getElementById('blocklyDiv');
        // Compute the absolute coordinates and dimensions of blocklyArea.
        var element = blocklyArea;
        var x = 0;
        var y = 0;
        do {
            x += element.offsetLeft;
            y += element.offsetTop;
            element = element.offsetParent;
        } while (element);
        // Position blocklyDiv over blocklyArea.
        blocklyDiv.style.left = x + 'px';
        blocklyDiv.style.top = y + 'px';
        blocklyDiv.style.width = blocklyArea.offsetWidth + 'px';
        blocklyDiv.style.height = blocklyArea.offsetHeight + 'px';
    },

    injectBlockly: function(){
        var blocklyArea = document.getElementById('db_blockly');
        var blocklyDiv = document.getElementById('blocklyDiv');
        ClusteringAnalysis.workspace = Blockly.inject(blocklyDiv,
            {
                toolbox: document.getElementById('toolbox'),
                media: "DwenguinoIDE/img/",
                zoom: {controls: true, wheel: true}
            });
        window.addEventListener('resize', ClusteringAnalysis.onresize, false);
        ClusteringAnalysis.onresize();
        Blockly.svgResize(ClusteringAnalysis.workspace);
        ClusteringAnalysis.workspace.addChangeListener(ClusteringAnalysis.renderCode);
    },

    changeLanguage: function() {
        // Store the blocks for the duration of the reload.
        // This should be skipped for the index page, which has no blocks and does
        // not load Blockly.
        // Also store the recoring up till now.
        // MSIE 11 does not support sessionStorage on file:// URLs.
        if (typeof Blockly !== 'undefined' && window.sessionStorage) {
            var xml = Blockly.Xml.workspaceToDom(ClusteringAnalysis.workspace);
            var text = Blockly.Xml.domToText(xml);
            window.sessionStorage.loadOnceBlocks = text;
        }

        var languageMenu = document.getElementById('db_menu_item_language_selection');
        var newLang = encodeURIComponent(languageMenu.options[languageMenu.selectedIndex].value);
        var search = window.location.search;
        if (search.length <= 1) {
            search = '?lang=' + newLang;
        } else if (search.match(/[?&]lang=[^&]*/)) {
            search = search.replace(/([?&]lang=)[^&]*/, '$1' + newLang);
        } else {
            search = search.replace(/\?/, '?lang=' + newLang + '&');
        }

        window.location = window.location.protocol + '//' +
        window.location.host + window.location.pathname + search;
    },

    /**
     * User's language (e.g. "en").
     * @type {string}
     */
    LANG: DwenguinoBlocklyLanguageSettings.getLang(),

    isRtl: function(){
        return false;
    },

    /**
     * Initialize the page language.
     */
    initLanguage: function() {
      // Set the HTML's language and direction.
      var rtl = ClusteringAnalysis.isRtl();
      document.dir = rtl ? 'rtl' : 'ltr';
      document.head.parentElement.setAttribute('lang', ClusteringAnalysis.LANG);

      // Sort languages alphabetically.
      var languages = [];
      for (var lang in DwenguinoBlocklyLanguageSettings.LANGUAGE_NAME) {
        languages.push([DwenguinoBlocklyLanguageSettings.LANGUAGE_NAME[lang], lang]);
      }
      var comp = function(a, b) {
        // Sort based on first argument ('English', 'Русский', '简体字', etc).
        if (a[0] > b[0]) return 1;
        if (a[0] < b[0]) return -1;
        return 0;
      };
      languages.sort(comp);

  },

    doTranslation: function() {
        // Inject language strings.
        document.title += ' ' + MSG['title'];
        //document.getElementById('title').textContent = MSG['title'];
        //document.getElementById('tab_blocks').textContent = MSG['blocks'];

        //document.getElementById('linkButton').title = MSG['linkTooltip'];
        //document.getElementById('db_menu_item_run').title = MSG['runTooltip'];
        document.getElementById('db_menu_item_upload').title = MSG['loadBlocksFileTooltip'];
        document.getElementById('db_menu_item_download').title = MSG['saveBlocksFileTooltip'];
        document.getElementById('db_menu_item_simulator').title = MSG['toggleSimulator'];
        //document.getElementById('t

        var tutorials = []; /*['tutsIntroduction', 'tutsHelloDwenguino', 'tutsBlink', 'tutsHelloRobot',
        'tutsNameOnLcd', 'tutsBlinkLED', 'tutsLedOnButtonPress', 'tutsBitPatternOnLeds',
      'tutsAllButtons', 'tutsDriveForward', 'tutsRideInSquare', 'tutsRideToWall', 'tutsAvoidWall'];*/
      /*  for (var i = 0; i < tutorials.length ; i++){
            var element = document.getElementById(tutorials[i]);
            if (element){
                element.innerHTML = MSG[tutorials[i]];
            }
        }*/

        var categories = ['catLogic', 'catLoops', 'catMath', 'catText', 'catLists',
            'catColour', 'catVariables', 'catFunctions', 'catBoardIO', 'catDwenguino', 'catArduino'];
        for (var i = 0, cat; cat = categories[i]; i++) {
            var element = document.getElementById(cat);
            if (element) {
                element.setAttribute('name', MSG[cat]);
            }

        }
        var textVars = document.getElementsByClassName('textVar');
        for (var i = 0, textVar; textVar = textVars[i]; i++) {
            textVar.textContent = MSG['textVariable'];
        }
        var listVars = document.getElementsByClassName('listVar');
        for (var i = 0, listVar; listVar = listVars[i]; i++) {
            listVar.textContent = MSG['listVariable'];
        }
    },

    /**
     * Load blocks saved on App Engine Storage or in session/local storage.
     * @param {string} defaultXml Text representation of default blocks.
     */
    loadBlocks: function(defaultXml) {
      try {
        var loadOnce = window.sessionStorage.loadOnceBlocks;
      } catch(e) {
        // Firefox sometimes throws a SecurityError when accessing sessionStorage.
        // Restarting Firefox fixes this, so it looks like a bug.
        var loadOnce = null;
      }
      if ('BlocklyStorage' in window && window.location.hash.length > 1) {
        // An href with #key trigers an AJAX call to retrieve saved blocks.
        BlocklyStorage.retrieveXml(window.location.hash.substring(1));
      } else if (loadOnce) {
        // Language switching stores the blocks during the reload.
        delete window.sessionStorage.loadOnceBlocks;
        var xml = Blockly.Xml.textToDom(loadOnce);
        Blockly.Xml.domToWorkspace(xml, ClusteringAnalysis.workspace);
      } else if (defaultXml) {
        // Load the editor with default starting blocks.
        var xml = Blockly.Xml.textToDom(defaultXml);
        Blockly.Xml.domToWorkspace(xml, ClusteringAnalysis.workspace);
      } else if ('BlocklyStorage' in window) {
        // Restore saved blocks in a separate thread so that subsequent
        // initialization is not affected from a failed load.
        window.setTimeout(BlocklyStorage.restoreBlocks, 0);
      }
  },
}

$(document).ready(function(){
    ClusteringAnalysis.loadSessionData();
    ClusteringAnalysis.initLanguage();
    ClusteringAnalysis.injectBlockly();
    ClusteringAnalysis.loadBlocks('<xml id="startBlocks" style="display: none">' + document.getElementById('startBlocks').innerHTML + '</xml>');

})
