		<csscriptdict>
<script><!--
CSStopExecution = false;
CSInit = new Array;




(function() {
  // すでにスマートフォン用サイトへのリダイレクトが完了しているか、
  // ユーザーが「いいえ」を選択した場合は、何もしない
  if (sessionStorage && sessionStorage.getItem("sp_flag")) {
    return;
  }

  // ユーザーエージェントではなく、画面幅でモバイルかどうかを判定する
  // 一般的なスマートフォンの画面幅を基準とする（768px以下をモバイルとみなす）
  const isMobile = window.matchMedia('(max-width: 768px)').matches;

  // スマートフォンと判定され、かつリダイレクトを促すポップアップをまだ見ていない場合
  if (isMobile) {
    if (confirm('スマートフォン用サイトを表示しますか？')) {
      // ユーザーが「はい」を選択した場合、モバイルサイトへリダイレクト
      window.location.href = 'https://be-intl.com/m/volunteers.htm';
    } else {
      // ユーザーが「いいえ」を選択した場合、セッションストレージにフラグを保存し、
      // 次回以降同じセッションではポップアップを表示しない
      sessionStorage.setItem("sp_flag", true);
    }
  }
})();





function CSScriptInit() {
if(typeof(skipPage) != "undefined") { if(skipPage) return; }
idxArray = new Array;
for(var i=0;i<CSInit.length;i++)
	idxArray[i] = i;
CSAction2(CSInit, idxArray);
}
CSAg = window.navigator.userAgent; CSBVers = parseInt(CSAg.charAt(CSAg.indexOf("/")+1),10);
function IsIE() { return CSAg.indexOf("MSIE") > 0;}
function CSIEStyl(s) { return document.all.tags("div")[s].style; }
function CSNSStyl(s) { return CSFindElement(s,0); }
function CSFindElement(n,ly) { if (CSBVers < 4) return document[n];
	var curDoc = ly ? ly.document : document; var elem = curDoc[n];
	if (!elem) { for (var i=0;i<curDoc.layers.length;i++) {
		elem = CSFindElement(n,curDoc.layers[i]); if (elem) return elem; }}
	return elem;
}
function CSClickReturn () {
	var bAgent = window.navigator.userAgent; 
	var bAppName = window.navigator.appName;
	if ((bAppName.indexOf("Explorer") >= 0) && (bAgent.indexOf("Mozilla/3") >= 0) && (bAgent.indexOf("Mac") >= 0))
		return true; // dont follow link
	else return false; // dont follow link
}
function CSButtonReturn () {
	var bAgent = window.navigator.userAgent; 
	var bAppName = window.navigator.appName;
	if ((bAppName.indexOf("Explorer") >= 0) && (bAgent.indexOf("Mozilla/3") >= 0) && (bAgent.indexOf("Mac") >= 0))
		return false; // follow link
	else return true; // follow link
}
CSIm = new Object();
function CSIShow(n,i) {
	if (document.images) {
		if (CSIm[n]) {
			var img = (!IsIE()) ? CSFindElement(n,0) : document[n];
			if (img && typeof(CSIm[n][i].src) != "undefined") {img.src = CSIm[n][i].src;}
			if(i != 0)
				self.status = CSIm[n][3];
			else
				self.status = " ";
			return true;
		}
	}
	return false;
}
function CSILoad(action) {
	im = action[1];
	if (document.images) {
		CSIm[im] = new Object();
		for (var i=2;i<5;i++) {
			if (action[i] != '') { CSIm[im][i-2] = new Image(); CSIm[im][i-2].src = action[i]; }
			else CSIm[im][i-2] = 0;
		}
		CSIm[im][3] = action[5];
	}
}
CSStopExecution = false;

function CSAction(array) { 
	return CSAction2(CSAct, array);
}
function CSAction2(fct, array) { 
	var result;
	for (var i=0;i<array.length;i++) {
		if(CSStopExecution) return false; 
		var actArray = fct[array[i]];
		if(actArray == null) return false; 
		var tempArray = new Array;
		for(var j=1;j<actArray.length;j++) {
			if((actArray[j] != null) && (typeof(actArray[j]) == "object") && (actArray[j].length == 2)) {
				if(actArray[j][0] == "VAR") {
					tempArray[j] = CSStateArray[actArray[j][1]];
				}
				else {
					if(actArray[j][0] == "ACT") {
						tempArray[j] = CSAction(new Array(new String(actArray[j][1])));
					}
				else
					tempArray[j] = actArray[j];
				}
			}
			else
				tempArray[j] = actArray[j];
		}			
		result = actArray[0](tempArray);
	}
	return result;
}
CSAct = new Object;

// --></script>
		</csscriptdict>
		<csactiondict>
			<script><!--
/**
 * Modern, cleaned-up version of the script.
 *
 * This script handles two main functionalities:
 * 1. A mobile redirection prompt.
 * 2. Preloading and swapping images for rollover effects on buttons.
 *
 * The original script contained a lot of boilerplate and compatibility code
 * for very old browsers (Netscape 4, IE 4), which has been removed.
 * The logic has been preserved while updating the syntax to modern standards.
 */

// 1. Mobile Redirection
(() => {
  // If the user previously chose not to redirect, do nothing.
  if (sessionStorage.getItem("sp_flag")) {
    return;
  }

  // Use matchMedia for modern responsive detection.
  const isMobile = window.matchMedia('(max-width: 768px)').matches;

  if (isMobile) {
    if (confirm('スマートフォン用サイトを表示しますか？')) {
      // Redirect to mobile site.
      window.location.href = 'https://be-intl.com/m/volunteers.htm';
    } else {
      // Remember the user's choice for this session.
      sessionStorage.setItem("sp_flag", true);
    }
  }
})();


// 2. Image Rollover Functionality

// CSIm will store the preloaded image objects.
const CSIm = {};
// CSInit will be populated with the image data arrays.
const CSInit = [];
// Preserved for compatibility, though likely unused.
const CSAct = {}; 

/**
 * Preloads images defined in an action array.
 * @param {Array} action - e.g., [CSILoad, 'buttonName', 'out.jpg', 'over.jpg', '', 'status text']
 */
function CSILoad(action) {
  // action[0] is the function itself (CSILoad), so we start from index 1.
  const imageName = action[1];
  const srcOut = action[2];
  const srcOver = action[3];
  const statusText = action[5];

  if (document.images) {
    CSIm[imageName] = {
      out: new Image(),
      over: new Image(),
      status: statusText
    };
    CSIm[imageName].out.src = srcOut;
    CSIm[imageName].over.src = srcOver;
  }
}

/**
 * Swaps an image's source. This is intended to be called from HTML event attributes
 * like onmouseover="CSIShow('buttonName', 1)" and onmouseout="CSIShow('buttonName', 0)".
 * @param {string} imageName - The name of the image element.
 * @param {number} state - 0 for the 'out' state, 1 for the 'over' state.
 */
function CSIShow(imageName, state) {
  if (document.images && CSIm[imageName]) {
    // The old syntax `document[imageName]` finds an element with a `name` or `id` of `imageName`.
    // This is deprecated but is the most likely way the old HTML is structured. We keep it for compatibility.
    const imgElement = document[imageName];

    if (imgElement) {
      const imageToShow = (state === 0) ? CSIm[imageName].out : CSIm[imageName].over;
      if (imageToShow && imageToShow.src) {
        imgElement.src = imageToShow.src;
      }
    }

    // Update the browser status bar text, as in the original script.
    self.status = (state !== 0) ? CSIm[imageName].status : " ";
    return true;
  }
  return false;
}

// Generic action executor, modernized from the original.
function CSAction2(actionSet, indexArray) {
  let result;
  for (const index of indexArray) {
    const action = actionSet[index];
    if (!action) continue;

    const func = action[0];
    if (typeof func === 'function') {
      // The original passed a modified array. Passing the whole `action` array
      // works because the target function `CSILoad` accesses arguments from index 1 onwards.
      result = func(action);
    }
  }
  return result;
}

/**
 * Kept for backwards compatibility in case the HTML calls it.
 */
function CSAction(array) {
  return CSAction2(CSAct, array);
}

/**
 * Initializes the image preloading by executing the functions in the CSInit array.
 * This should be called when the page loads, e.g., <body onload="CSScriptInit()">.
 */
function CSScriptInit() {
  // Create an array of indices [0, 1, 2, ...] for CSInit.
  const indices = CSInit.map((_, i) => i);
  CSAction2(CSInit, indices);
}


// --- Data for Image Rollovers ---
// The HTML page populates this array with image data.
// The format is [function, name, out_src, over_src, unused, status_text]
CSInit.push(new Array(CSILoad, 'button2', 'images/top_0001d.jpg', 'images/top_0002d.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button4', 'images/top_0001b.jpg', 'images/top_0002b.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button3', 'images/top_0001c.jpg', 'images/top_0002c.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button5', 'images/top_0006b.jpg', 'images/top_0007b.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button6', 'images/top_0006c.jpg', 'images/top_0007c.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button7', 'images/top_0006d.jpg', 'images/top_0007d.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button8', 'images/top_0006e.jpg', 'images/top_0007e.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button9', 'images/top_0006f.jpg', 'images/top_0007f.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button10', 'images/top_0006g.jpg', 'images/top_0007g.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button', 'images/menu_001a.jpg', 'images/menu_002a.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button11', 'images/menu_001b.jpg', 'images/menu_002b.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button12', 'images/menu_001c.jpg', 'images/menu_002c.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button13', 'images/menu_001d.jpg', 'images/menu_002d.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button14', 'images/menu_001e.jpg', 'images/menu_002e.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button15', 'images/menu_001f.jpg', 'images/menu_002f.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button16', 'images/menu_001g.jpg', 'images/menu_002g.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button17', 'images/menu_001h.jpg', 'images/menu_002h.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button18', 'images/menu_001i.jpg', 'images/menu_002i.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button19', 'images/menu_001j.jpg', 'images/menu_002j.jpg', '', ''));
CSInit.push(new Array(CSILoad, 'button20', 'images/top_0009b.gif', 'images/top_0009a.gif', '', ''));

CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button4',/*URL*/'images/top_0001b.jpg',/*URL*/'images/top_0002b.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button3',/*URL*/'images/top_0001c.jpg',/*URL*/'images/top_0002c.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button5',/*URL*/'images/top_0006b.jpg',/*URL*/'images/top_0007b.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button6',/*URL*/'images/top_0006c.jpg',/*URL*/'images/top_0007c.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button7',/*URL*/'images/top_0006d.jpg',/*URL*/'images/top_0007d.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button8',/*URL*/'images/top_0006e.jpg',/*URL*/'images/top_0007e.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button9',/*URL*/'images/top_0006f.jpg',/*URL*/'images/top_0007f.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button10',/*URL*/'images/top_0006g.jpg',/*URL*/'images/top_0007g.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button',/*URL*/'images/menu_001a.jpg',/*URL*/'images/menu_002a.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button11',/*URL*/'images/menu_001b.jpg',/*URL*/'images/menu_002b.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button12',/*URL*/'images/menu_001c.jpg',/*URL*/'images/menu_002c.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button13',/*URL*/'images/menu_001d.jpg',/*URL*/'images/menu_002d.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button14',/*URL*/'images/menu_001e.jpg',/*URL*/'images/menu_002e.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button15',/*URL*/'images/menu_001f.jpg',/*URL*/'images/menu_002f.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button16',/*URL*/'images/menu_001g.jpg',/*URL*/'images/menu_002g.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button17',/*URL*/'images/menu_001h.jpg',/*URL*/'images/menu_002h.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button18',/*URL*/'images/menu_001i.jpg',/*URL*/'images/menu_002i.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button19',/*URL*/'images/menu_001j.jpg',/*URL*/'images/menu_002j.jpg',/*URL*/'','');
CSInit[CSInit.length] = new Array(CSILoad,/*CMP*/'button20',/*URL*/'images/top_0009b.gif',/*URL*/'images/top_0009a.gif',/*URL*/'','');

// --></script>
		</csactiondict>