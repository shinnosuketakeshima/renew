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
